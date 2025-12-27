from datetime import timezone, datetime, timedelta

from flask import Flask, render_template, session
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity, set_access_cookies
from flask_cors import CORS
from core import database, seeds
from core.auth import repository
from core.encription import bcrypt
from flask_session import Session
from web.storage import storage
from .api.auth_google import auth_google_bp

from .api.routes import bp as api_bp
from .controllers.auth import auth_bp
from .controllers.feature_flags import feature_flags_bp
from .controllers.historic_site import historic_site_bp
from .controllers.tags import tags_bp
from .controllers.users import user_bp
from .controllers.reviews import reviews_bp
from .handlers.error import error_401, error_404, error_500

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(f"web.config.{env.capitalize()}Config")
    app.config.update(
        SESSION_COOKIE_SAMESITE=app.config.get("JWT_COOKIE_SAMESITE", "Lax"),
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
    )
    Session(app)
    bcrypt.init_app(app)
    database.init_app(app)
    JWTManager(app)
    storage.init_app(app)
    if not app.config["TESTING"]:
        # Definimos los orígenes permitidos hardcodeados para desarrollo local
        # más lo que venga en el entorno
        allowed_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            app.config.get("FRONTEND_ORIGIN")
        ]
        
        # Filtramos para quitar duplicados o valores nulos
        allowed_origins = list(set([origin for origin in allowed_origins if origin]))

        # Habilitamos CORS para todas las rutas (/api/* es lo crítico, pero global está bien para dev)
        CORS(app, supports_credentials=True, origins=allowed_origins)
    # if not app.config["TESTING"]:
    #     CORS(app, supports_credentials=True, origins=[app.config.get("FRONTEND_ORIGIN")])
    # if not app.config["TESTING"]:
    #     cfg_origin = app.config.get("FRONTEND_ORIGIN")
    #     if isinstance(cfg_origin, (list, tuple)):
    #         origins = list(cfg_origin)
    #     elif cfg_origin:
    #         origins = [cfg_origin]
    #     else:
    #         origins = []

    #     if "http://127.0.0.1:5173" not in origins:
    #         origins.append("http://127.0.0.1:5173")
    #     if "http://localhost:5173" not in origins:
    #         origins.append("http://localhost:5173")

    #     CORS(app, supports_credentials=True, origins=origins)

    @app.route("/")
    def home():
        user = None
        if session.get("user_id"):
            user = repository.get_user(session["user_id"])

        return render_template("home.html", user=user)

    @app.route("/protected")
    def protected():
        return (
            render_template(
                "error.html",
                number=401,
                name="No autorizado",
                description="No tienes permisos para acceder a esta página.",
            ),
            401,
        )

    @app.route("/server_error")
    def server_error():
        return (
            render_template(
                "error.html",
                number=500,
                name="Error interno del servidor",
                description="Ocurrió un error inesperado en el servidor.",
            ),
            500,
        )

    @app.route("/not_found")
    def not_found():
        return (
            render_template(
                "error.html",
                number=404,
                name="No encontrado",
                description="La página que estás buscando no existe.",
            ),
            404,
        )

    @app.cli.command("reset-db")
    def reset_db():
        database.reset_db()

    @app.cli.command("seed-db")
    def seed_db():
        print("Seeding database...")
        seeds.run()
        print("Database seeding complete.")

    @app.after_request
    def refresh_expiring_jwts(response):
        """Actualiza el token JWT si está a 30 minutos de expirar."""
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            return response



    app.register_blueprint(auth_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(feature_flags_bp)
    app.register_blueprint(historic_site_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_google_bp)
    app.register_error_handler(401, error_401)
    app.register_error_handler(500, error_500)
    app.register_error_handler(404, error_404)

    return app
