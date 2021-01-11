import json
import random

from django.contrib.auth.models import User
from faker import Faker
from rest_framework.test import APIClient

from restapi.models.members import Member


def get_tokens(username, password=""):
    url = '/api/token/'
    data = {'username': str(username), 'password': str(password)}
    client = APIClient()
    response = client.post(url, data, format='json')
    response.render()
    content = json.loads(response.content)
    return content


def get_authed_client(username, password):
    token = get_tokens(username, password)['access']
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token))
    return client


def generate_fake_new_user(is_staff=False):
    fake = Faker()

    name = fake.name()
    email = fake.email()
    phone = get_phone()

    # Ensuring we don't have an accidental collision in the db.
    # Super rare probabilistically, but still.
    while Member.objects.filter(phone=phone).count() != 0:
        phone = get_phone()

    while Member.objects.filter(name=name).count() != 0:
        name = fake.name()

    user_account = User.objects.create_user(
        name,
        email,
        "fake_password",
        is_staff=is_staff
    )

    member = Member.objects.create(
        user=user_account,
        name=name,
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        legal_name=name,
        address=fake.address(),
        email=email,
        phone=get_phone(),
        rollnumber=Member.objects.count() + 1,
        member_score=random.randint(0,100),
        inactive_flag=False,
        abroad_flag=False,
        present=random.randint(0, 50),
        position="Test Member"
    )

    return member


# Generates a random phone number of a standard xxx.xxx.xxxx format.
def get_phone():
    random.seed()
    number = ""
    for x in range(0, 2):
        number += str(random.randint(0, 1000))
        number += "."
    number += str(random.randint(0, 10000))
    return number


# Resolves the given response and returns its content.
def get_response_content(response):
    response.render()
    return json.loads(response.content)


# Takes a string and returns the string in url-format.
def urlify(in_string, in_string_length):
    return in_string[:in_string_length].replace(' ', '%20')


