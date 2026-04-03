from flask import Blueprint, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models import User, Questionnaire
from app import db

statistics_bp = Blueprint('statistics', __name__)

def get_user_type(user):
    #Calculate and return the user type based on the latest questionnaire results.
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
@jwt_required()

def user_type_distribution():
    # Retrieve the filtered tumour type from the URL parameters; the default is “all”.
    tumor_type = request.args.get('tumor_type', 'all')
    doctor_id = get_jwt_identity()
    doctor = User.query.get(doctor_id)
    print(f"Currently selected tumour type: {tumor_type}") # Debug print

    #   Query all users with the role 'user'
    query = db.session.query(User).filter_by(role='user')

    #   If a specific tumour type is selected, filter users by that tumour type
    if tumor_type != 'all':
        query = query.filter_by(tumor_type=tumor_type)
        print(f"Currently filtering tumor_type = '{tumor_type}' users...") #Debug print

    users = query.all()
    print(f"Number of users retrieved: {len(users)}") #     Debug print
    
    #   Initialize counters for each user type
    type_count = {'specialist': 0, 'targeted': 0, 'universal': 0}

    for user in users:
        #   Get the latest questionnaire for each user
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
    
    print(f"Final tally: {type_count}") #   Debug print
    
    return render_template(
        'user_type_distribution.html',
        type_count=type_count,
        percentages=percentages,
        total_users=total_users,
        selected_tumor=tumor_type,
        username=doctor.name,      
        user_role=doctor.role      
    )