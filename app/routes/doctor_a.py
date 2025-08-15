# app/routes/doctor_a.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, g
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User, Question, Answer  # ✅ 关键修改：导入 Answer 模型
from app import db
from app.routes.statistics_routes import get_user_type
from datetime import datetime
from sqlalchemy.orm import joinedload

# 创建新的医生回答蓝图
doctor_a_bp = Blueprint('doctor_a', __name__)

@doctor_a_bp.before_request
def check_doctor_role():
    """
    在所有 doctor_a 蓝图的路由执行前，检查用户是否为医生。
    """
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect(url_for('auth.login_page'))

@doctor_a_bp.route('/qa_dashboard')
@jwt_required()
def qa_dashboard():
    """
    医生问答看板，显示所有用户的问题。
    """
    
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    # ✅ 修改：查询时加载关联的 answers 和 user
    questions = Question.query.options(
        joinedload(Question.user),
        joinedload(Question.answers).joinedload(Answer.doctor)
    ).order_by(Question.created_at.desc()).all()
    
    questions_with_info = []
    for q in questions:
        user_type = get_user_type(q.user)
        
        # ✅ 修改：获取最新回答的医生名字
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
    医生回答问题的 AJAX API。
    """
    question = Question.query.get_or_404(question_id)
    answer_content = request.form.get('answer')
    doctor_id = session.get('user_id')
    
    if answer_content and doctor_id:
        # ✅ 关键修改：创建新的 Answer 对象并添加到数据库
        new_answer = Answer(
            content=answer_content,
            question_id=question_id,
            doctor_id=doctor_id
        )
        db.session.add(new_answer)
        
        # ✅ 更新问题状态为 'answered'
        if question.status != 'answered':
            question.status = 'answered'
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Answer content is required or doctor ID is missing'}), 400