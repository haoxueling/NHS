from flask import Blueprint, render_template
from app.models import User

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/user_type_distribution')
def user_type_distribution():
    users = User.query.all()

    type_count = {
        'specialist': 0,
        'targeted': 0,
        'universal': 0
    }

    total_users = len(users)

    for user in users:
        questionnaires = user.questionnaires.all()

        is_specialist = False
        is_targeted = False

        for q in questionnaires:
            levels = [q.dasi_level, q.phq4_level, q.pgsga_level]
            if any(level and 'specialist' in level.lower() for level in levels):
                is_specialist = True
                break
            if any(level and 'targeted' in level.lower() for level in levels):
                is_targeted = True

        if is_specialist:
            type_count['specialist'] += 1
        elif is_targeted:
            type_count['targeted'] += 1
        else:
            type_count['universal'] += 1

    # 计算百分比
    if total_users > 0:
        percentages = {
            key: f"{(count / total_users * 100):.2f}%" for key, count in type_count.items()
        }
    else:
        percentages = {key: "0%" for key in type_count}

    return render_template('user_type_distribution.html',
                           type_count=type_count,
                           percentages=percentages,
                           total_users=total_users)
