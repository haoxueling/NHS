from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from datetime import datetime

from app import db
from app.models import Questionnaire, User

# User Blueprint (routing prefix /user)
bp = Blueprint('user', __name__, url_prefix='/user')


# Login Verification Decorator (redirects to login page if not logged in)
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        token = request.cookies.get('access_token')
        print('The token obtained:', token)
        if not token:
            print('No token found. Redirecting to the login page.')
            return redirect(url_for('auth.login_page'))
        try:
            verify_jwt_in_request()
            print('JWT verification successful')
        except Exception as e:
            print('JWT Verification failed:', str(e))
            return redirect(url_for('auth.login_page'))
        return view(*args, **kwargs)

    return wrapped_view


# User Dashboard (/user), remove progress bar calculation logic
@bp.route('/')
@login_required
def dashboard():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    return render_template(
        'user_dashboard.html',
        username=User.query.get(user_id).name,
        user_role=User.query.get(user_id).role
    )


# （/user/questionnaires/dasi）
@bp.route('/questionnaires/dasi')
@login_required
def dasi_questionnaire():
    return render_template('dasi.html')


#（/user/questionnaires/phq4）
@bp.route('/questionnaires/phq4')
@login_required
def phq4_questionnaire():
    return render_template('phq4.html')


# （/user/questionnaires/pgsga）
@bp.route('/questionnaires/pgsga')
@login_required
def pgsga_questionnaire():
    return render_template('pgsga.html')


# （/user/questionnaires/submit-all）
@bp.route('/questionnaires/submit-all', methods=['POST'])
@jwt_required()
def submit_all_questionnaires():
    user_id = get_jwt_identity()
    data = request.json

    # Verify that all three questionnaires are complete.
    required_questionnaires = ['dasi', 'phq4', 'pgsga']
    if not all(q in data for q in required_questionnaires):
        return jsonify(msg="please submit full DASI、PHQ4、PGSGA data"), 400

    # Analyse the data from each questionnaire
    dasi = data.get('dasi', {})
    phq4 = data.get('phq4', {})
    pgsga = data.get('pgsga', {})

    # Construct a single record (containing three questionnaire entries)
    submission = Questionnaire(
        user_id=user_id,
        # DASI 
        dasi_score=dasi.get('mets_score'),
        dasi_level=dasi.get('level'),
        dasi_answers=dasi.get('answers'),
        # PHQ4 
        phq4_score=phq4.get('phq4_total'),
        phq4_level=phq4.get('level'),
        phq4_answers=phq4.get('answers'),
        # PGSGA 
        pgsga_score=pgsga.get('pgsga_total'),
        pgsga_level=pgsga.get('level'),
        pgsga_answers=pgsga.get('answers'),
        # Overall condition
        status='completed',
        submitted_at=datetime.utcnow()
    )

    #   Save to database
    try:
        db.session.add(submission)
        db.session.commit()
        return jsonify(
            msg="Three questionnaires have been submitted (single record)",
            submission_id=submission.id
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f"submit failed：{str(e)}"), 500


# Doctors may view all user questionnaire details (subject to permission controls), with corrected return fields.
@bp.route('/questionnaires/<int:q_id>')
@jwt_required()
def get_questionnaire_detail(q_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # Permission check: doctors can view all, users can only view their own
    if current_user.role == 'doctor':
        record = Questionnaire.query.get_or_404(q_id)
    else:
        record = Questionnaire.query.filter_by(id=q_id, user_id=current_user_id).first_or_404()

    #    Corrected return fields
    return jsonify({
        'id': record.id,
        'user_id': record.user_id,
        'username': User.query.get(record.user_id).name,
        # Removed erroneous 'type' field
        'dasi_score': record.dasi_score,
        'dasi_level': record.dasi_level,
        'dasi_answers': record.dasi_answers,
        'phq4_score': record.phq4_score,
        'phq4_level': record.phq4_level,
        'phq4_answers': record.phq4_answers,
        'pgsga_score': record.pgsga_score,
        'pgsga_level': record.pgsga_level,
        'pgsga_answers': record.pgsga_answers,
        'submitted_at': record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


# User views their own questionnaire history list, with corrected return fields.
@bp.route('/questionnaires', methods=['GET'])
@jwt_required()
def get_user_questionnaires():
    user_id = get_jwt_identity()
    records = Questionnaire.query.filter_by(user_id=user_id).order_by(Questionnaire.submitted_at.desc()).all()

    result = []
    for record in records:
        result.append({
            'id': record.id,
            'dasi_score': record.dasi_score,
            'dasi_level': record.dasi_level,
            'phq4_score': record.phq4_score,
            'phq4_level': record.phq4_level,
            'pgsga_score': record.pgsga_score,
            'pgsga_level': record.pgsga_level,
            'submitted_at': record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    current_user_id = request.cookies.get('user_id')
    current_user = User.query.get(current_user_id)

    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        phone = request.form.get('phone')
        tumor_type = request.form.get('tumor_type')  
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        #   If changing password, verify old password
        if new_password and new_password != confirm_password:
            return redirect(url_for('user.user_profile'))

        #   Update user information
        if email:
            current_user.email = email
        if phone:
            current_user.phone = phone
        if tumor_type:
            current_user.tumor_type = tumor_type
        if new_password:
            current_user.set_password(new_password)
        
        db.session.commit()
        return redirect(url_for('user.user_profile'))

    return render_template('user_profile.html', user=current_user,username=current_user.name, user_role=current_user.role)
# Password Verification API Endpoint
@bp.route('/check-password', methods=['POST'])
@login_required
def check_password():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    data = request.get_json()
    password = data.get('password')

    if user.check_password(password):
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Incorrect password'}), 400