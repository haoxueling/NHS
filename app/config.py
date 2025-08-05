import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nhs-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/nhs_questionnaire_system'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'nhs-jwt-secret'