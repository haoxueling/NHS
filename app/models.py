from datetime import datetime
import bcrypt
from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other', name='user_gender_enum'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_id = db.Column(db.String(50), unique=True, nullable=False)
    chi_number = db.Column(db.String(10), unique=True, nullable=True)
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'nurse', 'doctor', name='user_role_enum'), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tumor_type = db.Column(db.String(50), nullable=True)
    # Correlation: Each submission corresponds to one record, with each record storing three questionnaires.
    questionnaires = db.relationship(
        'Questionnaire',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

# models.py
class Questionnaire(db.Model):
    __tablename__ = 'questionnaire'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户

    status = db.Column(db.String(20), default='completed')

    # DASI  
    dasi_type = db.Column(db.String(50), default='dasi')
    dasi_score = db.Column(db.Float)
    dasi_level = db.Column(db.String(50))
    dasi_answers = db.Column(db.JSON)

    # PHQ4  
    phq4_type = db.Column(db.String(50), default='phq4')
    phq4_score = db.Column(db.Float)
    phq4_level = db.Column(db.String(50))
    phq4_answers = db.Column(db.JSON)

    # PG-SGA    
    pgsga_type = db.Column(db.String(50), default='pgsga')
    pgsga_score = db.Column(db.Float)
    pgsga_level = db.Column(db.String(50))
    pgsga_answers = db.Column(db.JSON)

    #   Common fields
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Questionnaire {self.id} {self.type} {self.score}分 {self.level}>'
    
#Answer 
class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    
    # Related issues and doctors
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Answer content and timestamp
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='answers', lazy=True)
    doctor = db.relationship('User', backref='answers_by_doctor', lazy=True)
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'
    
# Question
class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='questions', lazy=True)
    
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f'<Question {self.id} by {self.user.name}>'