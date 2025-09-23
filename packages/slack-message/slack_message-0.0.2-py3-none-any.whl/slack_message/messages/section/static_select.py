from typing import Optional, Iterable

from ...blocks import Section
from ...interface import BaseSlackMessage


class StaticSelectMessage(BaseSlackMessage):
    def __init__(self, options: Iterable, text_before_option: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.text_before_option = text_before_option
        self.options = options

    def build_blocks(self) -> list:
        blocks = Section.static_select(options=self.options, text=self.text_before_option)
        return blocks