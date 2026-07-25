import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


def is_valid_email(email):
    """
    Perform basic email-format validation.
    """

    email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return re.match(
        email_pattern,
        email,
    ) is not None


def is_safe_redirect_url(target):
    """
    Prevent redirects to unsafe external websites.
    """

    if not target:
        return False

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(
        urljoin(request.host_url, target)
    )

    return (
        redirect_url.scheme in {"http", "https"}
        and host_url.netloc == redirect_url.netloc
    )


def validate_registration_form(
    full_name,
    email,
    password,
    confirm_password,
):
    """
    Validate registration form data.
    """

    if not full_name:
        return "Please enter your full name."

    if len(full_name) < 3:
        return "Your full name must contain at least 3 characters."

    if len(full_name) > 120:
        return "Your full name is too long."

    if not email:
        return "Please enter your email address."

    if not is_valid_email(email):
        return "Please enter a valid email address."

    if not password:
        return "Please create a password."

    if len(password) < 8:
        return "Your password must contain at least 8 characters."

    if not any(character.isupper() for character in password):
        return "Your password must contain an uppercase letter."

    if not any(character.islower() for character in password):
        return "Your password must contain a lowercase letter."

    if not any(character.isdigit() for character in password):
        return "Your password must contain a number."

    if password != confirm_password:
        return "The password confirmation does not match."

    return None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Create a new user account.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":
        full_name = request.form.get(
            "full_name",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        validation_error = validate_registration_form(
            full_name,
            email,
            password,
            confirm_password,
        )

        if validation_error:
            flash(
                validation_error,
                "error",
            )

            return render_template(
                "auth/register.html",
                full_name=full_name,
                email=email,
            )

        existing_user = db.session.execute(
            db.select(User).where(
                User.email == email
            )
        ).scalar_one_or_none()

        if existing_user:
            flash(
                "An account already exists with this email address.",
                "error",
            )

            return render_template(
                "auth/register.html",
                full_name=full_name,
                email=email,
            )

        new_user = User(
            full_name=full_name,
            email=email,
        )

        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()

        except Exception:
            db.session.rollback()

            flash(
                "The account could not be created. Please try again.",
                "error",
            )

            return render_template(
                "auth/register.html",
                full_name=full_name,
                email=email,
            )

        flash(
            "Your account was created successfully. You can now log in.",
            "success",
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Authenticate a registered user.
    """

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":
        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        remember_me = request.form.get(
            "remember_me"
        ) == "on"

        if not email or not password:
            flash(
                "Please enter both your email and password.",
                "error",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        user = db.session.execute(
            db.select(User).where(
                User.email == email
            )
        ).scalar_one_or_none()

        if user is None or not user.check_password(password):
            flash(
                "The email or password is incorrect.",
                "error",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        if not user.is_active_account:
            flash(
                "This account has been disabled.",
                "error",
            )

            return render_template(
                "auth/login.html",
                email=email,
            )

        login_user(
            user,
            remember=remember_me,
        )

        user.last_login = datetime.now(timezone.utc)

        try:
            db.session.commit()

        except Exception:
            db.session.rollback()

        flash(
            f"Welcome back, {user.full_name}.",
            "success",
        )

        next_page = request.args.get("next")

        if next_page and is_safe_redirect_url(next_page):
            return redirect(next_page)

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Log out the current user.
    """

    if current_user.is_authenticated:
        logout_user()

        flash(
            "You have been logged out successfully.",
            "success",
        )

    return redirect(
        url_for("main.home")
    )