

class Image:
    @classmethod
    def image(cls, image_url, image_name: str = 'image'):
        if image_url:
            return [
                {
                    "type": "image",
                    "block_id": "image_block",
                    "image_url": image_url,
                    "alt_text": image_name
                }
            ]
        return []