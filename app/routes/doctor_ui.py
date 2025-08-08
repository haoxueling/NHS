# app/routes/doctor_ui.py

from flask import Blueprint, render_template, redirect, url_for,request
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


@bp.route("/question-info", methods=['GET'])
def result_dashboard():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # 获取 GET 参数
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
#
# @bp.route("/question-info",methods=['POST'])
# def result_dashboard():
#     try:
#         # 验证 JWT 是否存在并有效
#         verify_jwt_in_request()
#         #这里的user是医生
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
#         #获取request中的问卷id
#         data = request.get_json()
#         question_id = data.get('id')
#         patient_name = data.get('name')
#
#         if not user:
#             return redirect(url_for('auth.login_page'))
#
#         return render_template('user_questionnaire_result.html', username=user.name, question_id=question_id , patient_name=patient_name )
#     except Exception as e:
#         # 如果 JWT 验证失败，跳转登录
#         print(f"JWT 错误：{e}")
#         return redirect(url_for('auth.login_page'))