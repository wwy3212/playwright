import subprocess
import json
import os
import re
from datetime import datetime
from extensions import db
from models import TestResult, PyTestCase


class TestRunner:
    """测试执行器"""

    def __init__(self, test_cases_folder=None):
        self.test_cases_folder = test_cases_folder or os.path.join(
            os.path.dirname(__file__), '..', 'test_cases'
        )
        os.makedirs(self.test_cases_folder, exist_ok=True)

    def run_test(self, test_case_id, test_content=None):
        """执行单个测试用例"""

        # 获取测试内容
        if test_content is None:
            test_case = PyTestCase.query.get(test_case_id)
            if not test_case:
                return {'status': 'error', 'message': '测试用例不存在'}
            test_content = test_case.py_content
            file_path = test_case.file_path or f'test_case_{test_case_id}.py'
        else:
            file_path = f'test_case_{test_case_id}.py'

        # 确保目录存在
        os.makedirs(self.test_cases_folder, exist_ok=True)

        # 写入测试文件
        test_file = os.path.join(self.test_cases_folder, file_path)
        # 清理内容，提取纯 Python 代码
        clean_content = self._extract_python_code(test_content)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)

        # 创建 conftest.py
        self._create_conftest()

        # 执行 pytest
        try:
            result = subprocess.run(
                ['pytest', test_file, '--json-report', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=self.test_cases_folder,
                timeout=300  # 5 分钟超时
            )

            # 解析结果
            return self._parse_result(result, test_case_id)

        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'message': '测试执行超时（超过 5 分钟）',
                'test_case_id': test_case_id
            }
        except FileNotFoundError:
            return {
                'status': 'error',
                'message': 'pytest 未安装，请运行：pip install pytest pytest-json-report',
                'test_case_id': test_case_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'test_case_id': test_case_id
            }

    def _extract_python_code(self, content):
        """从 Markdown 代码块中提取 Python 代码"""
        # 如果内容是 markdown 代码块格式，提取其中的 Python 代码
        match = re.search(r'```python\s*(.*?)```', content, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 如果没有代码块标记，尝试清理注释
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            if line.strip().startswith('# 注意：') or line.strip().startswith('# 调用 Claude'):
                continue
            clean_lines.append(line)
        return '\n'.join(clean_lines)

    def _create_conftest(self):
        """创建 pytest 配置文件"""
        conftest_content = '''import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "AI Test Platform"
    }


@pytest.fixture(scope="function")
def page():
    """Pytest fixture for Playwright page"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        context.close()
        browser.close()
'''
        conftest_path = os.path.join(self.test_cases_folder, 'conftest.py')
        with open(conftest_path, 'w', encoding='utf-8') as f:
            f.write(conftest_content)

    def _parse_result(self, subprocess_result, test_case_id):
        """解析 pytest 执行结果"""

        # 尝试读取 JSON 报告
        json_report_path = os.path.join(self.test_cases_folder, '.pytest', 'report.json')
        report_data = None

        if os.path.exists(json_report_path):
            try:
                with open(json_report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
            except:
                pass

        # 确定测试状态
        if subprocess_result.returncode == 0:
            status = 'passed'
        else:
            status = 'failed'

        # 保存结果到数据库
        test_result = TestResult(
            test_case_id=test_case_id,
            status=status,
            error_message=subprocess_result.stderr if subprocess_result.stderr else None,
            duration=self._parse_duration(subprocess_result.stdout),
            output_log=subprocess_result.stdout
        )
        db.session.add(test_result)
        db.session.commit()

        return {
            'status': status,
            'test_case_id': test_case_id,
            'stdout': subprocess_result.stdout,
            'stderr': subprocess_result.stderr,
            'duration': test_result.duration,
            'result_id': test_result.id,
            'report': report_data
        }

    def _parse_duration(self, output):
        """从输出中解析执行时间"""
        match = re.search(r'in ([\d.]+)s', output)
        if match:
            return float(match.group(1))
        return 0.0

    def run_all_tests(self, project_id=None):
        """执行所有测试或指定项目的测试"""
        query = PyTestCase.query
        if project_id:
            nl_case = db.session.query(PyTestCase.nl_case_id).join(
                PyTestCase.nl_test_case
            ).filter_by(project_id=project_id)
            query = query.filter(PyTestCase.nl_case_id.in_(nl_case))

        test_cases = query.all()
        results = []
        for tc in test_cases:
            result = self.run_test(tc.id)
            results.append(result)

        return results
