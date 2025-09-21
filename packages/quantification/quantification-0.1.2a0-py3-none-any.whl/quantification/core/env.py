import datetime
from abc import ABCMeta
from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .strategy import BaseStrategy


@dataclass
class Env:
    date: datetime.date
    time: datetime.time
    strategy: "BaseStrategy" = None


class EnvGetter(metaclass=ABCMeta):
    getter: Callable[[], Env] | None = None

    @property
    def env(self) -> Env | None:
        if self.__class__.getter is not None:
            return self.__class__.getter()

        return None


__all__ = ['EnvGetter', "Env"]
