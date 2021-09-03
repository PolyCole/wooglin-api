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

    def test_unauthed_shift_gets(self):
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

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'You do not have permission to perform this action.')

    def test_add_shift_staff(self):
        member = generate_fake_new_user(True)
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
        count_before = SoberBroShift.objects.count()

        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in content)
        self.assertEqual(content['title'], 'Test Shift')
        self.assertEqual(SoberBroShift.objects.count(), count_before + 1)

    def test_add_shift_improper_timestamps(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        timezone = pytz.timezone("America/Denver")
        now = datetime.datetime.now()
        now = timezone.localize(now)

        two_hours = datetime.timedelta(hours=2)
        one_day = datetime.timedelta(days=1)

        # First, lets try and create a shift for yesterday.
        data = {
            'date': now.date() - one_day,
            'time_start': now + two_hours,
            'time_end': now + two_hours + two_hours,
            'title': "Test Shift",
            'capacity': 5
        }
        count_before = SoberBroShift.objects.count()

        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SoberBroShift.objects.count(), count_before)
        self.assertTrue('date' in content)
        self.assertEqual(content['date'], "The date you've specified is in the past. Shifts in the past can only be "
                                          "created by an administrator.")

        # Second, lets try set our start time to be in the past.
        data = {
            'date': now.date(),
            'time_start': (now - one_day) - two_hours,
            'time_end': now + two_hours + two_hours,
            'title': "Test Shift",
            'capacity': 5
        }
        count_before = SoberBroShift.objects.count()

        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SoberBroShift.objects.count(), count_before)
        self.assertTrue('time_start' in content)
        self.assertTrue(content['time_start'], 'Your specified start time for the shift is in the past. Shifts in the '
                                               'past can only be altered by the administrator.')

        # Third, lets try set our end time to be in the past.
        data = {
            'date': now.date(),
            'time_start': now + two_hours,
            'time_end': (now - one_day) + two_hours + two_hours,
            'title': "Test Shift",
            'capacity': 5
        }
        count_before = SoberBroShift.objects.count()

        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SoberBroShift.objects.count(), count_before)
        self.assertTrue('time_end' in content)
        self.assertTrue(content['time_end'], 'Your specified end time for the shift is in the past. Shifts in the '
                                             'past can only be altered by the administrator.')

    def test_add_shift_improper_capacity(self):
        member = generate_fake_new_user(True)
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
            'capacity': 0
        }
        count_before = SoberBroShift.objects.count()

        response = client.post('/api/v1/sober-bro-shift/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(SoberBroShift.objects.count(), count_before)
        self.assertTrue('capacity' in content)
        self.assertEqual(content['capacity'], 'Capacity must be a positive integer.')

    def test_put_shift_doesnt_exist(self):
        member = generate_fake_new_user(True)
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

        response = client.put('/api/v1/sober-bro-shift/114/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in content)
        self.assertTrue(content['title'], 'Test Shift')

    def test_put_shift_does_exist(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        data = {
            'title': "Test Shift Edited",
            'capacity': 7
        }

        response = client.put('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('title' in content)
        self.assertTrue('capacity' in content)
        self.assertEqual(content['title'], 'Test Shift Edited')
        self.assertEqual(content['capacity'], 7)

    def test_patch_404(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        data = {
            'title': "Test Shift Edited",
            'capacity': 7
        }

        response = client.patch('/api/v1/sober-bro-shift/140/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'Not found.')

    def test_patch_improper_arguments(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        # First and foremost, negative capacity check.
        data = {
            'capacity': -1
        }

        before_value = self.shift.capacity

        response = client.patch('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('capacity' in content)
        self.assertEqual(content['capacity'], 'Capacity must be a positive integer.')
        self.assertEqual(SoberBroShift.objects.filter(id=self.shift.id)[0].capacity, before_value)

        # Secondly, let's check that SWEET date field, what if we try and put it in the past?
        now = datetime.datetime.now()
        timezone = pytz.timezone("America/Denver")
        now = timezone.localize(now)

        data = {
            'date': now.date() - datetime.timedelta(days=1)
        }

        before_value = self.shift.date

        response = client.patch('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('date' in content)
        self.assertEqual(content['date'], "The date you've specified is in the past. Shifts in the past can only be "
                                          "created by an administrator.")
        self.assertEqual(SoberBroShift.objects.filter(id=self.shift.id)[0].date, before_value)

        # Thirdly, how about that time_start field? What if it's in the past?
        data = {
            'time_start': now - datetime.timedelta(days=1)
        }

        before_value = self.shift.time_start

        response = client.patch('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('time_start' in content)
        self.assertEqual(content['time_start'], 'Your specified start time for the shift is in the past. Shifts in '
                                                'the past can only be altered by the administrator.')
        self.assertEqual(SoberBroShift.objects.filter(id=self.shift.id)[0].time_start, before_value)

        # Fourthly, how else can we break timestamps? Try and set the time_end field for the past.
        data = {
            'time_end': now - datetime.timedelta(days=1)
        }

        before_value = self.shift.time_end

        response = client.patch('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', data=data, format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('time_end' in content)
        self.assertEqual(content['time_end'],
                         "Your specified end time for the shift is in the past. Shifts in the past can "
                         "only be altered by the administrator. ")
        self.assertEqual(SoberBroShift.objects.filter(id=self.shift.id)[0].time_end, before_value)

    def test_delete_404(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        before_count = SoberBroShift.objects.count()
        response = client.delete('/api/v1/sober-bro-shift/12412/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('detail' in content)
        self.assertEqual(content['detail'], 'Not found.')
        self.assertEqual(SoberBroShift.objects.count(), before_count)

    def test_delete_happy_path(self):
        member = generate_fake_new_user(True)
        client = get_authed_client(member.name, 'fake_password')

        before_count = SoberBroShift.objects.count()
        response = client.delete('/api/v1/sober-bro-shift/' + str(self.shift.id) + '/', format='json')
        content = get_response_content(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SoberBroShift.objects.count(), before_count - 1)
        self.assertTrue('delete' in content)
        self.assertEqual(content['delete'], 'The Sober Bro Shift delete operation has completed successfully. Any '
                                            'members assigned to this shift have been removed as well.')
