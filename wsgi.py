from app import create_app, db
from app.models import * # 确保导入了所有模型

# 创建应用实例
app = create_app()

# 在应用上下文中执行数据库操作
with app.app_context():
    # ⚠️ 关键修改：移除所有迁移逻辑，直接创建或更新数据库表
    # 这会根据你所有的模型定义来创建表，如果表不存在的话
    # 如果你需要从一个完全干净的状态开始，可以先运行 db.drop_all()
    db.drop_all() 
    db.create_all()
    print("Database tables created or updated successfully.")

# 现在应用已准备好，可以直接启动