from collections.abc import Callable

import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from core.auth import repository as user_repo
from core.auth.models import User
from core.database import db
from core.historic_site import repository as historic_repo
from core.historic_site.models import HistoricSite
from core.reviews import repository as review_repo
from core.reviews.models import Review, ReviewState
from core.tags import repository as tags_repo
from web import create_app


@pytest.fixture(scope="session", autouse=True)
def check_database_connection():
    """Verifica que la base de datos esté corriendo antes de ejecutar los tests."""
    app = create_app(env="testing")

    with app.app_context():
        try:
            # Intentamos una consulta mínima
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except OperationalError:
            pytest.exit(
                "\n\n❌ No se pudo conectar a la base de datos.\n"
                "👉 Asegúrate de tener el contenedor de PostgreSQL corriendo.\n"
                "   Ejecutá:\n"
                "       docker compose up -d\n\n",
                returncode=1,
            )


@pytest.fixture(scope="session")
def app():
    app = create_app(env="testing")
    app.testing = True
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


@pytest.fixture(scope="function")
def client(app):
    db.create_all()
    yield app.test_client()
    db.session.remove()
    db.drop_all()


@pytest.fixture
def create_tags() -> Callable[..., None]:
    def _create_tags():
        tags_repo.create_tag(name="SitioTuristico")
        tags_repo.create_tag(name="Museo")
        tags_repo.create_tag(name="Educativo")
        tags_repo.create_tag(name="Clásico")

    return _create_tags


@pytest.fixture
def create_user() -> Callable[..., User]:
    def _create_user(
            email: str = "test@gmail.com",
            password: str = "test123",
            name: str = "Juan",
            last_name: str = "Pérez",
    ) -> User:
        """Crea y retorna un usuario persistido en la base de datos."""
        admin_role = user_repo.create_role(name="admin")
        return user_repo.create_user(
            email=email,
            name=name,
            last_name=last_name,
            password=password,
            enabled=True,
            system_admin=False,
            id_role=admin_role.id_role,
            deleted=False,
        )

    return _create_user


@pytest.fixture
def create_site(create_user) -> Callable[..., HistoricSite]:
    def _create_site(
            user: User = None,
            name: str = "Palacio de la Legislatura de la Provincia de Buenos Aires",
            short_description: str = "Sede del Poder Legislativo de la Provincia de Buenos Aires",
            description: str = "El Palacio de la Legislatura de la Provincia de Buenos Aires es un edificio emblemático...",
            city: str = "La Plata",
            province: str = "Buenos Aires",
            lat: float = -34.9226,
            long: float = -57.9561,
            state_of_conservation: str = "bueno",
    ) -> HistoricSite:
        """Crea y retorna un sitio histórico, asociado al usuario dado."""
        location = WKTElement(f"POINT({long} {lat})", srid=4326)

        if not user:
            user = create_user()

        return historic_repo.create_historic_site(
            user_id=user.id,
            name=name,
            short_description=short_description,
            description=description,
            city=city,
            province=province,
            location=location,
            state_of_conservation=state_of_conservation,
            inauguration_year=1898,
            visible=True,
            category=[],
            tags=[],
        )

    return _create_site


@pytest.fixture
def create_review(create_user, create_site) -> Callable[..., Review]:
    def _create_review(
            user: User = None,
            site: HistoricSite = None,
            state: ReviewState = ReviewState.APPROVED,
            rating: int = 5,
            comment: str = "Great place!",
    ) -> Review:
        """Crea y retorna una review para un sitio y usuario determinados."""
        if not user:
            user = create_user()
        if not site:
            site = create_site(user=user)

        review = review_repo.create_review(
            user_id=user.id,
            site_id=site.id,
            rating=rating,
            comment=comment,
        )
        review.state = state
        return review

    return _create_review


@pytest.fixture
def auth_headers(client, create_user) -> Callable[..., dict[str, str]]:
    def _auth_headers(user: User = None, password: str = None) -> dict[str, str]:
        """Devuelve los headers de autenticación (JWT Cookie)."""

        if not user:
            user = create_user()

        response = client.post("/api/auth", json={"email": user.email, "password": password or "test123"})
        assert response.status_code == 201
        cookie = response.headers.get("Set-Cookie")
        return {"Cookie": cookie}

    return _auth_headers
