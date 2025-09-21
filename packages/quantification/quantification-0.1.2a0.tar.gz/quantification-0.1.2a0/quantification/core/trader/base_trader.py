from tqdm import tqdm
from typing import TYPE_CHECKING
from datetime import date, timedelta, datetime

from dataclasses import dataclass

from .query import Query
from .report import (
    AssetData,
    OrderResultData,
    PeriodData,
    PointData,
    BenchmarkData,
    SingleStrategyReportV1,
    MultiStrategyReportV1
)
from .portfolio import Portfolio
from .collector import Collector
from .base_order import Result, BaseOrder
from .base_stage import BaseStage
from ..asset.cash import RMB
from ..data.field import Field

from ..env import EnvGetter, Env
from ..logger import logger

if TYPE_CHECKING:
    from ..data import BaseAPI
    from ..asset import BaseBroker, BaseAsset
    from ..strategy import BaseStrategy


@dataclass
class Rollup:
    strategy: "BaseStrategy"
    portfolio: Portfolio
    collector: Collector


class BaseTrader:
    def __init__(
            self,
            api: "BaseAPI",
            base: float,
            scale: float,
            start_date: date,
            end_date: date,
            padding: int,
            stage: type[BaseStage],
            brokers: list[type["BaseBroker"]],
            **kwargs
    ):
        self.api = api
        self.base = base
        self.scale = scale
        self.start_date = start_date
        self.end_date = end_date
        self.stage = stage
        self.query = Query(api, start_date - timedelta(days=padding), end_date)
        self.env: Env = Env(date=self.start_date, time=next(iter(self.stage)).time)

        self.brokers = [
            broker(api, start_date - timedelta(days=10), end_date + timedelta(days=10), stage, **kwargs)
            for broker in brokers
        ]

        EnvGetter.getter = lambda: self.env

    def match_broker(self, asset: "type[BaseAsset]") -> "BaseBroker|None":
        for candidate_broker in self.brokers:
            if candidate_broker.matchable(asset):
                return candidate_broker

        return None

    def liquidate(self, asset: "BaseAsset", day: date, stage: "BaseStage") -> int:
        if isinstance(asset, RMB):
            return asset.amount

        if (broker := self.match_broker(asset.__class__)) is None:
            return -1

        return broker.liquidate_asset(asset, day, stage)

    @property
    def timeline(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            for current_stage in self.stage:
                self.env = Env(date=current_date, time=current_stage.time)
                self.timeline_hook(current_date, current_stage)
                yield current_date, current_stage
            current_date += timedelta(days=1)

    def run_roll(self, roll: Rollup, day: date, stage: BaseStage):
        try:
            self.env.strategy = roll.strategy

            params = {
                "day": day,
                "stage": stage,
                "portfolio": roll.portfolio,
                "context": roll.strategy.context,
                "query": self.query,
                "trader": self,
                "strategy": roll.strategy
            }

            hooks = roll.strategy.triggered(**params)
            logger.trace(f"触发的全部hooks:{hooks}")

            if not hooks:
                return

            logger.info(f"运行策略: {roll.strategy}")

            for hook in hooks:
                logger.trace(f"开始运行{hook}")
                gen = hook(**params)
                order: BaseOrder | None = None
                result: Result | None = None

                while True:
                    try:
                        order = gen.send(result) if order else next(gen)
                        logger.trace(f"{hook}发出Order:{order}, 开始匹配Broker")

                        assert isinstance(order, BaseOrder), f"只能yield Order, 实际为{type(order)}"

                        broker = self.match_broker(order.asset)

                        if not broker:
                            logger.warning(f"{order}没有对应broker, 忽略该order")
                            result = None
                            continue

                        logger.trace(f"{broker}开始处理:{order}")

                        if result := broker.execute_order(order, roll.portfolio):
                            logger.trace(f"{broker}处理完成:{result}")
                            roll.portfolio += result.brought
                            roll.portfolio -= result.sold
                            roll.collector.collect(result, roll.portfolio)
                            logger.trace(f"资产增加{result.brought}, 减少{result.sold}")
                        else:
                            logger.trace(f"{broker}跳过指令:{order}")

                    except StopIteration:
                        logger.trace(f"运行结束{hook}")
                        break
        finally:
            self.env.strategy = None

    def gen_strategy_report(self, roll: Rollup, log: bool):
        strategy_data = []
        for shard in tqdm(roll.collector.shards, f"生成报告:{roll.strategy}"):
            portfolios_data: list[AssetData] = []
            total_liquidating_value = 0
            for asset in shard.portfolio:
                liquidating_value = self.liquidate(asset, shard.day, shard.stage)
                total_liquidating_value += liquidating_value
                portfolios_data.append(AssetData.from_asset(asset, liquidating_value=liquidating_value))

            datetime_str = datetime.combine(shard.day, shard.stage.time).isoformat()
            strategy_data.append(PeriodData(
                datetime=datetime_str,
                liquidating_value=total_liquidating_value,
                logs=logger.records.get(f"{roll.strategy.name}-{datetime_str}", []) if log else [],
                portfolios=portfolios_data,
                transactions=[OrderResultData.from_result(result) for result in shard.results]
            ))

        return strategy_data

    def gen_benchmark_report(self, benchmark: str):
        benchmark_points = [
            PointData(
                datetime=index.to_pydatetime().isoformat(),
                value=row[Field.IN_收盘点位]
            ) for index, row in self.api.query(
                start_date=self.start_date,
                end_date=self.end_date,
                fields=[Field.IN_收盘点位],
                index=benchmark,
            ).iterrows()
        ]

        return BenchmarkData(
            name=benchmark,
            init_value=benchmark_points[0].value,
            points=benchmark_points
        )

    def timeline_hook(self, current_date: date, current_stage: BaseStage):
        pass


class SingleTrader[T:BaseStrategy](BaseTrader):
    def __init__(
            self,
            api: "BaseAPI",
            base: float,
            scale: float,
            init_portfolio: Portfolio,
            start_date: date,
            end_date: date,
            padding: int,
            stage: type[BaseStage],
            brokers: list[type["BaseBroker"]],
            strategy: T,
            **kwargs
    ):
        super().__init__(api, base, scale, start_date, end_date, padding, stage, brokers, **kwargs)

        self.roll = Rollup(strategy=strategy, portfolio=init_portfolio, collector=Collector())

    def timeline_hook(self, current_date: date, current_stage: BaseStage):
        self.roll.collector.commence(current_date, current_stage, self.roll.portfolio)

    def run(self):
        for day, stage in self.timeline:
            logger.trace(f"==========日期:{day}===阶段:{stage}==========")
            self.run_roll(self.roll, day, stage)

    def report(self, title: str, description: str, benchmark: str, log: bool = True) -> SingleStrategyReportV1:
        return SingleStrategyReportV1(
            title=title,
            description=description,
            base=self.base,
            scale=self.scale,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            strategy=self.gen_strategy_report(self.roll, log),
            benchmark=self.gen_benchmark_report(benchmark)
        )


class MultiTrader(BaseTrader):
    def __init__(
            self,
            api: "BaseAPI",
            base: float,
            scale: float,
            init_portfolio: Portfolio,
            start_date: date,
            end_date: date,
            padding: int,
            stage: type[BaseStage],
            brokers: list[type["BaseBroker"]],
            strategies: list["BaseStrategy"],
            **kwargs
    ):
        super().__init__(api, base, scale, start_date, end_date, padding, stage, brokers, **kwargs)
        assert len(strategies) == len(set(map(str, strategies))), "请给Strategy设置不同名称"

        self.rolls = [
            Rollup(strategy=strategy, portfolio=init_portfolio.copy, collector=Collector())
            for strategy in strategies
        ]

    def timeline_hook(self, current_date: date, current_stage: BaseStage):
        for roll in self.rolls:
            roll.collector.commence(current_date, current_stage, roll.portfolio)

    def run(self):
        for day, stage in self.timeline:
            logger.trace(f"==========日期:{day}===阶段:{stage}==========")
            for roll in self.rolls:
                self.run_roll(roll, day, stage)

    def report(self, title: str, description: str, benchmark: str, log: bool = True) -> MultiStrategyReportV1:
        return MultiStrategyReportV1(
            title=title,
            description=description,
            base=self.base,
            scale=self.scale,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            strategy={roll.strategy.name: self.gen_strategy_report(roll, log) for roll in self.rolls},
            benchmark=self.gen_benchmark_report(benchmark)
        )


__all__ = ["BaseTrader", "SingleTrader", "MultiTrader"]
