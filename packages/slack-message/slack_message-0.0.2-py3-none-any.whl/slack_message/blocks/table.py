import pandas as pd


class Table:
    @classmethod
    def simple_table(cls, df: pd.DataFrame):
        blocks = [
            {
                "type": "table",
                "rows": []
            }
        ]
        headers = []

        if isinstance(df.columns, pd.MultiIndex):
            column_names = ['_'.join(map(str, col)) for col in df.columns]
        else:
            column_names = df.columns

        for column_name in column_names:
            headers.append(
                {
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": str(column_name),
                                    "style": {
                                        "bold": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            )
        blocks[0]["rows"].append(headers)

        for i, row in df.iterrows():
            one_row = []
            for j, col in enumerate(row):
                one_row.append({
                    "type": "rich_text",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": str(col),
                                    "style": {
                                        "bold": False
                                    }
                                }
                            ]
                        }
                    ]
                })
            blocks[0]["rows"].append(one_row)
        return blocks


