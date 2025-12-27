import pytest


def test_put_site_favorite_404(client, create_user, auth_headers):
    headers = auth_headers()
    response = client.put("/api/sites/1/favorite", headers=headers)
    assert response.status_code == 404


def test_put_site_favorite_204(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)
    response = client.put("/api/sites/1/favorite", headers=headers)
    assert response.status_code == 204
    assert site in user.favorites


def test_delete_site_favorite_404(client, create_user, auth_headers):
    headers = auth_headers()
    response = client.delete("/api/sites/1/favorite", headers=headers)
    assert response.status_code == 404


def test_delete_site_favorite_204(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    user.favorites.append(site)
    headers = auth_headers(user=user)
    response = client.delete("/api/sites/1/favorite", headers=headers)
    assert response.status_code == 204
    assert site not in user.favorites


@pytest.mark.parametrize("page,per_page", [(1, 100)])
def test_get_favorite_sites_empty(client, create_user, create_site, auth_headers, page, per_page):
    headers = auth_headers()
    endpoint = f"/api/me/favorites?page={page}&per_page={per_page}"
    response = client.get(endpoint, headers=headers)
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


@pytest.mark.parametrize("page,per_page", [(1, 100)])
def test_get_favorite_sites(client, create_user, create_site, auth_headers, page, per_page):
    user = create_user()
    site = create_site(user=user)
    user.favorites.append(site)
    headers = auth_headers(user=user)
    endpoint = f"/api/me/favorites?page={page}&per_page={per_page}"
    response = client.get(endpoint, headers=headers)
    assert response.status_code == 200
    assert response.json["data"] == [site.to_dict()]
    assert response.json["_meta"] == {
        "page": page,
        "per_page": per_page,
        "total_pages": 1,
        "total_items": 1,
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": endpoint
    }
