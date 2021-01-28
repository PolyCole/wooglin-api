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

    def test_unathed_shift_gets(self):
        response = self.client.get('/api/v1/sober-bro-shift/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', format='json')
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

    def test_add_shift_not_staff(self):
        member = generate_fake_new_user(False)
        client = get_authed_client(member.name, 'fake_password')

        timezone = pytz.timezone("America/Denver")
        now = datetime.datetime.now()
        now = timezone.localize(now)

        two_hours = datetime.timedelta(hours=2)

        data = {
            'date': now.date(),
            'time_start': now + two_hours,
            'time_end': now + two_hours + two_hours,
            'title': "Test Shift",
            'capacity': 5
        }
        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        print(content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
