from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """
    Stores registered PhishGuard users.
    """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    full_name = db.Column(
        db.String(120),
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_login = db.Column(
        db.DateTime,
        nullable=True,
    )

    is_active_account = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    scans = db.relationship(
        "ScanHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, password):
        """
        Convert a plain password into a secure password hash.
        """

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check whether a submitted password is correct.
        """

        return check_password_hash(
            self.password_hash,
            password,
        )

    @property
    def is_active(self):
        """
        Tell Flask-Login whether this account is active.
        """

        return self.is_active_account

    def __repr__(self):
        return f"<User {self.email}>"