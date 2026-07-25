from app import create_app
from app.extensions import db


app = create_app()


def create_database():
    """
    Create database tables if they do not already exist.
    """

    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_database()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )