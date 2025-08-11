from app import create_app

# ✅ 创建应用实例，Gunicorn 将使用这个变量来启动应用
app = create_app()

# 此处不需要 db.create_all()，我们将在部署后手动执行一次
if __name__ == '__main__':
    app.run()