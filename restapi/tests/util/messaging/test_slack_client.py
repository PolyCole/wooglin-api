import os
import unittest
from unittest import mock
from restapi.client.slack_client import SlackClient


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    body = kwargs.get('json', None)

    if body is None:
        return MockResponse({}, 200)

    if body is not None and body['text'] == 'test200':
        return MockResponse({"ok": True}, 200)
    elif body is not None and body['text'] == 'test400':
        return MockResponse({"ok": False}, 400)
    elif body is not None and body['text'] == 'test500':
        return MockResponse({"ok": False}, 500)

    return MockResponse(None, 404)


# Our test case class
class TestSlackClient(unittest.TestCase):

    def setUp(self):
        os.environ['SLACK_TOKEN'] = 'test_token'
        self.slack_url = 'https://test.slack.api.here.com/postMessage'

    # let's test that the client throws if the token is not set
    def test_client_throws_if_token_not_set(self):
        os.environ.clear()
        self.assertRaises(Exception, SlackClient)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_successful_post(self, mock_post):
        test_slack_client = SlackClient()
        is_ok, response = test_slack_client.send_message(message='test200', channel='test_channel')
        self.assertEqual(is_ok, True)
        self.assertEqual(response, {"ok": True})

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_failed_post(self, mock_post):
        test_slack_client = SlackClient()
        is_ok, response = test_slack_client.send_message(message='test400', channel='test_channel')
        self.assertEqual(is_ok, False)
        self.assertEqual(response, {"ok": False})

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_failed_post_with_500(self, mock_post):
        test_slack_client = SlackClient()
        is_ok, response = test_slack_client.send_message(message='test500', channel='test_channel')
        self.assertEqual(is_ok, False)
        self.assertEqual(response, {"ok": False})

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_failed_post_with_404(self, mock_post):
        test_slack_client = SlackClient()
        is_ok, response = test_slack_client.send_message(message='test404', channel='test_channel')
        self.assertEqual(is_ok, False)
        self.assertEqual(response, None)

    # let's test that send_message can handle blocks
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_send_message_with_blocks(self, mock_post):
        test_slack_client = SlackClient()
        is_ok, response = test_slack_client.send_message(message='test200', channel='test_channel', blocks=[
            {'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'test'}}])
        self.assertEqual(is_ok, True)
        self.assertEqual(response, {"ok": True})
