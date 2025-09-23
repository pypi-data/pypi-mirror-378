@echo off
chcp 65001 >nul
echo === Celery Worker 启动脚本 (Windows) ===
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 设置环境变量
set PYTHONPATH=%CD%
set PYTHONUNBUFFERED=1
set CELERY_OPTIMIZATION=fair
set CELERY_DISABLE_RATE_LIMITS=True
set CELERY_TASK_SERIALIZER=json
set CELERY_RESULT_SERIALIZER=json
set CELERY_ACCEPT_CONTENT=json

echo 当前工作目录: %CD%
echo Python路径: %PYTHONPATH%
echo.

REM 启动Python脚本
echo 正在启动Celery Worker...
python start_celery_worker.py

echo.
echo Worker已停止
pause