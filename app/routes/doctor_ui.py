# app/routes/doctor_ui.py
from flask import Blueprint, render_template

bp = Blueprint('doctor_ui', __name__)

@bp.route('/doctor')
def static_doctor_dashboard():
    return render_template('doctor_dashboard.html')
