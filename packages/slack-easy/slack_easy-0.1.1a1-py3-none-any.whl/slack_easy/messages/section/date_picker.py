from ...blocks import Section
from ...interface import BaseSlackMessage


class DatePickerMessage(BaseSlackMessage):
    def __init__(self, text: str, initial_date: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.initial_date = initial_date

    def build_blocks(self):
        blocks = Section.datepicker(text=self.text, initial_date=self.initial_date)
        return blocks
