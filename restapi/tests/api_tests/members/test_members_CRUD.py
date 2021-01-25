from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import json
from restapi.tests.testing_utilities import *

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

    # Getting without a token
    def test_unauthed_get(self):

        response = self.client.get('/api/v1/member/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Getting with a non-admin token.
    def test_authed_get_nonadmin_acct(self):
        member = generate_fake_new_user(False)

        token = get_tokens(member.name, "fake_password")['access']
        user = User.objects.get(email=member.email)

        url = '/api/v1/member/' + str(user.id) + '/'

        client = APIClient()

        # Trying to get with bogus token
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'helloworld')
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Getting with a legitimate token.
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
        response = client.get(url, data={'format': 'json'})
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('name' in content)
        self.assertTrue('address' not in content)
        self.assertTrue('member_score' not in content)
        self.assertEqual(content['name'], member.name)

    # Getting with an admin token
    def test_authed_get_admin_acct(self):
        member = generate_fake_new_user(True)

        token = get_tokens(member.name, "fake_password")['access']
        user = User.objects.get(email=member.email)

        url = '/api/v1/member/' + str(user.id) + '/'

        client = APIClient()

        # Trying to get with bogus token
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'helloworld')
        response = client.get(url, data={'format': 'json'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Getting with a legitimate token.
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
        response = client.get(url, data={'format': 'json'})
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('name' in content)
        self.assertTrue('address' in content)
        self.assertTrue('member_score' in content)
        self.assertEqual(content['name'], member.name)

    # Ensuring the API properly paginates on the list operation.
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

    # Getting with a non-admin token based on defined query parameters.
    def test_get_with_query_parameters_non_admin(self):
        member = generate_fake_new_user(False)
        token = get_tokens(member.name, "fake_password")['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Ensuring invalid search parameters are ignored, and treated like a regular request.
        url = '/api/v1/member/?test=123'
        content = get_response_content(client.get(url, data={'format': 'json'}))

        self.assertEqual(content['count'], 2)
        self.assertTrue('results' in content)

        member_objects = content['results']
        self.assertTrue('member_score' not in member_objects[0])
        self.assertTrue('address' not in member_objects[0])

        # Attempting to search with a valid search parameter:
        name_arg = str(urlify(member.name, len(member.name)))
        url = '/api/v1/member/?name=' + name_arg
        content = get_response_content(client.get(url, data={'name': str(name_arg)}))

        self.assertEqual(content['count'], 1)
        member_objects = content['results']
        self.assertEqual(len(member_objects), 1)
        self.assertEqual(member_objects[0]['name'], member.name)
        self.assertTrue('member_score' not in member_objects[0])
        self.assertTrue('address' not in member_objects[0])

        # Attempting to search by a parameter we don't have access to.
        # Expected behavior: Ignored completely.
        url = '/api/v1/member/?member_score=' + str(23.4)
        content = get_response_content(client.get(url, data={'member_score': str(23.4)}))

        self.assertTrue('count' in content)
        self.assertEqual(content['count'], 2)
        self.assertEqual(len(content['results']), 2)
        self.assertTrue('member_score' not in content['results'][0])
        self.assertTrue('address' not in content['results'][0])

    # Getting with an admin token based on defined query parameters.
    def test_get_with_query_parameters(self):
        member = generate_fake_new_user(True)
        token = get_tokens(member.name, "fake_password")['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Ensuring invalid search parameters are ignored, and treated like a regular request.
        url = '/api/v1/member/?test=123'
        content = get_response_content(client.get(url, data={'format': 'json'}))

        self.assertEqual(content['count'], 2)
        self.assertTrue('results' in content)

        # Attempting to search with a valid search parameter:
        name_arg = str(urlify(member.name, len(member.name)))
        url = '/api/v1/member/?name=' + name_arg
        content = get_response_content(client.get(url, data={'name': str(name_arg)}))

        self.assertEqual(content['count'], 1)
        member_objects = content['results']
        self.assertEqual(len(member_objects), 1)
        self.assertTrue('name' in member_objects[0])
        self.assertEqual(member_objects[0]['name'], member.name)
        self.assertTrue('member_score' in member_objects[0])

    # Creating a member with a non-admin token.
    def test_create_operation_denied(self):
        member = generate_fake_new_user(False)
        token = get_tokens(member.name, "fake_password")['access']

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
            "phone": "123.456.7890",
            "rollnumber": "1010",
            "inactive_flag": True,
            "position": "Member"
        }

        users_before, members_before = User.objects.count(), Member.objects.count()

        response = client.post(url, data=data, format='json')
        content = get_response_content(response)

        users_after, members_after = User.objects.count(), Member.objects.count()

        self.assertEqual(users_before, users_after)
        self.assertEqual(members_before, members_after)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(content['detail'], "You do not have permission to perform this action.")

    # Creating a member with an admin token and valid fields.
    def test_create_happy_path(self):
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

        users_before, members_before = User.objects.count(), Member.objects.count()

        response = client.post(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(users_before + 1, User.objects.count())
        self.assertEqual(members_before + 1, Member.objects.count())

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

    # Creating a member with an admin token and a reserved field that already exists.
    def test_create_user_duplicate_reserved_fields(self):
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

        users_before, members_before = User.objects.count(), Member.objects.count()

        # Test 1: Duplicate email.
        data['email'] = 'peter@avengers.com'
        data['phone'] = '123.123.1234'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'], "I'm sorry, it looks like there's already a user with that email.")
        self.assertTrue(User.objects.count(), users_before)
        self.assertTrue(Member.objects.count(), members_before)

        # Test 2: Duplicate phone number.
        data['email'] = 'tony@avengers.com'
        data['phone'] = '123.456.7890'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['phone'], "A member account with that phone number already exists.")
        self.assertTrue(User.objects.count(), users_before)
        self.assertTrue(Member.objects.count(), members_before)

        # Test 3: Duplicate email and phone number.
        data['email'] = 'peter@avengers.com'
        data['phone'] = '123.456.7890'
        response = client.post(url, data=data, format='json')
        response.render()
        content = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['phone'],
                         "A member account with that phone number already exists.")
        self.assertTrue(User.objects.count(), users_before)
        self.assertTrue(Member.objects.count(), members_before)

    # Creating a member with an admin token but specifying calculated fields.
    def test_create_member_sensitive_fields_overridden(self):
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

    # Creating a member with invalid email address formats.
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

    # Creating a member with invalid phone number formats.
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

    # Trying to delete with a non-admin token.
    def test_delete_forbidden(self):
        member = generate_fake_new_user(False)
        token = get_tokens(member.name, "fake_password")['access']

        url = '/api/v1/member/' + str(member.id) + "/"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

        response = client.delete(url, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    # Trying to delete with an admin token.
    def test_delete(self):
        member = generate_fake_new_user(True)
        token = get_tokens(member.name, "fake_password")['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        url = '/api/v1/member/'
        members_before, users_before = Member.objects.count(), User.objects.count()
        response = client.delete(url, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'Method "DELETE" not allowed.')

        self.assertEqual(Member.objects.count(), members_before)
        self.assertEqual(User.objects.count(), users_before)

        url = '/api/v1/member/123/'
        response = client.delete(url, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('primary_key' in content)
        self.assertEqual(content['primary_key'], "The specified primary key does not exist.")
        self.assertEqual(Member.objects.count(), members_before)
        self.assertEqual(User.objects.count(), users_before)

        to_delete_member = generate_fake_new_user(False)

        members_before, users_before = Member.objects.count(), User.objects.count()

        url = '/api/v1/member/' + str(to_delete_member.id) + "/"
        response = client.delete(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Member.objects.filter(id=to_delete_member.id).count(), 0)
        self.assertEqual(Member.objects.count(), members_before - 1)
        self.assertEqual(User.objects.count(), users_before - 1)

    # Trying to update a Member model without the proper perms.
    def test_partial_update_forbidden(self):
        member = generate_fake_new_user(False)
        token = get_tokens(member.name, "fake_password")['access']

        url = '/api/v1/member/' + str(member.id) + "/"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        data = {'name': 'Cole Polyak'}
        response = client.patch(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        db_member = Member.objects.filter(email=member.email)[0]
        self.assertEqual(db_member.name, member.name)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')

    # Trying to update a Member model with the proper perms.
    def test_partial_update(self):
        member = generate_fake_new_user(True)
        token = get_tokens(member.name, "fake_password")['access']

        url = '/api/v1/member/' + str(member.id) + "/"

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Checking to see that calculated fields are un-patch-able.
        data = {'member_score': 13.4, 'present': 23}
        response = client.patch(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('member_score' in content)
        self.assertEqual(content['member_score'], 'member_score is a calculated field and cannot be updated via PATCH.')
        self.assertTrue('present' in content)
        self.assertEqual(content['present'], 'present is a calculated field and cannot be updated via PATCH.')

        # Randomly specified fields are ignored by the API.
        data = {'name': 'Cole Polyak', 'hello': 'world'}
        response = client.patch(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in content)
        self.assertEqual(content['name'], 'Cole Polyak')

        db_member = Member.objects.filter(email=member.email)[0]
        self.assertEqual(db_member.name, 'Cole Polyak')
        self.assertFalse('hello' in content)

        # Regular PATCH, with multiple fields.
        data = {'name': 'Cole Polyak', 'first_name': 'Cole', 'last_name': 'Polyak'}
        response = client.patch(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in content)
        self.assertEqual(content['name'], 'Cole Polyak')
        self.assertTrue('first_name' in content)
        self.assertEqual(content['first_name'], 'Cole')
        self.assertTrue('last_name' in content)
        self.assertEqual(content['last_name'], 'Polyak')

        db_member = Member.objects.filter(email=member.email)[0]
        self.assertEqual(db_member.name, 'Cole Polyak')
        self.assertEqual(db_member.first_name, 'Cole')
        self.assertEqual(db_member.last_name, 'Polyak')

    # Trying to PUT a Member model without the proper perms.
    def test_put_update_forbidden(self):
        member = generate_fake_new_user(False)
        token = get_tokens(member.name, "fake_password")['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Trying with an existing id.
        url = '/api/v1/member/' + str(member.id) + "/"
        data = {'name': 'Cole Polyak'}
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        db_member = Member.objects.filter(email=member.email)[0]
        self.assertEqual(db_member.name, member.name)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')

        # Trying with a non-existent id.
        url = '/api/v1/member/45/'
        data = {'name': 'Cole Polyak'}
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        db_member = Member.objects.filter(email=member.email)[0]
        self.assertEqual(db_member.name, member.name)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')

    # Trying to PUT a Member model with the proper perms.
    def test_put_update(self):
        member = generate_fake_new_user(True)
        token = get_tokens(member.name, "fake_password")['access']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))

        # Trying with an existing id.
        url = '/api/v1/member/' + str(member.id) + "/"
        data = {'name': 'Cole Polyak'}
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_member = Member.objects.filter(id=member.id)
        self.assertEqual(updated_member[0].name, 'Cole Polyak')

        # Trying to update email address.
        url = '/api/v1/member/' + str(member.id) + "/"
        data = {'email': 'colepolyak@gmail.com'}
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('email' in content)
        self.assertEqual(content['email'], 'Email is a field that must be modified by an administrator manually.')
        updated_member = Member.objects.filter(id=member.id)
        self.assertEqual(member.email, updated_member[0].email)

        # Trying to update on a non-existent id, with improper information.
        url = '/api/v1/member/123/'
        data = {
            'email': 'cole@gmail.com',
            'first_name': 'Peter',
            'last_name': 'Parker',
            'name': 'Peter Parker',
            'legal_name': 'Petathan Parker',
            'address': 'Stark Tower, Room 1',
            'phone': '000.000.0000',
            'rollnumber': 123456,
            'inactive_flag': False,
            'abroad_flag': True,
        }
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('position' in content)
        self.assertEqual(content['position'][0], 'This field is required.')
        self.assertEqual(Member.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

        # Trying to update a non-existent id with proper data.
        url = '/api/v1/member/123/'
        data['position'] = 'Test Member'
        response = client.put(url, data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('name' in content)
        self.assertEqual(content['name'], 'Peter Parker')
        self.assertEqual(Member.objects.count(), 3)
        self.assertEqual(User.objects.count(), 3)

    # Helper method for improper email formats.
    def bogus_email_test(self, client, data, email):
        data['email'] = email
        response = client.post('/api/v1/member/', data=data, format='json')
        response.render()
        content = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(content['email'], "It would appear that you haven't entered a valid email address!")
        self.assertTrue(User.objects.count(), 1)
        self.assertTrue(Member.objects.count(), 1)

    # Helper method for improper phone number formats.
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
