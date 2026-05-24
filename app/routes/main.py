# ─────────────────────────────────────────────────────────────────
#  app/routes/main.py
#  Veltrix – Main Blueprint
#
#  Handles public-facing pages:
#    GET /           → landing page
#    GET /dashboard  → protected dashboard (login required)
# ─────────────────────────────────────────────────────────────────

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app.utils.helpers import format_datetime

# Create the blueprint; "main" is its internal name
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    """
    Public landing page.
    Accessible to everyone – logged-in users see a personalised
    greeting, guests see the default welcome message.
    """
    return render_template("landing.html")


@main_bp.route("/dashboard")
@login_required  # redirects to auth.login if user is not authenticated
def dashboard():
    """
    Protected dashboard page.
    Only accessible to authenticated users.
    Passes the current user and their formatted join date to the template.
    """
    joined       = format_datetime(current_user.created_at)
    current_date = format_datetime(datetime.now(timezone.utc), fmt="%A, %B %d %Y")
    return render_template("dashboard.html", joined=joined, current_date=current_date)
