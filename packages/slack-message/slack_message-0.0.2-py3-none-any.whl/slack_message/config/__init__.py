from typing import Dict

from ..bot import slack_bot


def configure_slack(token: str, recipients: Dict[str, str]):
    slack_bot.connect(token=token)
    for recipient_id, recipient_name in recipients.items():
        slack_bot.add_recipient(recipient_id, recipient_name)
