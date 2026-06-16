# ─────────────────────────────────────────────────────────────────
#  app/routes/main.py
#  Veltrix – Main Blueprint
#
#  Handles public-facing pages:
#    GET  /           → landing page
#    GET  /dashboard  → protected dashboard (login required)
#    POST /dashboard  → salary prediction form submission
# ─────────────────────────────────────────────────────────────────

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime, timezone

from app.utils.helpers import format_datetime
from app.services.churn_predictor import (
    predict_churn,
    get_field_options,
    PredictionInputError,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def landing():
    """
    Public landing page.
    Accessible to everyone – logged-in users see a personalised
    greeting, guests see the default welcome message.
    """
    return render_template("landing.html")


@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Protected dashboard page – model overview, metrics & analytics.
    """
    joined       = format_datetime(current_user.created_at)
    current_date = format_datetime(datetime.now(timezone.utc), fmt="%A, %B %d %Y")

    options = get_field_options()
    info = {
        "problem_type": "classification",
        "algorithm": "Random Forest Classifier",
        "accuracy": "0.7839",
        "precision": "0.6287",
        "recall": "0.4572",
        "f1_score": "0.5294",
        "model_loaded": True
    }

    return render_template(
        "dashboard.html",
        joined=joined,
        current_date=current_date,
        options=options,
        info=info,
    )


@main_bp.route("/test-model", methods=["GET", "POST"])
@main_bp.route("/predict", methods=["GET", "POST"])
@login_required
def test_model():
    """
    Halaman Prediksi Churn Pelanggan.
    GET  → render form kosong.
    POST → proses input form, kembalikan hasil prediksi.
    """
    options = get_field_options()
    result  = None

    if request.method == "POST":
        result = predict_churn(request.form)

    return render_template(
        "test_model.html",
        options=options,
        result=result,
    )