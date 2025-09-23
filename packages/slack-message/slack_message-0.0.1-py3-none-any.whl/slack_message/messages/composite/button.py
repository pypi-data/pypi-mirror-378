import logging

from ...blocks import Actions, Section
from ...interface import BaseSlackMessage

logger = logging.getLogger(__name__)

class ButtonMessage(BaseSlackMessage):
    def __init__(self, text: str = None, **kwargs):
        self.text = text
        button_params = {k: v for k, v in kwargs.items() if k.startswith("button_")}

        for key in button_params:
            del kwargs[key]

        button_numbers = set()
        for param in button_params:
            parts = param.split("_")
            if len(parts) == 3 and parts[0] == "button":
                button_numbers.add(parts[1])
        if not button_numbers:
            raise ValueError("At least one button must be provided (use button_1_text and related parameters)")

        self.buttons: list[dict] = []
        for num in sorted(button_numbers):
            text_key = f"button_{num}_text"
            if text_key not in button_params:
                raise ValueError(f"Button {num} is missing required 'text' (use {text_key})")

            button = {
                "text": button_params[text_key]
            }

            style = button_params.get(f"button_{num}_style")
            if style and style in ["primary", "danger"]:
                button["style"] = style
            value = button_params.get(f"button_{num}_value")
            if value:
                button["value"] = value
            url = button_params.get(f"button_{num}_url")
            if url:
                button["url"] = url
            self.buttons.append(button)
        super().__init__(**kwargs)

    def build_blocks(self) -> list[dict]:
        if self.text is not None and len(self.buttons) == 1:
            blocks = Section.button(text=self.text, button=self.buttons[0])
        else:
            if self.text is not None:
                logger.warning(
                    f"Multiple buttons detected (count: {len(self.buttons)}). When using multiple buttons, "
                    "Actions.buttons() method will be used. The top-level 'text' parameter "
                    "will be ignored as it's not supported for multi-button layouts.",
                )
            blocks = Actions.buttons(buttons=self.buttons)
        return blocks