import os
from pathlib import Path
from flask import Flask, g, session
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
    # 确定项目根目录（假设 app 文件夹与 templates 和 static 同级）
    project_root = Path(__file__).parent.parent
    
    # 显式指定 static 和 templates 文件夹的路径
    static_folder_path = str(project_root / "static")
    template_folder_path = str(project_root / "templates")
    
    # 创建 Flask 应用实例，并传入正确的路径
    app = Flask(__name__,
                static_folder=static_folder_path,
                template_folder=template_folder_path)

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
    
    # =========================================================
    # ✅ 关键修改点: 动态配置数据库 URI
    # =========================================================
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # 在 Render 上，使用环境变量中的 PostgreSQL 连接字符串，并指定 psycopg2 驱动
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace(
            'postgresql://', 'postgresql+psycopg2://'
        )
        # 为生产环境配置连接池，提高性能和稳定性
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
        # =========================================================
        # ✅ 新增配置: 解决连接失效问题
        # =========================================================
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            # 在使用连接前，先 ping 数据库，确保连接是活跃的
            'pool_pre_ping': True,
            # 每隔 30 分钟回收一次连接，防止因长时间不活动而失效
            'pool_recycle': 1800  # 1800秒 = 30分钟
        }
        # =========================================================
    else:
        # 在本地开发，使用你原有的 MySQL 连接字符串
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/nhs_questionnaire_system'
    # =========================================================

    # 配置 JWT 从 Cookie 中获取令牌
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)  # 关联 app 和 db
    jwt.init_app(app)
    CORS(app, supports_credentials=True)
    
    @app.before_request
    def load_logged_in_user():
        # """在每个请求之前加载登录用户信息。"""
        from app.models import User
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            # 假设你的 User 模型可以通过 id 查询
            g.user = User.query.get(user_id)
    

    # 注册蓝图
    from app.routes.auth import bp as auth_bp
    from app.routes.user import bp as user_bp
    from app.routes.staff import bp as staff_bp
    from app.routes.doctor_ui import bp as doctor_ui_bp
    from app.routes.statistics_routes import statistics_bp
    from app.routes.user_q import user_q_bp
    from app.routes.doctor_a import doctor_a_bp
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(doctor_ui_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(user_q_bp, url_prefix='/user')
    app.register_blueprint(doctor_a_bp, url_prefix='/doctor')

    return app