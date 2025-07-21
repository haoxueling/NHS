from datetime import datetime
import bcrypt
from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_id = db.Column(db.String(50), unique=True, nullable=False)
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'nurse', 'doctor'), default='user')  # 支持医生角色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联用户的所有问卷记录
    questionnaires = db.relationship('Questionnaire', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )


class Questionnaire(db.Model):
    __tablename__ = 'questionnaire'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户
    type = db.Column(db.String(50), nullable=False)  # 问卷类型：dasi/phq4/pgsga
    score = db.Column(db.Float, nullable=False)  # 该问卷的分数
    level = db.Column(db.String(50), nullable=False)  # 该问卷的等级
    answers = db.Column(db.JSON, nullable=False)  # 完整问卷答案（含详情）
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')

    def __repr__(self):
        return f'<Questionnaire {self.id} {self.type} {self.score}分 {self.level}>'