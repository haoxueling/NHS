# app/routes/doctor_ui.py

from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User,Questionnaire


bp = Blueprint('doctor_ui', __name__, url_prefix='/doctor')

@bp.route('/')
def static_doctor_dashboard():
    try:
        # 验证 JWT 是否存在并有效
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        questionnaires = Questionnaire.query.all()
        if not user:
            return redirect(url_for('auth.login_page'))

        return render_template('doctor_dashboard.html', username=user.name,patients = questionnaires)
    except Exception as e:
        # 如果 JWT 验证失败，跳转登录
        print(f"JWT 错误：{e}")
        return redirect(url_for('auth.login_page'))
