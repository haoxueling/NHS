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

    # 关联：一次提交对应一条记录，一条记录存三份问卷
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



    # DASI 问卷数据
    dasi_type = db.Column(db.String(50), default='dasi')
    dasi_score = db.Column(db.Float)
    dasi_level = db.Column(db.String(50))
    dasi_answers = db.Column(db.JSON)

    # PHQ4 问卷数据
    phq4_type = db.Column(db.String(50), default='phq4')
    phq4_score = db.Column(db.Float)
    phq4_level = db.Column(db.String(50))
    phq4_answers = db.Column(db.JSON)

    # PG-SGA 问卷数据
    pgsga_type = db.Column(db.String(50), default='pgsga')
    pgsga_score = db.Column(db.Float)
    pgsga_level = db.Column(db.String(50))
    pgsga_answers = db.Column(db.JSON)

    # 提交时间与状态（整体状态）
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # 一次提交即完成三份

    def __repr__(self):
        return f'<Questionnaire {self.id} 用户{self.user_id} 状态{self.status} 提交时间{self.submitted_at}>'