from core.reviews.models import ReviewState


def test_get_all_site_reviews_unauthorized(client, create_site):
    create_site()
    response = client.get("/api/sites/1/reviews")
    assert response.status_code == 401


def test_get_all_site_reviews_site_not_found(client, create_user, auth_headers):
    headers = auth_headers()
    response = client.get("/api/sites/1/reviews", headers=headers)
    assert response.status_code == 404


def test_get_all_site_reviews_empty(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    site = create_site(user=user)
    create_review(user=user, site=site, state=ReviewState.PENDING)
    headers = auth_headers(user=user)
    response = client.get("/api/sites/1/reviews", headers=headers)
    assert response.status_code == 200
    assert response.json["data"] == []
    assert response.json["_meta"] == {
        "page": 1,
        "per_page": 10,
        "total_pages": 0,
        "total_items": 0,
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": "/api/sites/1/reviews?page=1&per_page=10"
    }


def test_get_all_site_reviews_200(client, create_review, auth_headers, create_user, create_site):
    user = create_user()
    site = create_site(user=user)
    review = create_review(user=user, site=site)
    headers = auth_headers(user=user)
    response = client.get("/api/sites/1/reviews", headers=headers)
    assert response.status_code == 200
    assert response.json["data"] == [review.to_dict()]
    assert response.json["_meta"] == {
        "page": 1,
        "per_page": 10,
        "total_pages": 1,
        "total_items": 1,
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": "/api/sites/1/reviews?page=1&per_page=10"
    }


def test_create_review_unauthorized(client, create_site):
    create_site()
    review_data = {
        "historic_site_id": 1,
        "rating": 5,
        "comment": "Amazing place!"
    }
    response = client.post("/api/sites/1/reviews", json=review_data)
    assert response.status_code == 401


def test_create_review_site_not_found(client, auth_headers):
    headers = auth_headers()
    review_data = {
        "historic_site_id": 1,
        "rating": 5,
        "comment": "Amazing place!"
    }
    response = client.post("/api/sites/1/reviews", json=review_data, headers=headers)
    assert response.status_code == 404


def test_create_review_400_missing_fields(client, create_site, auth_headers, create_user):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)
    review_data = {
        # "historic_site_id" is missing
        "rating": 5,
        "comment": "Amazing place!"
    }
    response = client.post(f"/api/sites/{site.id}/reviews", json=review_data, headers=headers)
    assert response.status_code == 400
    assert "historic_site_id" in response.json["error"]["details"]


def test_create_review_400_invalid_rating(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)
    review_data = {
        "historic_site_id": site.id,
        "rating": 6,  # Invalid rating, should be between 1 and 5
        "comment": "Amazing place!"
    }
    response = client.post(f"/api/sites/{site.id}/reviews", json=review_data, headers=headers)
    assert response.status_code == 400


def test_create_review_returns_503_when_reviews_disabled(client, auth_headers, monkeypatch):
    headers = auth_headers()  # usuario autenticado

    # Simular ValueError dentro del try (como el except del método)
    def fake_is_flag_enabled(_):
        return False

    monkeypatch.setattr("core.feature_flags.repository.is_flag_enabled", fake_is_flag_enabled)

    response = client.post(
        "/api/sites/1/reviews",
        json={"historic_site_id": 1, "rating": 5, "comment": "test"},
        headers=headers
    )

    assert response.status_code == 503

    data = response.get_json()
    assert data["error"]["code"] == "service_unavailable"
    assert data["error"]["message"] == "The reviews are temporary disabled"


def test_create_review_201(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)
    review_data = {
        "historic_site_id": site.id,
        "rating": 5,
        "comment": "Amazing place!"
    }

    response = client.post(f"/api/sites/{site.id}/reviews", json=review_data, headers=headers)
    print(response.json)
    assert response.status_code == 201
    assert response.json["rating"] == review_data["rating"]
    assert response.json["comment"] == review_data["comment"]
    assert response.json["user_id"] == user.id
    assert len(site.reviews) == 1
    assert response.json["id"] == site.reviews[0].id


def test_get_site_review_401(client, create_site):
    site = create_site()
    response = client.get(f"/api/sites/{site.id}/reviews/1")
    assert response.status_code == 401


def test_get_site_review_403(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    site = create_site(user=user)
    review = create_review(user=user, site=site, state=ReviewState.PENDING)
    headers = auth_headers(user=user)

    response = client.get(f"/api/sites/{site.id}/reviews/{review.id}", headers=headers)
    assert response.status_code == 403

def test_get_site_review_404_review(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)

    response = client.get(f"/api/sites/{site.id}/reviews/1", headers=headers)
    assert response.status_code == 404
    assert "Review not found" in response.json["error"]["message"]

def test_get_site_review_404_site(client, create_user, create_site, auth_headers):
    headers = auth_headers()
    response = client.get(f"/api/sites/1/reviews/1", headers=headers)
    assert response.status_code == 404
    assert "Site not found" in response.json["error"]["message"]

def test_get_site_review_200(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    site = create_site(user=user)
    review = create_review(user=user, site=site)
    headers = auth_headers(user=user)

    response = client.get(f"/api/sites/{site.id}/reviews/{review.id}", headers=headers)
    assert response.status_code == 200
    assert response.json == review.to_dict()


def test_remove_site_review_401(client, create_site):
    site = create_site()
    response = client.delete(f"/api/sites/{site.id}/reviews/1")
    assert response.status_code == 401


def test_remove_site_review_403(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    site = create_site(user=user)
    review = create_review(user=user, site=site, state=ReviewState.PENDING)
    headers = auth_headers(user=user)

    response = client.delete(f"/api/sites/{site.id}/reviews/{review.id}", headers=headers)
    assert response.status_code == 403


def test_remove_site_review_404_review(client, create_user, create_site, auth_headers):
    user = create_user()
    site = create_site(user=user)
    headers = auth_headers(user=user)

    response = client.delete(f"/api/sites/{site.id}/reviews/1", headers=headers)
    assert response.status_code == 404
    assert "Review not found" in response.json["error"]["message"]


def test_remove_site_review_404_site(client, create_user, create_site, auth_headers):
    headers = auth_headers()
    response = client.delete(f"/api/sites/1/reviews/1", headers=headers)
    assert response.status_code == 404
    assert "Site not found" in response.json["error"]["message"]


def test_remove_site_reviews_returns_503_when_reviews_disabled(client, auth_headers, monkeypatch):
    headers = auth_headers()  # usuario autenticado

    # Simular ValueError dentro del try (como el except del método)
    def fake_is_flag_enabled(_):
        return False

    monkeypatch.setattr("core.feature_flags.repository.is_flag_enabled", fake_is_flag_enabled)

    response = client.delete(
        "/api/sites/1/reviews/1",
        headers=headers
    )

    assert response.status_code == 503

    data = response.get_json()
    assert data["error"]["code"] == "service_unavailable"
    assert data["error"]["message"] == "The reviews are temporary disabled"


def test_remove_site_review_204(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    site = create_site(user=user)
    review = create_review(user=user, site=site)
    headers = auth_headers(user=user)

    response = client.delete(f"/api/sites/{site.id}/reviews/{review.id}", headers=headers)
    assert response.status_code == 204
    assert len(site.reviews) == 1
    assert site.reviews[0].deleted == True


def test_get_my_reviews_unauthorized(client):
    response = client.get("/api/me/reviews")
    assert response.status_code == 401


def test_get_my_reviews_empty(client, create_user, create_review, auth_headers):
    user = create_user()
    headers = auth_headers(user=user)

    # Crear una review de OTRO usuario para garantizar filtrado
    other_user = create_user(email="other@example.com")
    create_review(user=other_user)

    response = client.get("/api/me/reviews", headers=headers)
    assert response.status_code == 200

    assert response.json["data"] == []
    assert response.json["_meta"] == {
        "page": 1,
        "per_page": 10,
        "total_pages": 0,
        "total_items": 0
    }
    assert response.json["_links"] == {
        "prev": None,
        "next": None,
        "self": "/api/me/reviews?page=1&per_page=10"
    }


def test_list_reviews_of_user_returns_only_user_approved_reviews(
    client, create_user, create_site, create_review, auth_headers
):
    user = create_user()
    headers = auth_headers(user=user)

    site = create_site(user=user)

    # Reviews aprobadas del usuario
    r1 = create_review(user=user, site=site)
    r2 = create_review(user=user, site=site)

    # Review NO aprobada
    create_review(user=user, site=site, state=ReviewState.PENDING)

    # Review aprobada pero de otro usuario
    other_user = create_user(email="other@gmail.com")
    create_review(user=other_user, site=site)

    response = client.get(
        "/api/me/reviews",
        headers=headers
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["_meta"]["total_items"] == 2
    assert len(data["data"]) == 2
    ids = {item["id"] for item in data["data"]}
    assert ids == {r1.id, r2.id}



def test_list_reviews_of_user_pagination(
    client, create_user, create_site, create_review, auth_headers
):
    user = create_user()
    headers = auth_headers(user=user)
    site = create_site(user=user)

    reviews = [
        create_review(user=user, site=site)
        for _ in range(15)
    ]

    # page=1, per_page=10
    response = client.get("/api/me/reviews?page=1&per_page=10", headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["data"]) == 10
    assert data["_meta"]["total_items"] == 15
    assert data["_meta"]["page"] == 1
    assert data["_meta"]["per_page"] == 10

    # page=2, per_page=10
    response = client.get("/api/me/reviews?page=2&per_page=10", headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["data"]) == 5
    assert data["_meta"]["page"] == 2


def test_get_my_reviews_filters_deleted(client, create_user, create_site, create_review, auth_headers):
    user = create_user()
    headers = auth_headers(user=user)
    site = create_site(user=user)

    # Review válida
    r1 = create_review(user=user, site=site)

    # Review soft-deleted
    r2 = create_review(user=user, site=site)
    r2.deleted = True

    response = client.get("/api/me/reviews", headers=headers)
    assert response.status_code == 200

    assert response.json["data"] == [r1.to_dict()]  # Solo la no eliminada
    assert response.json["_meta"]["total_items"] == 1


def test_get_my_reviews_internal_error(client, create_user, auth_headers, monkeypatch):
    user = create_user()
    headers = auth_headers(user=user)

    # Simular ValueError dentro del try (como el except del método)
    def fake_get_user(_):
        raise ValueError()

    monkeypatch.setattr("core.auth.repository.get_user", fake_get_user)

    response = client.get("/api/me/reviews", headers=headers)
    assert response.status_code == 500
    assert response.json["error"]["code"] == "server_error"
