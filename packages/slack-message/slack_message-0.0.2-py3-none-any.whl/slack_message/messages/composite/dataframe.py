import pandas as pd
from tabulate import tabulate

from ...blocks import Section
from ...interface import BaseSlackMessage


class DataFrameMessage(BaseSlackMessage):
    def __init__(self, dataframe: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.dataframe: pd.DataFrame = dataframe
        self.df_headers: list[str] = kwargs.get('df_headers') if kwargs.get(
            'df_headers') else self.dataframe.columns.to_list()
        self.tablefmt: str = kwargs.get('tablefmt') if kwargs.get('tablefmt') else 'mixed_outline'
        self.show_index: bool = kwargs.get('show_index') if kwargs.get('show_index') else False

    def tabulate_message(self,
                         dataframe: pd.DataFrame
                         ):
        tabulate_msg = tabulate(tabular_data=dataframe,
                                tablefmt=self.tablefmt,
                                headers=self.df_headers,
                                showindex=self.show_index)
        tabulated_msg = f'```\n{tabulate_msg}\n```'
        return tabulated_msg


    def build_blocks(self) -> list[dict]:
        tabulated_msg = self.tabulate_message(self.dataframe)
        blocks = Section.mrkdwn(tabulated_msg)
        return blocks
