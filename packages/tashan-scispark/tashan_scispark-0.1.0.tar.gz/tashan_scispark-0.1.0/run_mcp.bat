@echo off
chcp 65001 >nul
echo TaShan SciSpark MCP Server 启动脚本
echo =====================================

REM 设置环境变量
set PYTHONPATH=%~dp0
set PYTHONIOENCODING=utf-8

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查是否存在mcp_server.py
if not exist "mcp_server.py" (
    echo 错误: mcp_server.py文件不存在
    pause
    exit /b 1
)

echo 正在启动AstroInsight MCP服务器...
echo 使用Ctrl+C停止服务器
echo.

REM 启动MCP服务器
python mcp_server.py

echo.
echo 服务器已停止
pause