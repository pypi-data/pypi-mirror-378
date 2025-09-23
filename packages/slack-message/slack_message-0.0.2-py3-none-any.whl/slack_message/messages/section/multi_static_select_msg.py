from typing import Iterable

from ...blocks import Section
from ...interface import BaseSlackMessage

class MultiStaticSelectMessage(BaseSlackMessage):
    def __init__(self, text_before_option: str, options: Iterable, **kwargs):
        super().__init__(**kwargs)
        self.text_before_option = text_before_option
        self.options = options

    def build_blocks(self) -> list:
        blocks = Section.multi_static_select(text=self.text_before_option, options=self.options)
        return blocks
