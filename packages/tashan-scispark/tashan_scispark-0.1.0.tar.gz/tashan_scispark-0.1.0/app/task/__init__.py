# 显式导入任务，确保Celery能够发现和注册任务
from .paper_assistant import paper_assistant

# 导出任务列表，供Celery自动发现使用
__all__ = ['paper_assistant']