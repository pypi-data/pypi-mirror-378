from typing import Iterable, Optional

from ...blocks import Section, Actions
from ...interface import BaseSlackMessage


class CheckBoxesMessage(BaseSlackMessage):
    def __init__(self, options: Iterable, text: Optional[str] = None, options_description: Optional[Iterable] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.options = options
        self.options_description = options_description

    def build_blocks(self) -> list:
        if self.text is None:
            blocks = Actions.checkboxes(options=self.options, options_description=self.options_description)
        else:
            blocks = Section.checkboxes(text=self.text, options=self.options, options_description=self.options_description)
        return blocks