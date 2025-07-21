# app/routes/staff.py
"""护士和医生接口"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import User, Questionnaire
from app.utils.auth import role_required
from datetime import datetime

bp = Blueprint('staff', __name__)


@bp.route('/users', methods=['GET'])
@jwt_required()
@role_required(['nurse', 'doctor'])
def get_users():
    """获取用户列表，支持按等级筛选"""
    # 获取当前用户角色
    current_role = get_jwt()['role']

    # 获取筛选参数
    level = request.args.get('level', 'all')

    # 构建查询
    query = User.query.join(Questionnaire).group_by(User.id)

    # 医生默认筛选targeted和specialist
    if current_role == 'doctor' and level == 'all':
        query = query.filter(Questionnaire.level.in_(['targeted', 'specialist']))
    elif level != 'all':
        query = query.filter(Questionnaire.level == level)

    users = query.all()

    # 格式化返回
    result = []
    for user in users:
        # 计算年龄
        dob = user.date_of_birth
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        # 获取最新提交时间
        latest_q = user.questionnaires.order_by(Questionnaire.submitted_at.desc()).first()

        # 获取各问卷分数和等级
        dasi = user.questionnaires.filter_by(type='dasi').order_by(Questionnaire.submitted_at.desc()).first()
        phq4 = user.questionnaires.filter_by(type='phq4').order_by(Questionnaire.submitted_at.desc()).first()
        pgsga = user.questionnaires.filter_by(type='pgsga').order_by(Questionnaire.submitted_at.desc()).first()

        result.append({
            'id': user.id,
            'name': user.name,
            'medical_id': user.medical_id,
            'gender': user.gender,
            'age': age,
            'last_submitted_at': latest_q.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if latest_q else None,
            'dasi_score': float(dasi.score) if dasi else None,
            'dasi_level': dasi.level if dasi else None,
            'phq4_score': float(phq4.score) if phq4 else None,
            'phq4_level': phq4.level if phq4 else None,
            'pgsga_score': float(pgsga.score) if pgsga else None,
            'pgsga_level': pgsga.level if pgsga else None
        })

    return jsonify(result), 200


@bp.route('/users/<int:user_id>/questionnaires', methods=['GET'])
@jwt_required()
@role_required(['nurse', 'doctor'])
def get_user_questionnaires(user_id):
    """获取指定用户的问卷详情"""
    questionnaires = Questionnaire.query.filter_by(user_id=user_id).order_by(Questionnaire.submitted_at.desc()).all()

    result = []
    for q in questionnaires:
        result.append({
            'id': q.id,
            'type': q.type,
            'type_name': {
                'dasi': 'Duke Activity Status Index',
                'phq4': 'Patient Health Questionnaire-4',
                'pgsga': 'Patient-Generated Subjective Global Assessment'
            }[q.type],
            'score': float(q.score),
            'level': q.level,
            'answers': q.answers,
            'submitted_at': q.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(result), 200