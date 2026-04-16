"""Routes 包初始化"""
from .auth import auth
from .projects import projects
from .test_cases import test_cases
from .execution import execution
from .requirements import requirements

__all__ = ['auth', 'projects', 'test_cases', 'execution', 'requirements']
