import json
from rest_framework.test import APIClient


def get_tokens(username, password=""):
    url = '/api/token/'
    data = {'username': str(username), 'password': str(password)}
    client = APIClient()
    response = client.post(url, data, format='json')
    response.render()
    content = json.loads(response.content)
    return content
