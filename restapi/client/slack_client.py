import os
import logging
import requests


# The client used to interact with the Slack API
class SlackClient:
    def __init__(self):
        self.SLACK_URL = "https://slack.com/api/chat.postMessage"
        self.SLACK_TOKEN = os.environ.get("SLACK_TOKEN", None)
        print(self.SLACK_TOKEN)
        self.logger = logging.getLogger(__name__)

        if self.SLACK_TOKEN is None:
            self.logger.error("SLACK_TOKEN not set")
            raise Exception("SLACK_TOKEN not set")

    # Send a message to a channel, returns tuple of (status_code, response)
    def send_message(self, message: str, channel: str, blocks: list = None) -> (bool, requests.Response):
        if blocks is None:
            print("No blocks provided to send_message")

        headers = {
            "Authorization": f"Bearer {self.SLACK_TOKEN}",
            "Content-Type": "application/json; charset=utf-8"
        }

        payload = {
            "channel": channel,
            "text": message,
            "blocks": blocks
        }

        print(f"payload: {payload}")

        response = self.post_message(headers, payload)
        return response.status_code == 200, response.json()

    def post_message(self, headers, payload) -> requests.Response:
        print(f"Sending message to slack: {payload}")

        response = requests.post(self.SLACK_URL, headers=headers, json=payload)
        print(f"Slack response: {response}")

        if response.status_code != 200:
            self.logger.error(f"Slack response not ok: {response}")

        return response
