import requests


def test_get_post():
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    assert response.status_code == 200
    json_data = response.json()
    for field in ["id", "title", "body"]:
        assert field in json_data
    assert json_data["id"] == 1


def test_post():
    url = "https://jsonplaceholder.typicode.com/posts/"
    data = {
        "id": 32,
        "title": "test post api request",
        "body": "test post api request body",
    }
    response = requests.post(url, json=data)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["id"] is not None
    for field in ["title", "body"]:
        assert json_data[field] == data[field]


def test_put():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    new_data = {
        "title": "test put api request title",
        "body": "test put api request body",
    }
    response = requests.put(url, json=new_data)
    assert response.status_code == 200
    json_data = response.json()
    for field in ["title", "body"]:
        assert json_data[field] == new_data[field]


def test_delete():
    url = "https://jsonplaceholder.typicode.com/posts/1"
    response = requests.delete(url)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data == {}
