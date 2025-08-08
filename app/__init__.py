import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate  # 导入 Flask-Migrate
from flask_cors import CORS
from app.config import Config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()  # 初始化迁移工具


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')

    # 构建templates绝对路径并验证
    current_file = Path(__file__)
    # 确定项目根目录（假设app文件夹与templates同级）
    project_root = current_file.parent.parent
    template_dir = project_root / "templates"

    # 验证路径存在性，不存在则创建并提示
    if not template_dir.exists():
        template_dir.mkdir(parents=True, exist_ok=True)
        print(f"警告：templates文件夹不存在，已自动创建于 {template_dir}")

    app.template_folder = str(template_dir)

    app.config.from_object(config_class)

    # 配置 JWT 从 Cookie 中获取令牌
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)  # 关联 app 和 db
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # 注册蓝图
    from app.routes.auth import bp as auth_bp
    from app.routes.user import bp as user_bp
    from app.routes.staff import bp as staff_bp
    from app.routes.doctor_ui import bp as doctor_ui_bp
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(doctor_ui_bp)

    return app