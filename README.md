# AI 智能测试平台

一个基于 AI 的智能测试平台，使用 Claude API 生成 Playwright 测试用例和代码。

## 功能特性

1. **生成自然语言测试用例** - 分析源代码，生成 Playwright 可读的自然语言测试场景
2. **生成 Python 测试代码** - 将自然语言测试用例转换为 Playwright Python 代码
3. **执行测试用例** - 运行生成的测试用例，实时查看执行日志
4. **测试报告** - 展示测试结果统计和详细执行记录

## 技术栈

- **后端**: Flask + SQLAlchemy
- **前端**: Vue 3 + Element Plus
- **数据库**: SQLite
- **AI**: Claude API
- **测试**: Playwright + pytest

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
playwright install
```

### 2. 配置 Claude API Key

编辑 `backend/config.py`，设置你的 Claude API Key：

```python
CLAUDE_API_KEY = 'your-claude-api-key-here'
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 http://localhost:5000 启动

### 5. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 6. 构建前端生产版本

```bash
cd frontend
npm run build
```

构建后的文件将输出到 `frontend/dist`，后端会自动提供静态文件服务

## 默认登录账号

- 用户名：`admin`
- 密码：`admin`

## API 端点

| 端点 | 说明 |
|------|------|
| POST /api/auth/login | 用户登录 |
| POST /api/auth/logout | 用户登出 |
| GET /api/projects | 获取项目列表 |
| POST /api/projects | 创建项目 |
| POST /api/test-cases/nl | 生成自然语言测试用例 |
| POST /api/test-cases/py/generate | 生成 Python 测试代码 |
| POST /api/execution/run/<id> | 执行测试用例 |
| GET /api/execution/results | 获取测试结果 |

## 项目结构

```
.
├── backend/
│   ├── app.py              # Flask 主应用
│   ├── config.py           # 配置文件
│   ├── extensions.py       # Flask 扩展
│   ├── models/             # 数据模型
│   ├── routes/             # API 路由
│   ├── services/           # 业务服务
│   └── utils/              # 工具函数
└── frontend/
    ├── src/
    │   ├── views/          # 页面组件
    │   ├── components/     # 通用组件
    │   ├── stores/         # 状态管理
    │   └── router/         # 路由配置
    └── package.json
```

## 注意事项

1. 首次启动时会自动创建 admin 用户
2. 需要配置 Claude API Key 才能使用 AI 生成功能
3. 执行测试需要安装 Playwright 浏览器：`playwright install`
4. 测试用例保存在 `backend/test_cases` 目录

## License

MIT
