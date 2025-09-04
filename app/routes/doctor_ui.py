# app/routes/doctor_ui.py

from app import db
from flask import Blueprint, jsonify, render_template, redirect, url_for,request
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from app.models import User,Questionnaire
import json

bp = Blueprint('doctor_ui', __name__, url_prefix='/doctor')

@bp.route('/')
def static_doctor_dashboard():
    try:
        # Verify that the JWT exists and is valid
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        questionnaires = Questionnaire.query.all()
        if not user:
            return redirect(url_for('auth.login_page'))

        return render_template('doctor_dashboard.html', username=user.name,patients = questionnaires,user_role=user.role)
    except Exception as e:
        # If JWT verification fails, redirect to login.
        print(f"JWT error：{e}")
        return redirect(url_for('auth.login_page'))


@bp.route("/question-info", methods=['GET'])
def result_dashboard():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Retrieve GET parameters
        question_id = request.args.get('id')
        patient_name = request.args.get('name')

        if not user:
            return redirect(url_for('auth.login_page'))

        return render_template(
            'user_questionnaire_result.html',
            username=user.name,
            question_id=question_id,
            patient_name=patient_name
        )
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('auth.login_page'))

#View the responses for a specific section within a questionnaire
@bp.route("/result_detail")
def result_detail():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('auth.login_page'))

        # Retrieve GET parameters
        question_id = request.args.get('id')
        type = request.args.get('type')
        questionnaire=Questionnaire.query.filter_by(id=question_id).first()
        print('type=',type)
        if type=='dasi':
            score=questionnaire.dasi_score
            result_json=questionnaire.dasi_answers
            return render_template('dasi_result.html',result=result_json,score=score)
        elif type=='phq4':
            result_json = questionnaire.phq4_answers
            score=questionnaire.phq4_score

            return render_template('phq4_result.html',result=result_json,score=score)
        elif type=='pgsga':
            result_json = questionnaire.pgsga_answers
            score=questionnaire.pgsga_score

            return render_template('pgsga_result.html',result=result_json,score=score)
        else:
            a=1
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('auth.login_page'))

@bp.route('/profile', methods=['GET', 'POST'])
@jwt_required()  
def doctor_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'doctor':
        return redirect(url_for('auth.login_page'))

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password and new_password != confirm_password:
            # Flash message prompt: Password mismatch
            return redirect(url_for('doctor_ui.doctor_profile'))

        if email:
            user.email = email
        if phone:
            user.phone = phone
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        return redirect(url_for('doctor_ui.doctor_profile'))

    return render_template('doctor_profile.html', user=user, username=user.name, user_role=user.role)

# Password Verification API Endpoint
@bp.route('/check-password', methods=['POST'])
def check_password():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        data = request.get_json()
        password = data.get('password')

        if user.check_password(password):
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': 'Incorrect password'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Authentication error: {str(e)}'}), 401