from rest_framework import status
from rest_framework.test import APITestCase

from restapi.tests.testing_utilities import *
from restapi.models.sober_bros import SoberBro
from restapi.models.sober_bro_shifts import SoberBroShift

import datetime
from datetime import timedelta
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
        response = self.client.get('/api/v1/sober-bro-shift/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_shift_get_proper_range(self):
        """
        Ensuring basic index get returns only shifts in a 31-day period.
        """

        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        response = client.get('/api/v1/sober-bro-shift/', format='json')
        content = get_response_content(response)

        self.assertTrue('title' in content)
        self.assertEqual(content['date'], str(datetime.datetime.today().date()))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Now let's ensure that a shift occurring two months away isn't included in the returned object.
        shift = create_sober_shift()

        self.assertEqual(SoberBroShift.objects.count(), 2)

        response = client.get('/api/v1/sober-bro-shift/', format='json')
        content = get_response_content(response)

        self.assertTrue('title' in content)
        self.assertEqual(content['date'], str(datetime.datetime.today().date()))
        self.assertEqual(SoberBroShift.objects.all()[0].date, datetime.datetime.today().date())

        future_shift = datetime.datetime.today()
        future_shift = future_shift + datetime.timedelta(days=62)
        self.assertEqual(SoberBroShift.objects.all()[1].date, future_shift.date())

    def test_get_specific_shift(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        response = client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content['title'], self.shift.title)
        self.assertEqual(content['id'], self.shift.id)
        self.assertEqual(content['capacity'], self.shift.capacity)

    def test_get_shift_members(self):
        member = generate_fake_new_user()
        client = get_authed_client(member.name, 'fake_password')

        response = client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/brothers/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), 4)
        self.assertEqual(content[0]['shift']['title'], self.shift.title)
        self.assertEqual(content[0]['member']['name'], self.sbs[0].name)

    def test_add_brother_happy_path(self):
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

    def test_add_brother_fails_if_not_authed_user(self):
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

    def test_add_brother_fails_on_full_shift(self):
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

