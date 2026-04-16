@echo off
echo ========================================
echo AI 智能测试平台 - 安装和启动脚本
echo ========================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

echo.
echo [1/5] 安装后端依赖...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 后端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [2/5] 安装 Playwright 浏览器...
playwright install chromium

echo.
echo [3/5] 安装前端依赖...
cd ..\frontend
call npm install
if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
)

echo.
echo [4/5] 构建前端...
call npm run build

echo.
echo [5/5] 启动后端服务...
cd ..\backend
start http://localhost:5000
python app.py

pause
