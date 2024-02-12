import functools
import re
import uuid

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from org_chart_maker.db import get_db
from org_chart_maker.emails import MailServer
from org_chart_maker.utils import register_new_users_allowed

bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

def isValidUsername(username):
    """Check if the given user name is valid."""

    pattern = "[a-zA-Z0-9_-]*"
    isValid = re.fullmatch(pattern, username)

    return isValid

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """

    # Re-route if not allowed.
    if not register_new_users_allowed():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        # Check username is valid.
        if not isValidUsername(username):
            error = "Username is invalid."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password, email) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), email),
                )
                db.commit()
            except db.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {username} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        # flash(error)

        # Use secure error message.
        flash("Incorrect username or password.")

    # Pass flag to template.
    g.allow_register_new_users = register_new_users_allowed()

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))

# @bp.route("/forgot-password", methods=("GET", "POST"))
@bp.route("/forgot-password", methods=("GET",))
def forgotPassword():
    """Allow the user to send a 'reset password' link."""

    # if request.method == "POST":
    #     # Look up database record.
    #     username = request.form["username"]
    #     email = request.form["email"]
    #     db = get_db()
    #     error = None
    #     user = db.execute(
    #         "SELECT * FROM user WHERE username = ?", (username,)
    #     ).fetchone()
    #
    #     # Check entered email matches database record. This is a basic
    #     # security measure to avoid spamming.
    #     if user is None:
    #         error = "Username does not exist."
    #     elif not user["email"] == email:
    #         error = "Incorrect email for username."
    #
    #     if error is None:
    #         # store the user id in a new session and return to the index
    #         # session.clear()
    #         # session["user_id"] = user["id"]
    #         # return redirect(url_for("index"))
    #         flash("Sending email...")
    #         MailServer().sendPasswordResetEmail()
    #     else:
    #         flash(error)

    return render_template("auth/forgot-password.html")

@bp.route("/create-reset-password-link", methods=("POST",))
def createResetPasswordLink():
    """Create a 'reset password' link."""

    # Debug.
    print ("Creating password reset link...")

    # Look up user in database.
    username = request.form["username"]
    email = request.form["email"]
    db = get_db()
    error = None
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()

    # Check entered email matches database record. This is a basic
    # security measure to avoid spamming.
    if user is None:
        error = "Username does not exist."
    elif not user["email"] == email:
        error = "Incorrect email for username."

    if error is None:
        # flash("Sending email...")
        # MailServer().sendPasswordResetEmail()
        pass
    else:
        # flash(error)
        content = {"status": "Error", "problem": error}
        return jsonify(content)

    # Create the database record.
    link = str(uuid.uuid4())
    db = get_db()
    db.execute(
        "INSERT INTO password_reset_link (user_id, link, created_date, expiry_date, status) VALUES (?, ?, date('now'), date('now', '+2 days'), ?)",
        (user["id"], link, "sent")
    )
    db.commit()

    # Return output.
    content = {"status": "OK", "link": link}
    return jsonify(content)

@bp.route("/reset-password", methods=("GET",))
def resetPassword():
    """Show the page to enter a new password."""

    # Look up link in database.
    link = request.args.get('link')
    error = None
    db = get_db()
    db_record = db.execute(
        "SELECT * FROM password_reset_link WHERE link = ?", (link,)
    ).fetchone()

    if db_record is None:
        error = "Invalid link."
        # TODO: Show this and disable the fields.

    # Return output.
    g.passwordResetLink = link
    return render_template("auth/reset-password.html")

@bp.route("/save-new-password", methods=("POST",))
def saveNewPassword():
    """Save the new password for the user."""

    # Get the user ID securely!
    link = request.form.get('link')
    db = get_db()
    error = None
    db_record = db.execute(
        "SELECT * FROM password_reset_link WHERE link = ?", (link,)
    ).fetchone()
    user_id = db_record["user_id"];
    # user_id = int(user_id); # Cast from string to number.
    # user_id = 3; # Hack!

    # Look up link in database.
    new_password = request.form.get('new_password')
    print ("New Password:", new_password)
    print ("User ID:", user_id)
    db.execute(
        "UPDATE user SET password = ? WHERE id = ?", (generate_password_hash(new_password), user_id)
    )
    # db.execute(
    #     "UPDATE user SET password = 'what' WHERE id = 3"
    # )
    db.commit()

    # TODO: The password is not updated. Perhaps I must cast to an integer first.

    # Return.
    content = {"status": "OK"};
    return jsonify(content)
