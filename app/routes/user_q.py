# app/routes/user_q.py
from flask import Blueprint, render_template, request, redirect, url_for, session, make_response
from app.models import User, Question, Answer
from app import db
from sqlalchemy.orm import joinedload

# Create a new user Q&A blueprint
user_q_bp = Blueprint('user_q', __name__)

@user_q_bp.route('/my_questions', methods=['GET', 'POST'])
def my_questions():
    """
    A homepage where users can ask questions and view their own queries.
    """
    if 'user_id' not in session:
        print("Debug: user_id not in session. Redirecting to login.")  
        return redirect(url_for('auth.login_page'))
    
    user_id = session['user_id']
    print(f"Debug: user_id from session is {user_id}") 
    user = User.query.get(user_id)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            new_question = Question(user_id=user_id, title=title, content=content, status='pending')
            db.session.add(new_question)
            db.session.commit()
            print("Debug: New question submitted and committed.") 
            return redirect(url_for('user_q.my_questions'))
    
    # Force reload of data in the database
    db.session.expire_all()
    
    questions = Question.query.filter_by(user_id=user_id)\
                              .options(joinedload(Question.answers).joinedload(Answer.doctor))\
                              .order_by(Question.created_at.desc())\
                              .all()
    
    print(f"Debug: Found {len(questions)} questions for user {user_id}") 
    
    # Responses disabling browser caching
    resp = make_response(render_template('my_questions.html', questions=questions, username=user.name, user_role=user.role))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp