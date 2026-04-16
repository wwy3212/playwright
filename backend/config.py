import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ai-test-platform-secret-key-2026'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///test_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session 配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Claude API 配置
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') or 'sk-QEZfNSTA5xAvylvglwA3b5IiWcsb22FouP8meg8Iq55qpPeg'
    CLAUDE_MODEL = 'qwen3.5-plus'
    CLAUDE_BASE_URL = 'https://gpt-agent.cc'

    # 文件存储配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    TEST_CASES_FOLDER = os.path.join(os.path.dirname(__file__), 'test_cases')
    PROJECTS_FOLDER = os.path.join(os.path.dirname(__file__), 'projects')
    REQUIREMENTS_FOLDER = os.path.join(os.path.dirname(__file__), 'requirements')

    # 确保目录存在
    for folder in [UPLOAD_FOLDER, TEST_CASES_FOLDER, PROJECTS_FOLDER, REQUIREMENTS_FOLDER]:
        os.makedirs(folder, exist_ok=True)
