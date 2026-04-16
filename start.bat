@echo off
echo ========================================
echo AI 智能测试平台 - 快速启动
echo ========================================

cd backend
start http://localhost:5000
echo 正在启动后端服务...
echo 访问地址：http://localhost:5000
echo 登录账号：admin / admin
echo.
python app.py

pause
