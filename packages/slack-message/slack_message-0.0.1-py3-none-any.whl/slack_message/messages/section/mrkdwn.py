from ...blocks import Section
from ...interface import BaseSlackMessage


class MrkDwnMessage(BaseSlackMessage):
    def __init__(self, mrkdwn_text: str, **kwargs):
        super().__init__(**kwargs)
        self.mrkdwn_text = mrkdwn_text

    def build_blocks(self) -> list:
        blocks = Section.mrkdwn(self.mrkdwn_text)
        return blocks
