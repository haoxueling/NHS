"""用户注册登录接口"""
#print("auth.py 模块开始加载", flush=True)
from flask import Blueprint, request, jsonify, render_template, redirect, make_response, Flask, session, url_for
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
    # required_fields = ['name', 'gender', 'date_of_birth', 'medical_id', 'email', 'phone', 'password']
    required_fields = ['name', 'gender', 'date_of_birth', 'email', 'phone', 'password',"role"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify(msg=f'缺少必要字段或字段值为空: {field}'), 400

    # 检查医疗账号和邮箱唯一性
    if User.query.filter_by(medical_id=data['medical_id']).first():
        return jsonify(msg='医疗账号已被注册'), 400

    role = data['role']

    if role == 'user':  # 患者注册
        chi_number = data.get('chi_number')
        if not chi_number:
            return jsonify(msg='请提供 CHI Number'), 400

        # 确保 CHI 号码唯一（包括兼容 medical_id 字段）
        if User.query.filter(
                (User.chi_number == chi_number) | (User.medical_id == chi_number)
        ).first():
            return jsonify(msg='该 CHI Number 已被注册'), 400

        medical_id = chi_number  # 为了模型中 medical_id 非空约束，写入相同值

    elif role == 'doctor':  # 临床人员注册
        medical_id = data.get('medical_id')
        if not medical_id:
            return jsonify(msg='请提供 Medical ID'), 400

        if User.query.filter_by(medical_id=medical_id).first():
            return jsonify(msg='该 Medical ID 已被注册'), 400

        chi_number = None  # 医生无 chi_number

    else:
        return jsonify(msg='无效的角色'), 400


    # 创建用户（捕获数据库异常）
    try:
        user = User(
            name=data['name'],
            gender=data['gender'],
            date_of_birth=data['date_of_birth'],
            medical_id=medical_id,
            chi_number=chi_number,
            email=data['email'],
            phone=data['phone'],
            role=role
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

        role = data.get('role')
        password = data.get('password')

        if not role or not password:
            return jsonify(msg='缺少角色或密码'), 400

        user = None

        if role == 'patient':
            chi_number = data.get('chi_number')
            if not chi_number:
                return jsonify(msg='缺少 CHI Number'), 400
            user = User.query.filter_by(role='user', chi_number=chi_number).first()
        # 数据库里面的role doctor 字段对应clinician ，user字段对应patient
        elif role == 'clinician':
            medical_id = data.get('medical_id')
            if not medical_id:
                return jsonify(msg='缺少 Medical ID'), 400
            user = User.query.filter_by(role='doctor', medical_id=medical_id).first()

        else:
            return jsonify(msg='无效的角色'), 400

        if not user or not user.check_password(password):
            return jsonify(msg='账号或密码错误'), 401

        # 生成令牌
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role},
            expires_delta=timedelta(hours=24)
        )
        resp = make_response(jsonify(
            access_token=access_token,
            user={
                 'id': user.id,
                  'name': user.name,
                  'role': user.role,
                  'medical_id': user.medical_id,
                 'chi_number': user.chi_number
                  }
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
# 退出登录路由（清除Token并跳转登录页）
@bp.route('/logout')
def logout():
    """用户退出登录：清除Token Cookie并重定向到登录页"""
    # 创建响应对象，用于删除Cookie
    resp = make_response(redirect(url_for('auth.login_page')))  # 重定向到登录页面
    # 删除存储的access_token Cookie（与登录时设置的Cookie路径保持一致）
    resp.delete_cookie('access_token', path='/')  # path='/'确保所有路径下的Cookie都被清除

    return resp