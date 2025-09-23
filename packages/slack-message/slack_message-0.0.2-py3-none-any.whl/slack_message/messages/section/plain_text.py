from ...blocks import Section
from ...interface import BaseSlackMessage


class PlainTextMessage(BaseSlackMessage):
    def __init__(self, plain_text: str, **kwargs):
        super().__init__(**kwargs)
        self.plain_text = plain_text

    def build_blocks(self) -> list:
        blocks = Section.plain_text(self.plain_text)
        return blocks