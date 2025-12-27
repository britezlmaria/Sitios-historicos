from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    return db


def reset_db():
    print("Resetting database...")
    db.metadata.drop_all(bind=db.engine)
    db.metadata.create_all(bind=db.engine)
    print("Database reset complete.")
