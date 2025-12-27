import pytest


def test_get_site_id_404(client):
    response = client.get("/api/sites/1")
    assert response.status_code == 404


def test_get_site_id_200(client, create_site):
    site = create_site()
    response = client.get("/api/sites/1")
    assert response.status_code == 200
    assert response.json == site.to_dict()


def test_post_sites_not_authenticated(client):
    response = client.post("/api/sites")
    assert response.status_code == 401


def test_post_sites_authenticated(client, create_user, create_tags, auth_headers):
    user = create_user()
    create_tags()
    headers = auth_headers(user=user)
    site_data = {
        "name": "Test Site",
        "short_description": "Short desc",
        "description": "Full desc",
        "city": "Ciudad",
        "province": "Provincia",
        "lat": -31.42,
        "long": -64.18,
        "tags": ["Educativo"],
        "state_of_conservation": "Bueno",
        "inauguration_year": 1990
    }
    response = client.post("/api/sites", json=site_data, headers=headers)
    assert response.status_code == 201
    assert response.json["user_id"] == user.id


@pytest.mark.parametrize("page,per_page", [(1, 100)])
def test_get_sites_empty(client, page, per_page):
    endpoint = f"/api/sites?page={page}&per_page={per_page}"
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json["data"] == []
    assert response.json["_meta"] == {
        "page": page,
        "per_page": per_page,
        "total_pages": 0,
        "total_items": 0,
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": endpoint
    }


@pytest.mark.parametrize("page,per_page", [(1, 10)])
def test_get_sites_not_empty(client, create_site, create_user, page, per_page):
    # Crear un sitio histórico de prueba
    user = create_user()
    site = create_site(user=user)
    endpoint = f"/api/sites?page={page}&per_page={per_page}"
    response = client.get(endpoint)
    assert response.status_code == 200
    assert response.json["data"] == [site.to_dict()]
    assert response.json["_meta"] == {
        "page": 1,
        "per_page": 10,
        "total_items": 1,
        "total_pages": 1
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": endpoint
    }


@pytest.mark.parametrize("lat,long,per_page", [(200, 400, 200)])
def test_get_sites_invalid_params(client, lat, long, per_page):
    endpoint = f"/api/sites?lat={lat}&long={long}&per_page={per_page}"
    response = client.get(endpoint)
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"]["code"] == "invalid_query"
    assert "lat" in response.json["error"]["details"]
    assert "long" in response.json["error"]["details"]
    assert "per_page" in response.json["error"]["details"]
