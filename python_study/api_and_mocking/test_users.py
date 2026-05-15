import requests
import pytest
from fake_useragent import FakeUserAgent

# def test_create_new_user():
#     url = "https://jsonplaceholder.typicode.com/users"
#     headers = {
#         'User-Agent': FakeUserAgent().random,
#     }
#     payload = {
#         "name": "bob",
#         "two": "three"
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     status = response.status_code
#     assert status == 201
#     data = response.json()
#     assert data["name"] == "bob"
#     assert data["two"] == "three"
#     assert 'id' in data

@pytest.mark.parametrize("user_id, expected_name", [
    (1, "Leanne Graham"),
    (2, "Ervin Howell"),
    (5, "Chelsey Dietrich"),
    (8, "Nicholas Runolfsdottir V")
])

def test_find_specific_user(user_id, expected_name):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"

    response = requests.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == expected_name


def test_user_not_found():
    url = "https://jsonplaceholder.typicode.com/users/9999"
    response = requests.get(url)
    assert response.status_code == 404
    assert response.json() == {}


def test_user_update():
    url = "https://jsonplaceholder.typicode.com/users/1"
    headers = {
        "User-Agent": FakeUserAgent().random,
    }
    payload = {
        "id": 1,
        "name": "bob",
        "email": "qwerty@il.com"
    }
    response = requests.put(url, json=payload, headers = headers)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'bob'


def test_delete_user():
    url = "https://jsonplaceholder.typicode.com/users/1"
    response = requests.delete(url)
    assert response.status_code == 200
    data = response.json()
    assert data == {}
