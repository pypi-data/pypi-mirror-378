@echo off
chcp 65001 >nul
echo TaShan SciSpark MCP Server 依赖安装脚本
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    echo 请先安装Python 3.10或更高版本
    pause
    exit /b 1
)

echo 正在安装MCP服务器依赖...
echo.

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装FastMCP
echo 安装FastMCP...
python -m pip install fastmcp

REM 安装其他依赖
if exist "requirements_mcp.txt" (
    echo 安装项目依赖...
    python -m pip install -r requirements_mcp.txt
) else (
    echo 警告: requirements_mcp.txt文件不存在，跳过依赖安装
)

echo.
echo 依赖安装完成！
echo.
echo 现在可以运行以下命令启动MCP服务器:
echo   run_mcp.bat
echo 或者:
echo   python start_mcp_server.py --mode stdio
echo.
pause