from flask import Blueprint, render_template, request
from app.models import User, Questionnaire
from app import db

statistics_bp = Blueprint('statistics', __name__)

def get_user_type(user):
    #根据用户的最新问卷结果计算并返回用户类型
    latest_questionnaire = user.questionnaires.order_by(Questionnaire.submitted_at.desc()).first()
    
    user_type_result = 'universal'
    if latest_questionnaire:
        levels = [
            latest_questionnaire.dasi_level,
            latest_questionnaire.phq4_level,
            latest_questionnaire.pgsga_level
        ]
        levels = [level.lower() for level in levels if level]

        if any('specialist' in level for level in levels):
            user_type_result = 'specialist'
        elif any('targeted' in level for level in levels):
            user_type_result = 'targeted'
    return user_type_result


@statistics_bp.route('/user_type_distribution')
def user_type_distribution():
    # 从 URL 参数中获取筛选的肿瘤类型，默认是 'all'
    tumor_type = request.args.get('tumor_type', 'all')
    print(f"当前筛选的肿瘤类型: {tumor_type}") # 调试打印

    # 构建基础查询，只筛选角色为 'user' 的用户
    query = db.session.query(User).filter_by(role='user')

    # 如果选择了特定的肿瘤类型，则添加过滤条件
    if tumor_type != 'all':
        query = query.filter_by(tumor_type=tumor_type)
        print(f"正在筛选 tumor_type = '{tumor_type}' 的用户...") # 调试打印

    users = query.all()
    print(f"查询到的用户数量: {len(users)}") # 调试打印
    
    # 初始化用户类型计数器
    type_count = {'specialist': 0, 'targeted': 0, 'universal': 0}

    for user in users:
        # 获取该用户的最新问卷记录
        latest_questionnaire = user.questionnaires.order_by(Questionnaire.submitted_at.desc()).first()
        
        if latest_questionnaire:
            is_specialist = False
            is_targeted = False

            levels = [
                latest_questionnaire.dasi_level,
                latest_questionnaire.phq4_level,
                latest_questionnaire.pgsga_level
            ]
            levels = [level.lower() for level in levels if level]

            if any('specialist' in level for level in levels):
                is_specialist = True
            elif any('targeted' in level for level in levels):
                is_targeted = True

            if is_specialist:
                type_count['specialist'] += 1
            elif is_targeted:
                type_count['targeted'] += 1
            else:
                type_count['universal'] += 1

    total_users = sum(type_count.values())
    
    percentages = {
        key: f"{(count / total_users * 100):.2f}%" if total_users > 0 else "0.00%"
        for key, count in type_count.items()
    }
    
    print(f"最终计数结果: {type_count}") # 调试打印
    
    return render_template(
        'user_type_distribution.html',
        type_count=type_count,
        percentages=percentages,
        total_users=total_users,
        selected_tumor=tumor_type
    )