from typing import Iterable

from ..utils import is_valid_date_fmt, validate_options, validate_initial_time

class Actions:

    @classmethod
    def init_blocks(cls) -> list[dict]:
        return [{
            "type": "actions",
            "elements": []
        }]

    @classmethod
    def buttons(cls, buttons: list[dict]):
        blocks = cls.init_blocks()
        for i, button in enumerate(buttons):
            button_block = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": button["text"],
                },
                "action_id": f"action-button-{i}"
            }
            style = button.get("style")
            if style:
                button_block["style"] = style
            other_info = button.get("value", f"button_value-{i}")
            button_block["value"] = other_info
            url = button.get("url")
            if url:
                button_block["url"] = url
            blocks[0]["elements"].append(
                button_block
            )
        return blocks

    @classmethod
    def datepickers(cls, initial_dates: Iterable[str]):
        blocks = cls.init_blocks()
        for i, initial_date in enumerate(initial_dates):
            is_valid_date_fmt(initial_date)
            initial_date_block = {
					"type": "datepicker",
					"initial_date": initial_date,
					"placeholder": {
						"type": "plain_text",
						"text": "Select a date",
						"emoji": True
					},
					"action_id": f"action-datepickers-{i}"
				}
            blocks[0]["elements"].append(
                initial_date_block
            )
        return blocks

    @classmethod
    @validate_options
    def checkboxes(cls, options: Iterable[str], options_description: Iterable[str]):
        blocks = cls.init_blocks()
        option_list: list = []
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
        blocks[0]["elements"].append({
            "type": "checkboxes",
            "options": option_list
        })
        return blocks


    @classmethod
    @validate_options
    def radio_buttons(cls, options: Iterable[str]):
        blocks = cls.init_blocks()
        option_list: list = []
        for i, opt in enumerate(options):
            option_list.append({
                "text": {
                    "type": "mrkdwn",
                    "text": f"{str(opt)}",
                },
                "value": f"value-{i}"
            })
        blocks[0]["elements"].append({
            "type": "radio_buttons",
            "options": option_list
        })
        return blocks

    @classmethod
    @validate_initial_time
    def time_picker(cls, initial_time: str):
        blocks = cls.init_blocks()
        time_picker = {
            "type": "timepicker",
            "initial_time": initial_time,
            "placeholder": {
                "type": "plain_text",
                "text": "Select time",
                "emoji": True
            },
            "action_id": "timepicker-action"
        }
        blocks[0]["elements"].append(time_picker)
        return blocks


