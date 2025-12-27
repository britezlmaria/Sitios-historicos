import pytest

def test_update_user_with_all_data(client, create_user, auth_headers):
    user = create_user()
    headers = auth_headers(user=user)

    user_data = {
        "name": "NuevoNombre",
        "last_name": "NuevoApellido",
        "avatar": "NuevaFoto"
    }
    response = client.put("/api/me", json=user_data, headers=headers)

    assert response.status_code == 201
    assert user.name == "NuevoNombre"
    assert user.last_name == "NuevoApellido"
    assert user.avatar == "NuevaFoto"

def test_update_user_only_name(client, create_user, auth_headers):
    user = create_user()
    headers = auth_headers(user=user)

    user_data = {
        "name": "NuevoNombre"
    }
    response = client.put("/api/me", json=user_data, headers=headers)

    assert response.status_code == 201
    assert user.name == "NuevoNombre"
    assert user.last_name == "Pérez"
    assert user.avatar is None