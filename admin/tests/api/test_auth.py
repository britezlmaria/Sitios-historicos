def test_post_auth_401(client):
    response = client.post("/api/auth", json={"email": "otro@gmail.com", "password": "otro"})
    assert response.status_code == 401


def test_post_auth_201(client, create_user):
    user = create_user()
    response = client.post("/api/auth", json={"email": "test@gmail.com", "password": "test123"})
    assert response.status_code == 201
    assert "Set-Cookie" in response.headers
