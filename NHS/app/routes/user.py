from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from functools import wraps



from app import db
from app.models import Questionnaire, User


# 用户蓝图（路由前缀 /user）
bp = Blueprint('user', __name__, url_prefix='/user')


# 登录验证装饰器（未登录则跳转登录页）
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


# 用户仪表盘（/user）
@bp.route('/')
@login_required
def dashboard():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login_page'))
    # 查询用户已完成的问卷
    completed_types = set()
    records = Questionnaire.query.filter_by(user_id=user_id).all()
    for record in records:
        completed_types.add(record.type)

    total = 3
    completed_count = len(completed_types)
    progress = int((completed_count / total) * 100)

    return render_template(
        'user_dashboard.html',
        username=User.query.get(user_id).name,  # 正确获取用户名
        progress_percent=progress,
        step1_completed='dasi' in completed_types,
        step2_completed='phq4' in completed_types,
        step3_completed='pgsga' in completed_types,
        step1_available=True,
        step2_available='dasi' in completed_types,
        step3_available='phq4' in completed_types
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


# 提交问卷接口（/user/questionnaires）
@bp.route('/questionnaires', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    try:
        user_id = int(get_jwt_identity())  # 将获取的用户 ID 转换为整数类型
        data = request.json

        # 2. 验证必要参数
        valid_types = {'dasi', 'phq4', 'pgsga'}
        required = ['type', 'answers', 'score', 'level']
        if not all(k in data for k in required) or data['type'] not in valid_types:
            return jsonify(msg="无效参数：需包含type、answers、score、level"), 400

        # 3. 验证数据类型
        try:
            float(data['score'])  # 确保分数为数字
            assert isinstance(data['level'], str)  # 等级为字符串
        except (ValueError, AssertionError) as e:
            print(f"数据类型验证失败: {e}")
            return jsonify(msg="数据类型错误：score需为数字，level需为字符串"), 400

        # 4. 保存问卷记录（独立存储每个问卷的分数和等级）
        try:
            new_record = Questionnaire(
                user_id=user_id,
                type=data['type'],
                score=float(data['score']),
                level=data['level'],
                answers=data['answers']  # 保存完整答案（含详情）
            )
            db.session.add(new_record)
            db.session.commit()

            return jsonify({
                'msg': f"{data['type']}提交成功",
                'data': {
                    'type': data['type'],
                    'score': float(data['score']),
                    'level': data['level'],
                    'submitted_at': new_record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 201
        except Exception as e:
            print(f"保存问卷记录失败: {e}")
            db.session.rollback()
            return jsonify(msg=f"提交失败：{str(e)}"), 500
    except Exception as e:
        print(f"处理请求时发生未知错误: {e}")
        return jsonify(msg=f"未知错误：{str(e)}"), 500


# 医生查看所有用户问卷详情（权限控制）
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

    # 返回完整详情（含答案、分数、等级）
    return jsonify({
        'id': record.id,
        'user_id': record.user_id,
        'username': User.query.get(record.user_id).name,
        'type': record.type,
        'score': float(record.score),
        'level': record.level,
        'answers': record.answers,  # 完整答案详情
        'submitted_at': record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200


# 获取当前用户的所有问卷记录（含各自分数和等级）
@bp.route('/questionnaires', methods=['GET'])
@jwt_required()
def get_user_questionnaires():
    user_id = get_jwt_identity()
    records = Questionnaire.query.filter_by(user_id=user_id).order_by(Questionnaire.submitted_at.desc()).all()

    result = []
    for record in records:
        result.append({
            'id': record.id,
            'type': record.type,
            'score': float(record.score),
            'level': record.level,
            'submitted_at': record.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result), 200