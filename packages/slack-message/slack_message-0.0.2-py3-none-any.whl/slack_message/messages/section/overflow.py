from ...blocks import Section
from ...interface import BaseSlackMessage


class OverflowMessage(BaseSlackMessage):
    def __init__(self, text: str, options: list[str], **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.options = options

    def build_blocks(self):
        blocks = Section.overflow(text=self.text, options=self.options)
        return blocks