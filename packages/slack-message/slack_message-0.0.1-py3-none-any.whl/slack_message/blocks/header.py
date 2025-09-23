from typing import Optional


class Header:
    @classmethod
    def plain_text(cls, header: Optional[str] = None) -> list:
        """
        header - text
        """
        if header:
            return [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": header,
                        "emoji": True
                    }
                }
            ]
        return []
