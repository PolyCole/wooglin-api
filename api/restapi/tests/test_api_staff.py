from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import json
from .testing_utilities import get_tokens, get_authed_client, generate_fake_new_user

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

        user = User.objects.get(email='peter@avengers.com')

        url = '/api/v1/member/' + str(user.id) + '/'

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

        self.assertTrue('name' in content)
        self.assertTrue('address' in content)
        self.assertTrue('member_score' in content)
        self.assertEqual(content['name'], "Pete Parker")

    def test_create_happy_path(self):
        """
        Testing if we are able to create a new member account when providing the proper information.
        """
        token = get_tokens('pparker', "totallyNotSpiderman")['access']
        url = '/api/v1/member/'

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        data = {
            'name': 'Tony Stark',
            'first_name': "Tony",
            "last_name": "Stark",
            "legal_name": "Anthony Stark",
            "address": "123 Stark Tower",
            "email": "tony@avengers.com",
            "phone": "123.456.7894",
            "rollnumber": "1010",
            "inactive_flag": True,
            "abroad_flag": False,
            "position": "Member"
        }

        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        response = client.post(url, data=data, format='json')

        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(content['name'], "Tony Stark")
        self.assertEqual(content['phone'], '123.456.7894')
        self.assertEqual(content['member_score'], -1.0)
        self.assertEqual(content['temp_password'], True)
        self.assertEqual(content['present'], 0)

        new_member = Member.objects.get(email="tony@avengers.com")
        self.assertEqual(new_member.name, "Tony Stark")
        self.assertEqual(new_member.phone, '123.456.7894')
        self.assertEqual(new_member.member_score, -1.0)
        self.assertEqual(new_member.temp_password, True)
        self.assertEqual(new_member.present, 0)

        new_user = User.objects.get(email="tony@avengers.com")
        self.assertEqual(new_user.email, "tony@avengers.com")
        self.assertEqual(new_user.username, 'tony.stark')

    def test_create_user_duplicate_reserved_fields(self):
        """
        Testing if we are turned away when trying to create a new member account for a email or phone number that already exists.
        """
        token = get_tokens('pparker', "totallyNotSpiderman")['access']
        url = '/api/v1/member/'

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Base request data.
        data = {
            'name': 'Tony Stark',
            'first_name': "Tony",
            "last_name": "Stark",
            "legal_name": "Anthony Stark",
            "address": "123 Stark Tower",
            "rollnumber": "1010",
            "inactive_flag": True,
            "abroad_flag": False,
            "position": "Member"
        }

        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        # Test 1: Duplicate email.
        data['email'] = 'peter@avengers.com'
        data['phone'] = '123.123.1234'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'], "I'm sorry, it looks like there's already a user with that email.")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        # Test 2: Duplicate phone number.
        data['email'] = 'tony@avengers.com'
        data['phone'] = '123.456.7890'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['phone'], "A member account with that phone number already exists.")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        # Test 3: Duplicate email and phone number.
        data['email'] = 'peter@avengers.com'
        data['phone'] = '123.456.7890'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['phone'],
                         "A member account with that phone number already exists.")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

    def test_create_member_sensitive_fields_overridden(self):
        """
        Testing if we try and create a member account with sensative parameters included, they're properly changed before creation.
        """
        url = '/api/v1/member/'

        client = get_authed_client('pparker', 'totallyNotSpiderman')

        data = {
            'name': 'Tony Stark',
            'first_name': "Tony",
            "last_name": "Stark",
            "legal_name": "Anthony Stark",
            "address": "123 Stark Tower",
            "email": "tony@avengers.com",
            "phone": "123.456.7894",
            "rollnumber": "1010",
            "inactive_flag": True,
            "abroad_flag": False,
            "position": "Member",
            # Sensative (calculated) fields.
            "present": 14,
            "member_score": -15,
            "temp_password": False
        }

        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(content['member_score'], -1.0)
        self.assertEqual(content['temp_password'], True)
        self.assertEqual(content['present'], 0)

        new_member = Member.objects.get(email="tony@avengers.com")
        self.assertEqual(new_member.member_score, -1.0)
        self.assertEqual(new_member.temp_password, True)
        self.assertEqual(new_member.present, 0)

    def test_pagination(self):
        """
        Testing that the Members table successfully paginates.
        """
        url = '/api/v1/member/'
        client = get_authed_client('pparker', 'totallyNotSpiderman')

        # First, let's ensure that the API paginates by default.
        response = client.get(url, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertTrue('count' in content)
        self.assertTrue('next' in content)
        self.assertTrue('previous' in content)
        self.assertEqual(content['previous'], None)
        self.assertEqual(content['count'], 1)

        # Now, let's populate the table with a few more user objects and then try actual pagination.
        for x in range(0, 25):
            generate_fake_new_user()

        url = '/api/v1/member/?page=1'
        response = client.get(url, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(Member.objects.count(), 26)
        self.assertEqual(content['count'], 26)
        self.assertEqual(content['next'], 'http://testserver/api/v1/member/?page=2')
        self.assertEqual(content['previous'], None)

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

    def test_email_regex_create(self):
        url = '/api/v1/member/'
        client = get_authed_client('pparker', 'totallyNotSpiderman')

        data = {
            'name': 'Tony Stark',
            'first_name': "Tony",
            "last_name": "Stark",
            "legal_name": "Anthony Stark",
            "address": "123 Stark Tower",
            "email": "tony@avengers.com",
            "phone": "123.456.7894",
            "rollnumber": "1010",
            "inactive_flag": True,
            "abroad_flag": False,
            "position": "Member"
        }

        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        # Just a buncha invalid email addresses
        self.bogus_email_test(client, data, 'tonyavengers.com')
        self.bogus_email_test(client, data, '@avengers.com')
        self.bogus_email_test(client, data, ' @avengers.com')
        self.bogus_email_test(client, data, 'tony@aven gers.com')
        self.bogus_email_test(client, data, 'tony@avengers')
        self.bogus_email_test(client, data, 't @avengers.co')
        self.bogus_email_test(client, data, '123.456.7890')
        self.bogus_email_test(client, data, 'Hello world!')

        # Testing a VALID email address
        data['email'] = 'tony@avengers.com'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('name' in content)
        self.assertTrue('legal_name' in content)
        self.assertTrue(User.objects.count(), 2)
        self.assertTrue(Member.objects.count(), 2)

    def test_phone_regex_create(self):
        url = '/api/v1/member/'
        client = get_authed_client('pparker', 'totallyNotSpiderman')

        data = {
            'name': 'Tony Stark',
            'first_name': "Tony",
            "last_name": "Stark",
            "legal_name": "Anthony Stark",
            "address": "123 Stark Tower",
            "email": "tony@avengers.com",
            "phone": "1234567894",
            "rollnumber": "1010",
            "inactive_flag": True,
            "abroad_flag": False,
            "position": "Member"
        }

        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

        # Just a buncha invalid phone numbers
        self.bogus_phone_test(client, data, '123.456.789')
        self.bogus_phone_test(client, data, '1.1.1.1.1.1.1')
        self.bogus_phone_test(client, data, '192.168.0.1')
        self.bogus_phone_test(client, data, '1234567890')
        self.bogus_phone_test(client, data, '(123)-456-7890')
        self.bogus_phone_test(client, data, '123-456-7890')
        self.bogus_phone_test(client, data, '(123).456.7890')
        self.bogus_phone_test(client, data, '(123.456.6798')
        self.bogus_phone_test(client, data, 'Hello world!')

        # Testing a VALID phone number
        data['phone'] = '234.724.2342'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('name' in content)
        self.assertTrue('legal_name' in content)
        self.assertTrue(User.objects.count(), 2)
        self.assertTrue(Member.objects.count(), 2)

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

    def bogus_email_test(self, client, data, email):
        data['email'] = email
        response = client.post('/api/v1/member/', data=data, format='json')
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'], "It would appear that you haven't entered a valid email address!")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

    def bogus_phone_test(self, client, data, phone):
        data['phone'] = phone
        response = client.post('/api/v1/member/', data=data, format='json')
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['phone'], "Phone number is in an improper format. Please make sure the phone number "
                                           "is in the form xxx.xxx.xxxx")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)
