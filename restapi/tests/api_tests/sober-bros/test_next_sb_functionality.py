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
            time_end=(now + two_hours),
            capacity=5
        )

        sbs = list()

        for member in four_members:
            sbs.append(SoberBro.objects.create(
                shift=shift,
                member=member
            ))

        self.shift = shift

    def test_get_next_sb_shift(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        timezone = pytz.timezone("America/Denver")
        now = datetime.datetime.now()
        now = timezone.localize(now)

        five_minutes = datetime.timedelta(minutes=5)
        two_hours = datetime.timedelta(hours=2)

        shift = SoberBroShift.objects.create(
            date=now.date(),
            time_start=now + five_minutes,
            time_end=now + two_hours,
            title="Test Shift",
            capacity=5
        )

        link = SoberBro.objects.create(
            shift=shift,
            member=member
        )

        response = client.get('/api/v1/next-sb-shift/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content), 1)

        self.assertEqual(content[0]["title"], "Test Shift")
        self.assertTrue('date' in content[0])

        self.assertEqual(len(content[0]["brothers"]), 1)
        brother = content[0]["brothers"][0]
        self.assertEqual(brother["name"], member.name)
        self.assertEqual(brother["phone"], member.phone)

    def test_get_next_sb_shift_no_shifts(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        response = client.get('/api/v1/next-sb-shift/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("no_shifts" in content)

    def test_unauthed_get_next_sb_shift(self):
        response = self.client.get('/api/v1/next-sb-shift/', format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
