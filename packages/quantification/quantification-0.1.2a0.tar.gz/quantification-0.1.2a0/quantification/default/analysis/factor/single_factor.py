from datetime import date
from functools import lru_cache

import numpy as np
import pandas as pd
from pydantic import BaseModel

from quantification.core import (
    Stock,
    BaseAPI,
    BaseBroker,
    Field,
    Trigger,
    Portfolio,
    logger,
    BaseStage,
    StockOrder,
    RMB,
    SingleStrategyReportV1,
    MultiStrategyReportV1
)
from quantification.default.use import use_factors, BaseFactor
from quantification.default.trader import LongShortSingleTrader, LongShortMultiTrader
from quantification.default.strategy import SimpleStrategy


class SingleFactorAnalysisReportV1(BaseModel):
    long_short: SingleStrategyReportV1
    stride: MultiStrategyReportV1


class MarketCap(BaseFactor):
    fields = [Field.ST_总市值]

    def calculate(self, stock: type[Stock], data: pd.DataFrame, day: date):
        valid_data = data[data[Field.ST_总市值] != "invalid"]
        return valid_data.iloc[-1][Field.ST_总市值]


class SingleFactorAnalysis:
    def __init__(
            self,
            api: BaseAPI,
            start_date: date,
            end_date: date,
            volume: float,
            stage: type[BaseStage],
            trigger: Trigger,
            factor: type[BaseFactor],
            stocks: list[type[Stock]],
            brokers: list[type[BaseBroker]],
            padding: int = 180,
            stride_size: int = 10,
    ) -> None:
        self.api = api
        self.start_date = start_date
        self.end_date = end_date
        self.volume = volume
        self.stage = stage
        self.trigger = trigger
        self.factor_clz = factor
        self.stocks = stocks
        self.brokers = brokers
        self.padding = padding
        self.stride_size = stride_size

    @property
    def long_short_strategy(self) -> SimpleStrategy:
        strategy = SimpleStrategy()

        @strategy.on(self.trigger)
        @use_factors(factor=self.factor_clz, CAP=MarketCap)
        def _(portfolio: Portfolio, factors: pd.DataFrame):
            logger.info(f"平仓前持仓:{portfolio}")
            for stock in portfolio[Stock]:
                if stock.amount > 0:
                    yield StockOrder(stock, "sell", share=stock.amount)
                else:
                    yield StockOrder(stock, "buy", share=-stock.amount)
            logger.info(f"平仓后持仓:{portfolio}")

            factors["rank"] = factors["factor"].rank(ascending=False, method='min')
            factors = factors.sort_values(by=["rank"], ascending=True, ignore_index=True)
            factors = factors.dropna()

            tail = factors.tail(10)
            tail_total_cap = tail["CAP"].sum()
            for _, row in tail.iterrows():
                order_value = self.volume * row["CAP"] / tail_total_cap
                logger.info(f"买入{row["Stock"]} 价值{order_value:.2f}")
                yield StockOrder(row["Stock"], "buy", value=order_value)

            head = factors.head(10)
            head_total_cap = head["CAP"].sum()
            for _, row in head.iterrows():
                order_value = self.volume * row["CAP"] / head_total_cap
                logger.info(f"卖出{row["Stock"]} 价值{order_value:.2f}")
                yield StockOrder(row["Stock"], "sell", value=order_value)

            logger.info(f"调仓后持仓:{portfolio}")

        return strategy

    @property
    def stride_strategies(self) -> list[SimpleStrategy]:
        strategies = [
            SimpleStrategy(name=f"组别{i + 1}", context={"index": i, "total": self.stride_size})
            for i in range(self.stride_size)
        ]

        @use_factors(factor=self.factor_clz, CAP=MarketCap)
        def _(factors: pd.DataFrame, context: dict, portfolio: Portfolio):
            logger.info(f"平仓前持仓:{portfolio}")
            for stock in portfolio[Stock]:
                yield StockOrder(stock, "sell", share=stock.amount)

            logger.info(f"平仓后持仓:{portfolio}")

            factors["rank"] = factors["factor"].rank(ascending=False, method='min')
            factors = factors.sort_values(by=["rank"], ascending=True, ignore_index=True)
            factors = factors.dropna()
            stride = pd.DataFrame(np.array_split(factors, context["total"])[context["index"]])
            cash = portfolio[RMB][0].amount
            total_cap = stride["CAP"].sum()
            for _, row in stride.iterrows():
                logger.info(f"买入{row["Stock"]} 价值{cash * row["CAP"] / total_cap:.2f}")
                yield StockOrder(row["Stock"], "buy", value=cash * row["CAP"] / total_cap)

            logger.info(f"调仓后持仓:{portfolio}")

        for strategy in strategies:
            strategy.on(self.trigger.copy)(_)

        return strategies

    @lru_cache()
    def run_long_short(self) -> LongShortSingleTrader:
        long_short_trader = LongShortSingleTrader(
            api=self.api,
            start_date=self.start_date,
            end_date=self.end_date,
            volume=2 * self.volume,
            long_short=True,
            stage=self.stage,
            strategy=self.long_short_strategy,
            stocks=self.stocks,
            padding=self.padding
        )


        long_short_trader.run()

        return long_short_trader

    @lru_cache()
    def run_stride(self) -> LongShortMultiTrader:
        stride_trader = LongShortMultiTrader(
            api=self.api,
            start_date=self.start_date,
            end_date=self.end_date,
            volume=self.volume,
            stage=self.stage,
            strategies=self.stride_strategies,
            stocks=self.stocks,
            padding=self.padding
        )

        stride_trader.run()

        return stride_trader

    @lru_cache()
    def run(self, benchmark: str):
        return SingleFactorAnalysisReportV1(
            long_short=self.run_long_short().report("多空策略", "", benchmark, False),
            stride=self.run_stride().report("分组策略", "", benchmark, False),
        )
