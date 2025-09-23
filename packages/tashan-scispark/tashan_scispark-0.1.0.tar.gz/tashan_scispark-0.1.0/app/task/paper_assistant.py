from tashan_scispark.app.core.celery import celery_app
import sys
import os
import gc
import logging

# 简化路径配置，确保模块能够正确导入
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 延迟导入main模块，避免循环导入
def get_main_function():
    """
    延迟导入main函数，避免启动时的循环导入问题
    """
    try:
        from main import main
        return main
    except ImportError as e:
        logging.error(f"导入main模块失败: {e}")
        raise

# 导入内存监控工具
from tashan_scispark.app.utils.memory_monitor import MemoryMonitor, cleanup_large_objects, memory_monitor_decorator

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
@memory_monitor_decorator(max_memory_mb=1024, cleanup_threshold=0.8)
def paper_assistant(self, keyword, paper_count):
    """
    Celery任务：生成研究想法
    集成内存监控和清理机制
    
    Args:
        keyword: 研究关键词
        paper_count: 论文数量
    
    Returns:
        任务执行结果
    """
    monitor = MemoryMonitor(max_memory_mb=1024)
    result = None
    
    try:
        logger.info(f"开始执行paper_assistant任务: keyword={keyword}, paper_count={paper_count}")
        monitor.log_memory_status("任务开始")
        
        # 更新任务状态 - 简化meta信息避免序列化问题
        self.update_state(state='PROGRESS', meta={'progress': 0})
        
        # 获取main函数并调用，参数顺序为：task, user_id, Keyword, SearchPaperNum
        main_func = get_main_function()
        result = main_func(task=self, user_id="mcp_user", Keyword=keyword, SearchPaperNum=paper_count)
        
        monitor.log_memory_status("main函数执行完成")
        
        # 更新任务状态为完成 - 简化meta信息
        self.update_state(state='SUCCESS', meta={'progress': 100})
        
        logger.info("paper_assistant任务执行成功")
        return result
        
    except Exception as e:
        logger.error(f"生成研究想法时发生错误: {e}")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误详情: {str(e)}")
        
        # 创建简单的异常信息，避免序列化问题
        error_message = str(e)
        error_type = type(e).__name__
        
        # 更新任务状态为失败，使用简单的字符串信息
        try:
            # 使用更简单的状态更新，避免复杂对象序列化
            self.update_state(
                state='FAILURE', 
                meta={
                    'error': f"{error_type}: {error_message}",
                    'stage': 'failed',
                    'progress': 0
                }
            )
        except Exception as update_error:
            logger.error(f"更新任务状态失败: {update_error}")
            # 如果状态更新失败，尝试更简单的方式
            try:
                self.update_state(state='FAILURE', meta={'error': 'Task failed'})
            except:
                pass  # 忽略状态更新失败
        
        # 创建一个新的简单异常来重新抛出，避免原始异常的序列化问题
        raise Exception(f"{error_type}: {error_message}")
    
    finally:
        # 最终清理
        monitor.log_memory_status("任务结束前清理")
        
        # 强制垃圾回收
        collected = gc.collect()
        logger.info(f"任务结束，执行垃圾回收，回收了 {collected} 个对象")
        
        monitor.log_memory_status("任务完全结束")
