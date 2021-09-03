from rest_framework import status
from rest_framework.test import APITestCase

from restapi.tests.testing_utilities import *
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift

import datetime
import pytz


class ApiTests(APITestCase):
    def setUp(self):
        four_members = list()

        for x in range(0, 4):
            four_members.append(generate_fake_new_user())

        self.sbs = four_members

        timezone = pytz.timezone("America/Denver")
        now = datetime.datetime.now()

        two_hours = datetime.timedelta(hours=2)

        now = timezone.localize(now)

        shift = SoberBroShift.objects.create(
            date=datetime.datetime.today().date(),
            title="Test Shift",
            time_start=now,
            time_end=(now+two_hours),
            capacity=5
        )

        sbs = list()

        for member in four_members:
            sbs.append(SoberBro.objects.create(
                shift=shift,
                member=member
            ))

        self.shift = shift

    def test_unathed_sb_get(self):
        response = self.client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_shift_sbs(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        response = client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), 4)
        self.assertEqual(content[0]['shift']['title'], self.shift.title)
        self.assertEqual(content[0]['member']['name'], self.sbs[0].name)

    def test_add_sb_happy_path(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id, "member": member.id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('shift' in content[0])
        self.assertEqual(content[0]['shift']['id'], self.shift.id)

        self.assertTrue('member' in content[0])
        self.assertTrue('address' not in content[0]['member'])
        self.assertEqual(content[0]['member']['id'], member.id)

    def test_add_sb_fails_if_not_authed_user(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id, "member": self.sbs[0].id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('operation' in content)
        self.assertEqual(content['operation'], 'You are trying to either drop or add a sober bro who is not yourself. '
                                               'You do not have permission to do this.')
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 4)

    def test_add_other_member_to_shift_if_staff(self):
        member = generate_fake_new_user(True)
        add_to_shift = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id, "member": add_to_shift.id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('shift' in content[0])
        self.assertEqual(content[0]['shift']['id'], self.shift.id)

        self.assertTrue('member' in content[0])
        self.assertTrue('address' not in content[0]['member'])
        self.assertEqual(content[0]['member']['id'], add_to_shift.id)

    def test_add_sb_fails_with_improper_body_object(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('member' in content)
        self.assertEqual(content['member'], 'A member id is required to add or remove a member from a shift')
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 4)

        # This one leaves out shift, but it's specified in the URL so it should work.
        data = {"member": member.id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('shift' in content[0])
        self.assertEqual(content[0]['shift']['title'], self.shift.title)
        self.assertTrue('member' in content[0])
        self.assertEqual(content[0]['member']['name'], member.name)
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 5)

    def test_add_sb_fails_on_full_shift(self):
        SoberBro.objects.create(
            shift=self.shift,
            member=generate_fake_new_user()
        )

        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id, "member": member.id}
        response = client.post('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 5)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('shift' in content)
        self.assertEqual(content['shift'], 'Shift is currently full. Unable to add another brother.')
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 5)

    def test_delete_sb_happy_path(self):
        client = get_authed_client(self.sbs[0].name, 'fake_password')

        data = {"shift": self.shift.id, "member":self.sbs[0].id}
        response = client.delete('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('delete' in content)

        desc_sentence = 'Successfully removed ' + \
                        str(self.sbs[0].name) + \
                        ' from the Sober Bro shift titled ' + \
                        str(self.shift.title) + \
                        ' on ' + \
                        str(self.shift.date)
        self.assertEqual(content['delete'], desc_sentence)
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 3)

    def test_delete_sb_not_sb_on_shift(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        data = {"shift": self.shift.id, "member": member.id}
        response = client.delete('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('member' in content)
        self.assertEqual(content['member'], "The member you're trying to delete is not currently a part of this shift.")
        self.assertEqual(SoberBro.objects.filter(shift=self.shift).count(), 4)

    def test_delete_sb_member_id_not_included(self):
        client = get_authed_client(self.sbs[0].name, 'fake_password')

        data = {"shift": self.shift.id}
        response = client.delete('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data,
                                 format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('member' in content)
        self.assertEqual(content['member'], 'A member id is required to add or remove a member from a shift')

        # this should work fine even without shift ID, since we specify it in the URL
        data = {"member": self.sbs[0].id}
        response = client.delete('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', data=data,
                                 format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('delete' in content)

        desc_sentence = 'Successfully removed ' + \
                        str(self.sbs[0].name) + \
                        ' from the Sober Bro shift titled ' + \
                        str(self.shift.title) + \
                        ' on ' + \
                        str(self.shift.date)
        self.assertEqual(content['delete'], desc_sentence)
