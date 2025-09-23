from typing import Iterable

from ...blocks import Section, Actions
from ...interface import BaseSlackMessage

class RadioButtonsMessage(BaseSlackMessage):
    def __init__(self, text: str, options: Iterable, **kwargs) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.options = options

    def build_blocks(self) -> list:
        if self.text is None:
            blocks = Actions.radio_buttons(options=self.options)
        else:
            blocks = Section.radio_buttons(text=self.text, options=self.options)
        return blocks
