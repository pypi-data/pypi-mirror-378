from typing import Iterable

from ...blocks import Actions
from ...interface import BaseSlackMessage


class DatePickersMessage(BaseSlackMessage):
    def __init__(self, initial_dates: Iterable[str], **kwargs):
        super().__init__(**kwargs)
        self.initial_dates: Iterable[str] = initial_dates

    def build_blocks(self) -> list[dict]:
        blocks = Actions.datepickers(initial_dates=self.initial_dates)
        return blocks
