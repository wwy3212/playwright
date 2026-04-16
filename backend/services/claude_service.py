import os
import anthropic
from config import Config


class ClaudeService:
    """Claude API 服务类"""

    def __init__(self):
        self.client = None
        self.api_key = Config.CLAUDE_API_KEY
        self.model = Config.CLAUDE_MODEL
        self.base_url = Config.CLAUDE_BASE_URL
        self._init_client()

    def _init_client(self):
        """初始化 Claude API 客户端"""
        if self.api_key and self.api_key != 'your-claude-api-key-here':
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None

    def update_api_key(self, api_key):
        """更新 API Key"""
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)

    def is_configured(self):
        """检查 API 是否已配置"""
        return self.client is not None

    def analyze_code_and_generate_nl(self, source_code, function_id, description):
        """分析源代码并生成自然语言测试用例"""

        prompt = f"""你是一个专业的测试工程师。请分析以下源代码，为指定功能生成详细的自然语言测试用例。

功能 ID: {function_id}
功能描述：{description}

源代码：
```
{source_code}
```

请生成 Playwright 可以理解的自然语言测试用例，格式如下：

## 测试场景 1: [场景名称]
- 前置条件：[执行测试前需要满足的条件]
- 测试步骤：
  1. [步骤 1]
  2. [步骤 2]
  3. [步骤 3]
- 预期结果：[期望的测试结果]

## 测试场景 2: [场景名称]
...

要求：
1. 测试用例应该覆盖主要功能和边界情况
2. 步骤描述要清晰具体，可以被 Playwright 执行
3. 包含适当的断言点
4. 考虑异常场景和错误处理

请生成至少 3 个测试场景。"""

        if not self.client:
            return self._generate_mock_nl(prompt)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"调用 Claude API 失败：{str(e)}"

    def generate_pytest_code(self, nl_test_case, page_object_code=None):
        """将自然语言测试用例转换为 Playwright Python 代码"""

        # 构建页面对象代码部分
        page_object_section = ""
        if page_object_code:
            page_object_section = f"页面对象代码：\n```\n{page_object_code}\n```\n"

        prompt = f"""你是一个自动化测试专家。请将以下自然语言测试用例转换为 Playwright Python 测试代码。

自然语言测试用例：
```
{nl_test_case}
```

{page_object_section}
要求：
1. 使用 pytest 测试框架
2. 使用 playwright.sync_api
3. 采用页面对象模式 (Page Object Pattern)
4. 包含适当的断言
5. 添加必要的等待和错误处理
6. 使用 pytest fixture 管理浏览器上下文
7. 代码要有良好的注释

请生成完整的、可直接运行的测试代码。"""

        if not self.client:
            return self._generate_mock_code(prompt)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"# 调用 Claude API 失败：{str(e)}"

    def _generate_mock_nl(self, prompt):
        """生成模拟的自然语言测试用例（当 API 未配置时）"""
        return f"""## 测试场景 1: 功能 {prompt.split('功能 ID:')[1].split(chr(10))[0].strip()} - 正常流程
- 前置条件：用户已登录，系统正常运行
- 测试步骤：
  1. 打开应用程序
  2. 导航到功能页面
  3. 执行主要操作
  4. 验证操作结果
- 预期结果：功能正常工作，显示成功消息

## 测试场景 2: 边界值测试
- 前置条件：用户已登录
- 测试步骤：
  1. 输入边界值数据
  2. 提交表单
  3. 验证处理结果
- 预期结果：系统正确处理边界值

## 测试场景 3: 异常场景测试
- 前置条件：用户已登录
- 测试步骤：
  1. 输入无效数据
  2. 提交表单
  3. 验证错误提示
- 预期结果：系统显示适当的错误消息

注意：这是模拟输出，请配置 Claude API Key 以获取真实的 AI 生成结果。"""

    def _generate_mock_code(self, prompt):
        """生成模拟的测试代码（当 API 未配置时）"""
        return '''# 注意：这是模拟生成的代码，请配置 Claude API Key 以获取真实的 AI 生成结果

import pytest
from playwright.sync_api import Page, expect


class TestGeneratedFeature:
    """自动生成的测试类"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """测试前设置"""
        page.goto("http://localhost:3000")
        # 登录操作
        page.fill('input[name="username"]', "admin")
        page.fill('input[name="password"]', "admin")
        page.click('button[type="submit"]')
        yield page

    def test_feature_normal_flow(self, page: Page):
        """测试功能正常流程"""
        # 导航到功能页面
        page.click('nav a[href="/feature"]')

        # 执行主要操作
        page.fill('input[name="input_field"]', "test data")
        page.click('button.submit-btn')

        # 验证结果
        expect(page.locator('.success-message')).to_be_visible()
        assert page.url == "http://localhost:3000/success"

    def test_feature_boundary_value(self, page: Page):
        """测试边界值"""
        # 输入边界值
        page.fill('input[name="input_field"]', "a" * 255)  # 最大长度
        page.click('button.submit-btn')

        # 验证
        expect(page.locator('.result')).to_be_visible()

    def test_feature_error_handling(self, page: Page):
        """测试错误处理"""
        # 输入无效数据
        page.fill('input[name="input_field"]', "")
        page.click('button.submit-btn')

        # 验证错误消息
        expect(page.locator('.error-message')).to_be_visible()
'''
