# app/routes/doctor_a.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, g
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User, Question, Answer  
from app import db
from app.routes.statistics_routes import get_user_type
from datetime import datetime
from sqlalchemy.orm import joinedload

# Create a new blueprint for doctor responses
doctor_a_bp = Blueprint('doctor_a', __name__)

@doctor_a_bp.before_request
def check_doctor_role():
    """
    Before executing any routes in the doctor_a blueprint, verify that the user is a doctor.
    """
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect(url_for('auth.login_page'))

@doctor_a_bp.route('/qa_dashboard')
@jwt_required()
def qa_dashboard():
    """
    Doctor Q&A Board, displaying all users' questions.
    """
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # Fetch all questions with related user and answers in one query to optimize performance
    questions = Question.query.options(
        joinedload(Question.user),
        joinedload(Question.answers).joinedload(Answer.doctor)
    ).order_by(Question.created_at.desc()).all()
    
    questions_with_info = []
    for q in questions:
        user_type = get_user_type(q.user)
        
        # Get the name of the doctor who answered the question, if any
        doctor_name = q.answers[0].doctor.name if q.answers else None
        
        questions_with_info.append({
            'id': q.id,
            'title': q.title,
            'content': q.content,
            'created_at': q.created_at,
            'answer': q.answers[-1].content if q.answers else None,
            'answered_at': q.answers[-1].created_at if q.answers else None,
            'status': q.status,
            'user_name': q.user.name,
            'user_tumor_type': q.user.tumor_type,
            'user_type': user_type,
            'doctor_name': doctor_name
        })
    
    return render_template('qa_dashboard.html', questions=questions_with_info, username=user.name, user_role=user.role)

@doctor_a_bp.route('/answer_question/<int:question_id>', methods=['POST'])
def answer_question(question_id):
    """
    AJAX API for Doctor Responses
    """
    question = Question.query.get_or_404(question_id)
    answer_content = request.form.get('answer')
    doctor_id = session.get('user_id')
    
    if answer_content and doctor_id:
        # Create a new response record
        new_answer = Answer(
            content=answer_content,
            question_id=question_id,
            doctor_id=doctor_id
        )
        db.session.add(new_answer)
        
        # Update the issue status to 'answered'
        if question.status != 'answered':
            question.status = 'answered'
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Answer content is required or doctor ID is missing'}), 400