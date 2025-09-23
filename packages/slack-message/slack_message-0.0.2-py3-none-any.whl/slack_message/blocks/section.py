from typing import Optional, Iterable

from ..utils import is_valid_date_fmt, validate_options, validate_initial_time


class Section:
    @classmethod
    def plain_text(cls, text: str):
        if text:
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": text,
                        "emoji": True
                    }
                }
            ]
        else:
            return []

    @classmethod
    def mrkdwn(cls, text: str = None):
        if text:
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                }
            ]
        return []

    @classmethod
    def text_fields(cls, texts: list):
        if not isinstance(texts, list) or (isinstance(texts, list) and len(texts) == 0):
            raise ValueError("texts must be a list with at least one element")
        fields = []
        for text in texts:
            fields.append({"type": "mrkdwn", "text": text})
        return [
            {
                "type": "section",
                "fields": fields
            }
        ]

    @classmethod
    def users_select(cls, text: Optional[str] = None):
        if not text:
            text = "Please select a user"
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{text}"
                },
                "accessory": {
                    "type": "users_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a user",
                        "emoji": True
                    },
                    "action_id": "users_select_action"
                }
            }
        ]


    @classmethod
    @validate_options
    def static_select(cls, options: Iterable, text: Optional[str] = None):
        if not text:
            text = "Please select a option"
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{text}"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a item",
                        "emoji": True
                    },
                    "action_id": "users_select_action"
                }
            }
        ]
        option_list = []
        for i, opt in enumerate(options):
            option_list.append({
            "text": {
                "type": "plain_text",
                "text": f"{str(opt)}",
                "emoji": True
            },
            "value": f"value-{i}"
        })
        blocks[0]["accessory"]["options"] = option_list
        return blocks

    @classmethod
    @validate_options
    def multi_static_select(cls, text: str, options: Iterable):
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{text}"
                },
                "accessory": {
                    "type": "multi_static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select options",
                        "emoji": True
                    },
                    "action_id": "multi_static_select-action"
                }
            }
        ]
        option_list = []
        for i, opt in enumerate(options):
            option_list.append({
                "text": {
                    "type": "plain_text",
                    "text": f"{str(opt)}",
                    "emoji": True
                },
                "value": f"value-{i}"
            })
        blocks[0]["accessory"]["options"] = option_list
        return blocks

    @classmethod
    def button(cls, text: str, button: dict):
        """
        section button is shown as an accessory, for action button, it can contain several buttons
        :param url: if the button is a link
        :param text:
        :param button: dict must have key 'text'
        :return: list
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button["text"],
                        "emoji": True
                    },
                    "value": button.get("value", "button_value"),
                    "action_id": button.get("action_id", "button_action_id")
                }
            }
        ]
        url = button.get("url")
        if url is not None:
            blocks[0]["accessory"]["url"] = url
        style = button.get("style")
        if style is not None and style in ["primary", "danger"]:
            blocks[0]["accessory"]["style"] = style
        return blocks

    @classmethod
    def image(cls, text: str, image_url: str, alt_text: Optional[str] = None):
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": alt_text if alt_text else "alt_text",
                }
            }
        ]
        return blocks

    @classmethod
    def slack_image(cls):
        pass

    @classmethod
    @validate_options
    def overflow(cls, text: str, options: Iterable[str]):
        option_list: list = []
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {"type": "overflow"}
            }
        ]
        for i, opt in enumerate(options):
            option_list.append({
                "text": {
                    "type": "plain_text",
                    "text": f"{str(opt)}",
                    "emoji": True
                },
                "value": f"value-{i}"
            })
        blocks[0]["accessory"]["options"] = option_list
        return blocks

    @classmethod
    def datepicker(cls, text: str, initial_date: str):
        is_valid_date_fmt(initial_date)
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {
                    "type": "datepicker",
                    "initial_date": initial_date,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    },
                    "action_id": "datepicker-action"
                }
            }
        ]
        return blocks

    @classmethod
    @validate_options
    def checkboxes(cls, text: str, options: Iterable[str], options_description: Iterable[str]):
        """All check boxes are selectable"""
        option_list: list = []
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                },
                "accessory": {
                    "type": "checkboxes",
                    "action_id": "checkboxes-action"
                }
            }
        ]
        for i, opt in enumerate(options):
            option_list.append({
                "text": {
                    "type": "mrkdwn",
                    "text": f"{str(opt)}",
                },
                "value": f"value-{i}"
            })
        if options_description:
            for i, opt_desc in enumerate(options_description):
                option_list[i]["description"] = {
                    "type": "mrkdwn",
                    "text": opt_desc
                }
        blocks[0]["accessory"]["options"] = option_list
        return blocks

    @classmethod
    @validate_options
    def radio_buttons(cls, text, options: Iterable[str]):
        option_list: list = []
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
                "accessory": {
                    "type": "radio_buttons",
                    "action_id": "radio_buttons-action"
                }
            }
        ]
        for i, opt in enumerate(options):
            option_list.append({
                "text": {
                    "type": "mrkdwn",
                    "text": f"{str(opt)}"
                },
                "value": f"value-{i}"
            })
        blocks[0]["accessory"]["options"] = option_list
        return blocks

    @classmethod
    @validate_initial_time
    def time_picker(cls, text: str, initial_time: str):
        blocks: list[dict] = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
                "accessory": {
                    "type": "timepicker",
                    "initial_time": initial_time,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select time",
                        "emoji": True
                    },
                    "action_id": "timepicker-section"
                }
            }
        ]
        return blocks


