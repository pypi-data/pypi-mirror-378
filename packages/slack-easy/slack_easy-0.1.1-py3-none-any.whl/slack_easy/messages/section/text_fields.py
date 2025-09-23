from ...blocks import Section
from ...interface import BaseSlackMessage


class TextFieldsMessage(BaseSlackMessage):
    def __init__(self, fields, **kwargs):
        super().__init__(**kwargs)
        self.fields: list[str] = fields

    def build_blocks(self) -> list:
        blocks = Section.text_fields(self.fields)
        return blocks
