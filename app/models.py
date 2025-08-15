from datetime import datetime
import bcrypt
from app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    # ✅ 修复: 为 ENUM 类型添加了 name 参数
    gender = db.Column(db.Enum('male', 'female', 'other', name='user_gender_enum'), nullable=False)
    # gender = db.Column(db.Enum('male', 'female', 'other'), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_id = db.Column(db.String(50), unique=True, nullable=False)
    # patient 新添chi_number 终端使用 Flask-Migrate 更新数据库：
    chi_number = db.Column(db.String(10), unique=True, nullable=True)
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # ✅ 修复: 为 ENUM 类型添加了 name 参数
    role = db.Column(db.Enum('user', 'nurse', 'doctor', name='user_role_enum'), default='user')
    # role = db.Column(db.Enum('user', 'nurse', 'doctor'), default='user')  # 支持医生角色
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # 新增肿瘤类型字段（患者专用，允许为空不影响医生角色）
    tumor_type = db.Column(db.String(50), nullable=True)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户

    # type = db.Column(db.String(50), nullable=False)  # 问卷类型：dasi/phq4/pgsga
    # score = db.Column(db.Float, nullable=False)  # 该问卷的分数
    # level = db.Column(db.String(50), nullable=False)  # 该问卷的等级
    # answers = db.Column(db.JSON, nullable=False)  # 完整问卷答案（含详情）
    # submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')

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
    
    def __repr__(self):
        return f'<Questionnaire {self.id} {self.type} {self.score}分 {self.level}>'
    
# 新增的 Answer 模型
class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    
    # 关联问题和医生
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 回答内容和时间
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 建立关系
    question = db.relationship('Question', backref='answers', lazy=True)
    doctor = db.relationship('User', backref='answers_by_doctor', lazy=True)
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'
    
# 修改 Question 模型
class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='questions', lazy=True)
    
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 状态字段改为 'pending'、'answered' 等
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f'<Question {self.id} by {self.user.name}>'