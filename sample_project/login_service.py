"""
示例登录模块 - 用于演示 AI 测试平台功能
"""


class LoginService:
    """登录服务类"""

    def __init__(self):
        self.users = {
            'admin': 'admin123',
            'user1': 'password1',
            'user2': 'password2'
        }
        self.logged_in_users = set()

    def login(self, username, password):
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            dict: 登录结果，包含 success 和 message
        """
        if not username or not password:
            return {'success': False, 'message': '用户名和密码不能为空'}

        if username not in self.users:
            return {'success': False, 'message': '用户不存在'}

        if self.users[username] != password:
            return {'success': False, 'message': '密码错误'}

        if username in self.logged_in_users:
            return {'success': False, 'message': '该用户已登录'}

        self.logged_in_users.add(username)
        return {'success': True, 'message': '登录成功', 'username': username}

    def logout(self, username):
        """用户登出"""
        if username in self.logged_in_users:
            self.logged_in_users.remove(username)
            return {'success': True, 'message': '登出成功'}
        return {'success': False, 'message': '用户未登录'}

    def is_logged_in(self, username):
        """检查用户是否已登录"""
        return username in self.logged_in_users


class UserRegistration:
    """用户注册类"""

    def __init__(self):
        self.users = {}
        self.min_password_length = 6

    def register(self, username, password, email):
        """
        用户注册

        Args:
            username: 用户名
            password: 密码
            email: 邮箱

        Returns:
            dict: 注册结果
        """
        # 验证用户名
        if not username or len(username) < 3:
            return {'success': False, 'message': '用户名至少需要 3 个字符'}

        if len(username) > 20:
            return {'success': False, 'message': '用户名不能超过 20 个字符'}

        # 验证密码
        if not password or len(password) < self.min_password_length:
            return {'success': False, 'message': f'密码至少需要 {self.min_password_length} 个字符'}

        # 验证邮箱
        if not email or '@' not in email:
            return {'success': False, 'message': '请输入有效的邮箱地址'}

        # 检查用户名是否已存在
        if username in self.users:
            return {'success': False, 'message': '用户名已存在'}

        # 创建用户
        self.users[username] = {
            'password': password,
            'email': email
        }

        return {'success': True, 'message': '注册成功', 'username': username}
