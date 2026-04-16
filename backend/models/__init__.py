from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    source_path = db.Column(db.String(500))
    source_type = db.Column(db.String(20), default='local')  # 'local' or 'git'
    git_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nl_test_cases = db.relationship('NLTestCase', backref='project', lazy='dynamic', cascade='all, delete-orphan')


class NLTestCase(db.Model):
    __tablename__ = 'nl_test_cases'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    function_id = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    nl_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    py_test_cases = db.relationship('PyTestCase', backref='nl_test_case', lazy='dynamic', cascade='all, delete-orphan')


class PyTestCase(db.Model):
    __tablename__ = 'py_test_cases'

    id = db.Column(db.Integer, primary_key=True)
    nl_case_id = db.Column(db.Integer, db.ForeignKey('nl_test_cases.id'), nullable=False)
    py_content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_results = db.relationship('TestResult', backref='test_case', lazy='dynamic', cascade='all, delete-orphan')


class TestResult(db.Model):
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('py_test_cases.id'), nullable=False)
    status = db.Column(db.String(20))  # 'passed', 'failed', 'skipped', 'error'
    error_message = db.Column(db.Text)
    duration = db.Column(db.Float)
    output_log = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)


class StructuredTestCase(db.Model):
    """结构化测试用例模型 - 支持列表展示和单独管理"""
    __tablename__ = 'structured_test_cases'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    function_id = db.Column(db.String(100), nullable=False)
    scenario = db.Column(db.String(500), nullable=False)  # 测试场景名称
    precondition = db.Column(db.Text)  # 前置条件
    steps = db.Column(db.Text, nullable=False)  # 测试步骤
    expected = db.Column(db.Text, nullable=False)  # 预期结果
    status = db.Column(db.String(20), default='draft')  # 'draft', 'pending', 'passed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', backref=db.backref('structured_cases', lazy='dynamic'))


class Requirement(db.Model):
    """需求文件管理模型"""
    __tablename__ = 'requirements'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)      # 原始文件名
    file_path = db.Column(db.String(500), nullable=False)    # 存储路径
    file_size = db.Column(db.Integer)                        # 文件大小(字节)
    file_type = db.Column(db.String(50))                     # 文件类型
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploader = db.relationship('User', backref='uploads')
    project = db.relationship('Project', backref='requirements')
