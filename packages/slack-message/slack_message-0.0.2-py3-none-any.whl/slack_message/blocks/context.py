

class Context:
    @classmethod
    def mrkdwn(cls, text:str) -> dict:
        return {
            "type": "mrkdwn",
            "text": text
        }

    @classmethod
    def image_url(cls, image_url: str) -> dict:
        return {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": "image"
                }