import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nhs-secret-key'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/nhs_questionnaire_system'
    # ✅ 修改：从环境变量中获取数据库 URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'nhs-jwt-secret'