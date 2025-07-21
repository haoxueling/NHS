"""用户注册登录接口"""
#print("auth.py 模块开始加载", flush=True)
from flask import Blueprint, request, jsonify, render_template, redirect, make_response
from flask_jwt_extended import create_access_token
from datetime import timedelta
from app import db
from app.models import User
from flask_cors import cross_origin  # 解决跨域问题
from sqlalchemy.exc import IntegrityError

# 初始化蓝图（无额外前缀，路由直接映射根路径）
bp = Blueprint('auth', __name__)

# 登录页面路由（前端访问 /login）
@bp.route('/login')
def login_page():
    return render_template('login.html')

# 注册页面路由（前端访问 /register）
@bp.route('/register')
def register_page():
    return render_template('register.html')

# 注册接口（前端请求 /api/register）
@bp.route('/api/register', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def register():
    """用户注册"""
    if request.method == 'OPTIONS':
        return jsonify(), 200

    data = request.json
    if not data:
        return jsonify(msg='请求数据为空'), 400

    # 验证必要字段
    required_fields = ['name', 'gender', 'date_of_birth', 'medical_id', 'email', 'phone', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify(msg=f'缺少必要字段或字段值为空: {field}'), 400

    # 检查医疗账号和邮箱唯一性
    if User.query.filter_by(medical_id=data['medical_id']).first():
        return jsonify(msg='医疗账号已被注册'), 400


    # 创建用户（捕获数据库异常）
    try:
        user = User(
            name=data['name'],
            gender=data['gender'],
            date_of_birth=data['date_of_birth'],
            medical_id=data['medical_id'],
            email=data['email'],
            phone=data['phone'],
            role='user'
        )
        user.set_password(data['password'])  # 确保User模型实现了set_password方法
        db.session.add(user)
        db.session.commit()
        return jsonify(msg='注册成功'), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify(msg=f'注册失败：数据库插入错误 {str(e)}'), 500
    except Exception as e:
        db.session.rollback()
        return jsonify(msg=f'注册失败：{str(e)}'), 500

# 登录接口（前端请求 /api/login）
@bp.route('/api/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    """用户登录"""
    print("收到登录请求", flush=True)
    if request.method == 'OPTIONS':
        return jsonify(), 200

    try:  # 新增异常捕获
        data = request.json
        print(f"请求数据：{data}", flush=True)  # 打印前端传来的参数
        if not data:
            return jsonify(msg='请求数据为空'), 400
        if not data.get('medical_id') or not data.get('password'):
            return jsonify(msg='请提供医疗账号和密码'), 400
        # 数据库查询（可能出错的步骤）
        user = User.query.filter_by(medical_id=data['medical_id']).first()
        if not user or not user.check_password(data['password']):
            return jsonify(msg='医疗账号或密码错误'), 401
        # 生成令牌
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role},
            expires_delta=timedelta(hours=24)
        )
        resp = make_response(jsonify(
            access_token=access_token,
            user={'id': user.id, 'name': user.name, 'role': user.role, 'medical_id': user.medical_id}
        ))
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    except Exception as e:  # 捕获所有异常并打印
        print(f"登录接口异常：{str(e)}", flush=True)  # 强制打印异常
        return jsonify(msg=f"服务器内部错误：{str(e)}"), 500

# 根路径重定向到登录页
@bp.route('/')
def index():
    return redirect('/login')  # 修正重定向路径，匹配登录页面路由