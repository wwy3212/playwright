"""认证路由"""
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required
from models import User
from extensions import db

auth = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        session.permanent = True
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'id': user.id,
                'username': user.username
            }
        })

    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    logout_user()
    return jsonify({'success': True, 'message': '已退出登录'})


@auth.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """获取当前用户信息"""
    from flask_login import current_user
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username
        }
    })


@auth.route('/init', methods=['POST'])
def init_admin():
    """初始化 admin 用户（仅用于首次启动）"""
    # 检查是否已有用户
    if User.query.first():
        return jsonify({'success': False, 'message': '用户已存在'}), 400

    admin = User(username='admin')
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()

    return jsonify({'success': True, 'message': 'admin 用户创建成功'})
