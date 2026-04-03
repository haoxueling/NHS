import os
from pathlib import Path
from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config


# Initialise the extension
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()  # Initialise the migration tool


def create_app(config_class=Config):
    # Specify the project root directory (assuming the app folder is at the same level as templates and static)
    project_root = Path(__file__).parent.parent
    
    # Explicitly specify the paths for the static and templates folders
    static_folder_path = str(project_root / "static")
    template_folder_path = str(project_root / "templates")
    
    # Create a Flask application instance and pass in the correct path.
    app = Flask(__name__,
                static_folder=static_folder_path,
                template_folder=template_folder_path)

    # Construct absolute paths for templates and validate them
    current_file = Path(__file__)
    # Determine the project root directory (assuming the app folder is at the same level as the templates folder)
    project_root = current_file.parent.parent
    template_dir = project_root / "templates"

    # Verify the existence of the path; if it does not exist, create it and provide a prompt.
    if not template_dir.exists():
        template_dir.mkdir(parents=True, exist_ok=True)
        print(f"Warning: The templates folder does not exist and has been automatically created at {template_dir}")

    app.template_folder = str(template_dir)

    app.config.from_object(config_class)
    
    
    # Dynamically configure database URI
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # On Render, utilise the PostgreSQL connection string from the environment variables and specify the psycopg2 driver.
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace(
            'postgresql://', 'postgresql+psycopg2://'
        )
        # Configure connection pools for production environments to enhance performance and stability.
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
        
        # Resolving connection failure issues
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            # Before using the connection, ping the database to ensure the connection is active.
            'pool_pre_ping': True,
            # Recover the connection every 30 minutes to prevent it from expiring due to prolonged inactivity.
            'pool_recycle': 1800  
        }
    else:
        # When developing locally, use the existing MySQL connection string.
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/nhs_questionnaire_system'
    # Configure JWT to retrieve the token from the cookie
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    # Initialisation of extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Bind the migration tool to the app and database
    jwt.init_app(app)
    CORS(app, supports_credentials=True)
    
    @app.before_request
    def load_logged_in_user():
        from app.models import User
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = User.query.get(user_id)
    

    # Register blueprints
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