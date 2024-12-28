import os
from slack_sdk import WebClient


def send_to_slack(message):
    client = WebClient(token=os.environ["SLACK_TOKEN"])

    # Send a message
    client.chat_postMessage(
        channel=os.getenv("SLACK_CHANNEL"),
        text=message,
        username="SRE Buddy"
    )


class slack:
    def __init__(self):
        pass



