import pandas as pd

from ...blocks import Table
from ...interface import BaseSlackMessage


class SimpleTableMessage(BaseSlackMessage):
    def __init__(self, df: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.df = df

    def build_blocks(self):
        blocks = Table.simple_table(self.df)
        return blocks