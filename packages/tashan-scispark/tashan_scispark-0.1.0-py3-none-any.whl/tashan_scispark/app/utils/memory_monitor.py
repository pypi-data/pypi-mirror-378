#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
内存监控和管理工具模块
用于监控Celery任务执行过程中的内存使用情况，并提供内存清理功能
"""

import gc
import os
import psutil
import logging
from functools import wraps
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryMonitor:
    """内存监控器类"""
    
    def __init__(self, max_memory_mb: int = 1024):
        """
        初始化内存监控器
        
        Args:
            max_memory_mb: 最大内存限制（MB）
        """
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> Dict[str, float]:
        """
        获取当前内存使用情况
        
        Returns:
            包含内存使用信息的字典
        """
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # 物理内存（MB）
                'vms_mb': memory_info.vms / 1024 / 1024,  # 虚拟内存（MB）
                'percent': memory_percent,  # 内存使用百分比
                'available_mb': psutil.virtual_memory().available / 1024 / 1024  # 可用内存（MB）
            }
        except Exception as e:
            logger.error(f"获取内存使用情况失败: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'available_mb': 0}
    
    def check_memory_limit(self) -> bool:
        """
        检查是否超过内存限制
        
        Returns:
            True表示超过限制，False表示正常
        """
        current_memory = self.get_memory_usage()
        return current_memory['rss_mb'] > self.max_memory_mb
    
    def force_garbage_collection(self) -> int:
        """
        强制执行垃圾回收
        
        Returns:
            回收的对象数量
        """
        logger.info("执行强制垃圾回收...")
        collected = gc.collect()
        logger.info(f"垃圾回收完成，回收了 {collected} 个对象")
        return collected
    
    def log_memory_status(self, stage: str = ""):
        """
        记录当前内存状态
        
        Args:
            stage: 当前执行阶段的描述
        """
        memory_info = self.get_memory_usage()
        memory_increase = memory_info['rss_mb'] - self.initial_memory['rss_mb']
        
        logger.info(f"[{stage}] 内存状态:")
        logger.info(f"  物理内存: {memory_info['rss_mb']:.2f} MB")
        logger.info(f"  虚拟内存: {memory_info['vms_mb']:.2f} MB")
        logger.info(f"  内存占用: {memory_info['percent']:.2f}%")
        logger.info(f"  可用内存: {memory_info['available_mb']:.2f} MB")
        logger.info(f"  内存增长: {memory_increase:.2f} MB")
        
        # 如果内存使用过高，发出警告
        if memory_info['rss_mb'] > self.max_memory_mb * 0.8:
            logger.warning(f"内存使用接近限制！当前: {memory_info['rss_mb']:.2f} MB, 限制: {self.max_memory_mb} MB")


def memory_monitor_decorator(max_memory_mb: int = 1024, cleanup_threshold: float = 0.8):
    """
    内存监控装饰器
    
    Args:
        max_memory_mb: 最大内存限制（MB）
        cleanup_threshold: 内存清理阈值（0-1之间的比例）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = MemoryMonitor(max_memory_mb)
            monitor.log_memory_status(f"开始执行 {func.__name__}")
            
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 检查内存使用
                current_memory = monitor.get_memory_usage()
                if current_memory['rss_mb'] > max_memory_mb * cleanup_threshold:
                    logger.warning(f"内存使用过高，执行清理: {current_memory['rss_mb']:.2f} MB")
                    monitor.force_garbage_collection()
                
                monitor.log_memory_status(f"完成执行 {func.__name__}")
                return result
                
            except Exception as e:
                monitor.log_memory_status(f"执行 {func.__name__} 时出错")
                logger.error(f"函数执行出错: {e}")
                raise
            
        return wrapper
    return decorator


def cleanup_large_objects(*objects):
    """
    清理大对象并强制垃圾回收
    
    Args:
        *objects: 要清理的对象
    """
    logger.info("开始清理大对象...")
    
    for obj in objects:
        if obj is not None:
            try:
                # 如果是列表或字典，清空内容
                if isinstance(obj, list):
                    obj.clear()
                elif isinstance(obj, dict):
                    obj.clear()
                # 删除对象引用
                del obj
            except Exception as e:
                logger.warning(f"清理对象时出错: {e}")
    
    # 强制垃圾回收
    collected = gc.collect()
    logger.info(f"对象清理完成，回收了 {collected} 个对象")


def get_system_memory_info() -> Dict[str, Any]:
    """
    获取系统内存信息
    
    Returns:
        系统内存信息字典
    """
    try:
        memory = psutil.virtual_memory()
        return {
            'total_gb': memory.total / 1024 / 1024 / 1024,
            'available_gb': memory.available / 1024 / 1024 / 1024,
            'used_gb': memory.used / 1024 / 1024 / 1024,
            'percent': memory.percent,
            'free_gb': memory.free / 1024 / 1024 / 1024
        }
    except Exception as e:
        logger.error(f"获取系统内存信息失败: {e}")
        return {}


if __name__ == "__main__":
    # 测试内存监控功能
    monitor = MemoryMonitor(512)  # 512MB限制
    monitor.log_memory_status("测试开始")
    
    # 模拟内存使用
    test_data = [i for i in range(100000)]
    monitor.log_memory_status("创建测试数据后")
    
    # 清理数据
    cleanup_large_objects(test_data)
    monitor.log_memory_status("清理数据后")
    
    # 显示系统内存信息
    sys_info = get_system_memory_info()
    print(f"系统内存信息: {sys_info}")