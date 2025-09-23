from ...blocks import Section
from ...interface import BaseSlackMessage


class UsersSelectMessage(BaseSlackMessage):
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def build_blocks(self) -> list:
        blocks = Section.users_select(self.text)
        return blocks