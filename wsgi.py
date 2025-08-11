from app import create_app, db
from flask_migrate import Migrate

# 创建应用实例
app = create_app()

# ✅ 新增：在应用启动时，自动创建数据库表
# 这一段代码会确保你的数据库表在应用第一次成功部署后自动生成
# 我们使用 try/except 块来确保即使表已经存在也不会报错
with app.app_context():
    try:
        # 这一行会根据你的模型定义自动创建所有表
        db.create_all()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"An error occurred while creating database tables: {e}")
        # 如果你正在使用 flask_migrate，确保它已经初始化
        # migrate = Migrate(app, db)