# app/routes/doctor_ui.py

from flask import Blueprint, render_template, redirect, url_for,request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User,Questionnaire
import json

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

#查看某个问卷的其中一个板块的答案
@bp.route("/result_detail")
def result_detail():
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('auth.login_page'))

        # 获取 GET 参数
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