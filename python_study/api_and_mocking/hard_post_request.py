import requests

def create_secure_user():
    url = "https://httpbin.org/post"
    headers = {
        'Authorization':"Bearer SUPER_SECRET_TOKEN_2026"
    }
    user_data = {
        "name": "Illia",
        "role": "Business Analyst",
        "skills": ["Python", "Playwright", "API"]
    }
    response = requests.post(url, headers=headers, json=user_data)
    assert response.status_code == 200
    print(response.json())


if __name__ == "__main__":
    create_secure_user()