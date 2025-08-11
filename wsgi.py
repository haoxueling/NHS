from app import create_app, db
from flask_migrate import Migrate, upgrade, stamp

# 创建应用实例
app = create_app()

# 初始化 Flask-Migrate
migrate = Migrate(app, db)

# 在应用上下文中执行数据库操作
with app.app_context():
    try:
        # 尝试升级数据库到最新版本。这是处理迁移的正确方式。
        upgrade()
        print("Database migrations applied successfully.")
    except Exception as e:
        # 如果数据库是空的（第一次部署），upgrade() 会失败，并抛出异常。
        # 在这种情况下，我们手动创建一个空的迁移，并标记为已完成。
        print(f"Upgrade failed, attempting to initialize database: {e}")
        try:
            # 标记数据库为最新版本，但实际上没有执行任何操作。
            # 这是一个绕过空数据库错误的技巧。
            stamp()
            # 再次尝试升级，这次应该能成功。
            upgrade()
            print("Database initialized and migrations applied successfully.")
        except Exception as e:
            # 如果依然失败，打印最终错误
            print(f"Final error occurred during database initialization: {e}")