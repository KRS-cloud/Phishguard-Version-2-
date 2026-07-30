import csv
import io
import json

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ScanHistory


history_bp = Blueprint(
    "history",
    __name__,
    url_prefix="/history",
)


@history_bp.route("/")
@login_required
def history():
    """
    Display the current user's scan history.
    """

    search_query = request.args.get(
        "search",
        "",
    ).strip()

    scan_type = request.args.get(
        "scan_type",
        "",
    ).strip()

    prediction = request.args.get(
        "prediction",
        "",
    ).strip()

    page = request.args.get(
        "page",
        1,
        type=int,
    )

    if page < 1:
        page = 1

    per_page = 10

    query = db.select(ScanHistory).where(
        ScanHistory.user_id == current_user.id
    )

    if search_query:
        query = query.where(
            ScanHistory.input_value.ilike(
                f"%{search_query}%"
            )
        )

    if scan_type in {"URL", "Email", "QR"}:
        query = query.where(
            ScanHistory.scan_type == scan_type
        )

    if prediction in {"Safe", "Suspicious", "Phishing"}:
        query = query.where(
            ScanHistory.prediction == prediction
        )

    query = query.order_by(
        ScanHistory.created_at.desc()
    )

    pagination = db.paginate(
        query,
        page=page,
        per_page=per_page,
        error_out=False,
    )

    total_scans = db.session.scalar(
        db.select(
            db.func.count(ScanHistory.id)
        ).where(
            ScanHistory.user_id == current_user.id
        )
    ) or 0

    safe_scans = db.session.scalar(
        db.select(
            db.func.count(ScanHistory.id)
        ).where(
            ScanHistory.user_id == current_user.id,
            ScanHistory.prediction == "Safe",
        )
    ) or 0

    suspicious_scans = db.session.scalar(
        db.select(
            db.func.count(ScanHistory.id)
        ).where(
            ScanHistory.user_id == current_user.id,
            ScanHistory.prediction == "Suspicious",
        )
    ) or 0

    phishing_scans = db.session.scalar(
        db.select(
            db.func.count(ScanHistory.id)
        ).where(
            ScanHistory.user_id == current_user.id,
            ScanHistory.prediction == "Phishing",
        )
    ) or 0

    return render_template(
        "history/history.html",
        scans=pagination.items,
        pagination=pagination,
        search_query=search_query,
        selected_scan_type=scan_type,
        selected_prediction=prediction,
        total_scans=total_scans,
        safe_scans=safe_scans,
        suspicious_scans=suspicious_scans,
        phishing_scans=phishing_scans,
    )


@history_bp.route("/<int:scan_id>")
@login_required
def scan_details(scan_id):
    """
    Display one detailed scan report.
    """

    scan = db.session.get(
        ScanHistory,
        scan_id,
    )

    if scan is None:
        abort(404)

    if scan.user_id != current_user.id:
        abort(403)

    recommendations = []

    if scan.recommendations:
        try:
            recommendations = json.loads(
                scan.recommendations
            )

        except (json.JSONDecodeError, TypeError):
            recommendations = [
                scan.recommendations
            ]

    return render_template(
        "history/scan_details.html",
        scan=scan,
        recommendations=recommendations,
    )


@history_bp.route("/export/csv")
@login_required
def export_csv():
    """
    Export the current user's scan history as a CSV file.
    """

    query = (
        db.select(ScanHistory)
        .where(
            ScanHistory.user_id == current_user.id
        )
        .order_by(
            ScanHistory.created_at.desc()
        )
    )

    scans = db.session.scalars(
        query
    ).all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Scan Type",
        "Input",
        "Prediction",
        "Risk Level",
        "Risk Score",
        "Confidence",
        "Explanation",
        "Recommendations",
        "Created At",
    ])

    for scan in scans:

        writer.writerow([
            scan.id,
            scan.scan_type,
            scan.input_value,
            scan.prediction,
            scan.risk_level,
            scan.risk_score,
            scan.confidence or "",
            scan.explanation or "",
            scan.recommendations or "",
            (
                scan.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if scan.created_at
                else ""
            ),
        ])

    csv_data = output.getvalue()

    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=phishguard_scan_history.csv"
        },
    )


@history_bp.route(
    "/<int:scan_id>/delete",
    methods=["POST"],
)
@login_required
def delete_scan(scan_id):
    """
    Delete one scan owned by the current user.
    """

    scan = db.session.get(
        ScanHistory,
        scan_id,
    )

    if scan is None:
        abort(404)

    if scan.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(scan)
        db.session.commit()

        flash(
            "The scan record was deleted successfully.",
            "success",
        )

    except Exception:
        db.session.rollback()

        flash(
            "The scan record could not be deleted.",
            "error",
        )

    return redirect(
        url_for("history.history")
    )