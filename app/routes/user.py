from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps
from datetime import datetime

from app import db
from app.models import Questionnaire, User

# 用户蓝图（路由前缀 /user）
bp = Blueprint('user', __name__, url_prefix='/user')


# 登录验证装饰器（未登录则跳转登录页）
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        token = request.cookies.get('access_token')
        print('获取到的令牌:', token)
        if not token:
            print('未找到令牌，重定向到登录页')
            return redirect(url_for('auth.login_page'))
        try:
            verify_jwt_in_request()
            print('JWT 验证成功')
        except Exception as e:
            print('JWT 验证失败:', str(e))
            return redirect(url_for('auth.login_page'))
        return view(*args, **kwargs)

    return wrapped_view


# 用户仪表盘（/user），移除进度条计算逻辑
@bp.route('/')
@login_required
def dashboard():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    # 直接渲染页面，不计算进度相关（后续若需展示可根据实际有数据的分问卷字段判断）
    return render_template(
        'user_dashboard.html',
        username=User.query.get(user_id).name  # 获取用户名
    )


# DASI问卷页面（/user/questionnaires/dasi）
@bp.route('/questionnaires/dasi')
@login_required
def dasi_questionnaire():
    return render_template('dasi.html')


# PHQ-4问卷页面（/user/questionnaires/phq4）
@bp.route('/questionnaires/phq4')
@login_required
def phq4_questionnaire():
    return render_template('phq4.html')


# PG-SGA问卷页面（/user/questionnaires/pgsga）
@bp.route('/questionnaires/pgsga')
@login_required
def pgsga_questionnaire():
    return render_template('pgsga.html')


# 合并提交所有问卷接口（/user/questionnaires/submit-all）
@bp.route('/questionnaires/submit-all', methods=['POST'])
@jwt_required()
def submit_all_questionnaires():
    user_id = get_jwt_identity()
    data = request.json

    # 校验三份问卷是否齐全
    required_questionnaires = ['dasi', 'phq4', 'pgsga']
    if not all(q in data for q in required_questionnaires):
        return jsonify(msg="please submit full DASI、PHQ4、PGSGA data"), 400

    # 解析各问卷数据
    dasi = data.get('dasi', {})
    phq4 = data.get('phq4', {})
    pgsga = data.get('pgsga', {})

    # 构造单条记录（存三份问卷数据）
    submission = Questionnaire(
        user_id=user_id,
        # DASI 数据
        dasi_score=dasi.get('mets_score'),
        dasi_level=dasi.get('level'),
        dasi_answers=dasi.get('answers'),
        # PHQ4 数据
        phq4_score=phq4.get('phq4_total'),
        phq4_level=phq4.get('level'),
        phq4_answers=phq4.get('answers'),
        # PGSGA 数据
        pgsga_score=pgsga.get('pgsga_total'),
        pgsga_level=pgsga.get('level'),
        pgsga_answers=pgsga.get('answers'),
        # 整体状态
        status='completed',
        submitted_at=datetime.utcnow()
    )

    # 保存到数据库
    try:
        db.session.add(submission)
        db.session.commit()
        return jsonify(
            msg="三份问卷已提交（单条记录）",
            submission_id=submission.id
        ), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f"submit failed：{str(e)}"), 500


# 医生查看所有用户问卷详情（权限控制），修正返回字段
@bp.route('/questionnaires/<int:q_id>')
@jwt_required()
def get_questionnaire_detail(q_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # 医生可查看所有问卷，普通用户仅查看自己的
    if current_user.role == 'doctor':
        record = Questionnaire.query.get_or_404(q_id)
    else:
        record = Questionnaire.query.filter_by(id=q_id, user_id=current_user_id).first_or_404()

    # 返回完整详情（按实际模型字段，分问卷返回 ）
    return jsonify({
        'id': record.id,
        'user_id': record.user_id,
        'username': User.query.get(record.user_id).name,
        # 分问卷数据，原来错误用了不存在的type等字段，现在按实际模型返回
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


# 获取当前用户的所有问卷记录（含各自分数和等级），修正返回字段
@bp.route('/questionnaires', methods=['GET'])
@jwt_required()
def get_user_questionnaires():
    user_id = get_jwt_identity()
    records = Questionnaire.query.filter_by(user_id=user_id).order_by(Questionnaire.submitted_at.desc()).all()

    result = []
    for record in records:
        result.append({
            'id': record.id,
            # 原来错误用了不存在的type字段，可根据实际需求决定是否保留、怎么标识问卷类型
            # 这里先去掉错误的type，若需区分，可结合业务逻辑判断（比如根据哪个分问卷有值 ）
            # 'type': record.type,
            'dasi_score': record.dasi_score,
            'dasi_level': record.dasi_level,
            'phq4_score': record.phq4_score,
            'phq4_level': record.phq4_level,
            'pgsga_score': record.pgsga_score,
            'pgsga_level': record.pgsga_level,
            'submitted_at': record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200