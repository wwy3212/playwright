"""
AI 智能测试平台 - Flask 后端应用
"""
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import db, login_manager
from models import User
from routes import auth, projects, test_cases, execution


def create_app(config_class=Config):
    """应用工厂函数"""

    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    CORS(app, supports_credentials=True)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝图
    app.register_blueprint(auth)
    app.register_blueprint(projects)
    app.register_blueprint(test_cases)
    app.register_blueprint(execution)

    # 用户加载回调
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 初始化 admin 用户
        init_admin()

    # API 健康检查
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'AI 智能测试平台运行中'})

    # 前端路由 fallback
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    return app


def init_admin():
    """初始化 admin 用户"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("已创建默认管理员用户：admin / admin")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
