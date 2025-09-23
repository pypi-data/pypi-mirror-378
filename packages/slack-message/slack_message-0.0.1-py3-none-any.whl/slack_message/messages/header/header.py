from ...blocks.header import Header
from ...blocks.divider import Divider
from ...interface import BaseSlackMessage


class HeaderMessage(BaseSlackMessage):
    def __init__(self, header: str, divider: bool=True, **kwargs):
        super().__init__(**kwargs)
        self.header = header
        self.divider = divider

    def build_blocks(self) -> list:
        blocks = Header.plain_text(self.header)
        if self.divider:
            blocks += Divider.divider()
        return blocks

