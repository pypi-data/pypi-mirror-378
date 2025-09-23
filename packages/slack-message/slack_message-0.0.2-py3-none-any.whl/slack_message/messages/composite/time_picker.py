from typing import Optional

from ...blocks import Actions, Section
from ...interface import BaseSlackMessage


class TimePickerMessage(BaseSlackMessage):
    def __init__(self, initial_time: str, text: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.initial_time = initial_time

    def build_blocks(self):
        if self.text is None:
            blocks = Actions.time_picker(self.initial_time)
        else:
            blocks = Section.time_picker(self.text, self.initial_time)
        return blocks