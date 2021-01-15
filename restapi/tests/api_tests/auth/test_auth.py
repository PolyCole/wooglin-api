from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from restapi.tests.testing_utilities import get_tokens, get_response_content

from restapi.models.members import Member


class ApiTests(APITestCase):
    def setUp(self):
        user_account = User.objects.create_user("pparker", "peter@avengers.com", "totallyNotSpiderman", is_staff=True)

        Member.objects.create(
            user=user_account,
            name="Pete Parker",
            first_name="Pete",
            last_name="Parker",
            legal_name="Peter Parker",
            address="123 Spiderman Street",
            email="peter@avengers.com",
            phone="123.456.7890",
            rollnumber="1",
            member_score="45.5",
            inactive_flag=False,
            abroad_flag=False,
            present=5,
            position="Member"
        )

    def test_token_get(self):
        """
        Ensuring we're able to send a request to get a token.
        """

        url = '/api/token/'

        data = {}
        response = self.client.post(url, data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('username' in content)
        self.assertEqual(content['username'], ["This field is required."])

        self.assertTrue('password' in content)
        self.assertEqual(content['password'], ["This field is required."])

        data = {'username': 'pparker', 'password': 'totallyNotSpiderman'}
        response = self.client.post(url, data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(content['access']), 0)

    def test_token_refresh(self):
        """
        Ensuring we're able to refresh our current token.
        """
        token = get_tokens("pparker", "totallyNotSpiderman")

        client = APIClient()

        url = '/api/token/refresh/'

        data = {}
        response = client.post(url, data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('refresh' in content)
        self.assertEqual(content['refresh'], ["This field is required."])

        data = {'refresh': str(token['refresh'])}
        response = client.post(url, data, format='json')
        content = get_response_content(response)

        self.assertTrue('access' in content)
        self.assertGreaterEqual(len(content['access']), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
