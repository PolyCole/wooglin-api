from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import json
from .utilities import get_tokens

from restapi.models.members import Member


class ApiTests(APITestCase):
    def setUp(self):
        user_account = User.objects.create_user("pparker", "peter@avengers.com", "totallyNotSpiderman")

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

    def test_unauthed_get(self):
        """
        Ensuring we're sent away if we ask for member data while un-authed.
        """
        response = self.client.get('/api/v1/member/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authed_get(self):
        """
        Testing if we can access a record with a valid token.
        """
        token = get_tokens("pparker", "totallyNotSpiderman")['access']
        url = '/api/v1/member/1/'

        client = APIClient()

        # Trying to get with bogus token
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'Spiderman')
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Getting with a legitimate token.
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response.render()
        content = json.loads(response.content)

        # Checking content
        self.assertTrue('name' in content)
        self.assertTrue('address' not in content)
        self.assertTrue('member_score' not in content)
        self.assertEqual(content['name'], "Pete Parker")

    def test_token_get(self):
        """
        Ensuring we're able to send a request to get a token.
        """
        self.assertEqual(User.objects.count(), 1)

        url = '/api/token/'
        data = {'username': 'pparker', 'password': 'totallyNotSpiderman'}

        response = self.client.post(url, data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(content['access']), 0)

    def test_token_refresh(self):
        """
        Ensuring we're able to refresh our current token.
        """

        token = get_tokens("pparker", "totallyNotSpiderman")

        client = APIClient()

        url = '/api/token/refresh/'
        data = {'refresh': str(token['refresh'])}
        response = client.post(url, data, format='json')
        response.render()

        content = json.loads(response.content)
        self.assertTrue('access' in content)
        self.assertGreaterEqual(len(content['access']), 0)
