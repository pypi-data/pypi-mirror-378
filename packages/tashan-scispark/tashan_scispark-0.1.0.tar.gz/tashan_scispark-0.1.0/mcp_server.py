#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TaShan SciSpark MCP Server
基于MCP协议的假设生成框架服务器
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 抑制第三方库的警告
from suppress_warnings import apply_warning_filters
apply_warning_filters()

try:
    from fastmcp import FastMCP
except ImportError:
    print("请安装fastmcp: pip install fastmcp")
    sys.exit(1)

# 导入项目模块
from tashan_scispark.main import main as astro_main
from tashan_scispark.app.utils.tool import (
    get_related_keyword, 
    remove_number_prefix, 
    extract_hypothesis, 
    search_releated_paper, 
    extract_technical_entities, 
    extract_message, 
    paper_compression, 
    review_mechanism, 
    extract_message_review, 
    extract_message_review_moa
)
from tashan_scispark.app.utils.arxiv_api import search_paper
from tashan_scispark.app.utils.llm_api import call_with_deepseek, call_with_qwenmax
from tashan_scispark.app.core.moa import moa_idea_iteration, moa_table
from tashan_scispark.app.core.config import OUTPUT_PATH
from tashan_scispark.app.task.paper_assistant import paper_assistant

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)  # 使用stderr避免与stdio传输冲突
    ]
)
logger = logging.getLogger(__name__)

# 初始化FastMCP服务器
mcp = FastMCP("TaShan SciSpark")

class TaskManager:
    """任务管理器，用于跟踪长时间运行的任务"""
    
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
    
    def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """创建新任务"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}_{int(datetime.now().timestamp())}"
        
        self.tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "params": params,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, status: str, result: Any = None, error: str = None):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            if result is not None:
                self.tasks[task_id]["result"] = result
            if error is not None:
                self.tasks[task_id]["error"] = error

# 全局任务管理器
task_manager = TaskManager()

@mcp.tool
def search_papers(keyword: str, limit: int = 5) -> Dict[str, Any]:
    """
    搜索学术论文
    
    Args:
        keyword: 搜索关键词
        limit: 返回论文数量限制，默认5篇
    
    Returns:
        包含论文列表的字典
    """
    try:
        logger.info(f"搜索论文，关键词: {keyword}, 限制: {limit}")
        
        # 获取相关关键词 - 使用try-except处理可能的异步问题
        try:
            related_keywords = get_related_keyword(keyword)
        except Exception as e:
            logger.warning(f"获取相关关键词失败，使用原关键词: {str(e)}")
            related_keywords = []
        
        all_keywords = [keyword] + related_keywords
        
        # 搜索论文
        papers = search_paper(Keywords=all_keywords, Limit=limit)
        
        # 格式化结果
        formatted_papers = []
        for paper in papers:
            formatted_papers.append({
                "title": paper.get("title", ""),
                "abstract": paper.get("abstract", ""),
                "authors": paper.get("authors", []),
                "published": paper.get("published", ""),
                "url": paper.get("url", ""),
                "topic": paper.get("topic", keyword)
            })
        
        return {
            "success": True,
            "keyword": keyword,
            "related_keywords": related_keywords,
            "papers": formatted_papers,
            "count": len(formatted_papers)
        }
        
    except Exception as e:
        logger.error(f"搜索论文时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
            "papers": [],
            "count": 0
        }

@mcp.tool
def extract_keywords(text: str, split_section: str = "Paper Abstract") -> Dict[str, Any]:
    """
    从文本中提取技术关键词
    
    Args:
        text: 要分析的文本内容
        split_section: 文本分割部分，默认为"Paper Abstract"
    
    Returns:
        包含提取的关键词列表的字典
    """
    try:
        logger.info(f"提取技术关键词，文本长度: {len(text)}")
        
        # 创建临时文件
        temp_file = f"temp_extract_{int(datetime.now().timestamp())}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        try:
            # 提取技术实体
            keywords, _ = extract_technical_entities(temp_file, split_section)
            
            # 格式化结果
            formatted_keywords = []
            for kw in keywords:
                formatted_keywords.append({
                    "entity": kw.get("entity", ""),
                    "relevance": kw.get("relevance", 0),
                    "count": kw.get("count", 0)
                })
            
            return {
                "success": True,
                "keywords": formatted_keywords,
                "count": len(formatted_keywords)
            }
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"提取关键词时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "keywords": [],
            "count": 0
        }

@mcp.tool
def generate_research_idea(keyword: str, paper_count: int = 3) -> Dict[str, Any]:
    """
    生成研究想法（异步任务）
    
    Args:
        keyword: 研究关键词
        paper_count: 参考论文数量，默认3篇
    
    Returns:
        包含任务ID的字典，可用于查询任务状态
    """
    try:
        logger.info(f"创建研究想法生成任务，关键词: {keyword}")
        
        # 创建任务
        task_id = task_manager.create_task("generate_research_idea", {
            "keyword": keyword,
            "paper_count": paper_count
        })
        
        # 启动Celery异步任务
        celery_task = paper_assistant.delay(keyword, paper_count)
        
        # 存储Celery任务ID以便后续跟踪
        task_manager.tasks[task_id]["celery_task_id"] = celery_task.id
        
        # 更新任务状态为运行中
        task_manager.update_task(task_id, "running")
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "研究想法生成任务已启动，请使用get_task_status查询进度"
        }
        
    except Exception as e:
        logger.error(f"创建研究想法生成任务时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def _generate_research_idea_async(task_id: str, keyword: str, paper_count: int):
    """异步生成研究想法"""
    try:
        task_manager.update_task(task_id, "running")
        
        # 创建模拟任务对象，兼容main.py中的task.request.id访问模式
        class MockTask:
            def __init__(self, task_id: str):
                self.id = task_id
                # 创建request对象以兼容getattr(task, 'request', {}).get('id')的访问模式
                self.request = type('Request', (), {'id': task_id})()
        
        mock_task = MockTask(task_id)
        
        # 调用主要的研究想法生成函数
        result = astro_main(
            task=mock_task,
            user_id="mcp_user",
            Keyword=keyword,
            SearchPaperNum=paper_count
        )
        
        task_manager.update_task(task_id, "completed", result)
        logger.info(f"任务 {task_id} 完成")
        
    except Exception as e:
        error_msg = str(e)
        task_manager.update_task(task_id, "failed", error=error_msg)
        logger.error(f"任务 {task_id} 失败: {error_msg}")

@mcp.tool
def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
    
    Returns:
        包含任务状态信息的字典
    """
    try:
        task = task_manager.get_task(task_id)
        if not task:
            return {
                "success": False,
                "error": f"任务 {task_id} 不存在"
            }
        
        # 如果有Celery任务ID，检查Celery任务状态
        if "celery_task_id" in task:
            celery_task_id = task["celery_task_id"]
            try:
                from app.core.celery import celery_app
                celery_task = celery_app.AsyncResult(celery_task_id)
                
                if celery_task.state == "SUCCESS":
                    # 更新任务状态为完成
                    task_manager.update_task(task_id, "completed", celery_task.result)
                elif celery_task.state == "FAILURE":
                    # 更新任务状态为失败
                    task_manager.update_task(task_id, "failed", error=str(celery_task.info))
                elif celery_task.state == "PENDING":
                    # 任务还在等待中
                    task_manager.update_task(task_id, "pending")
                elif celery_task.state == "STARTED":
                    # 任务正在运行
                    task_manager.update_task(task_id, "running")
                    
                # 重新获取更新后的任务状态
                task = task_manager.get_task(task_id)
                
            except Exception as e:
                logger.error(f"检查Celery任务状态时出错: {str(e)}")
        
        return {
            "success": True,
            "task": task
        }
        
    except Exception as e:
        logger.error(f"获取任务状态时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool
def review_research_idea(topic: str, draft: str) -> Dict[str, Any]:
    """
    评审研究想法
    
    Args:
        topic: 研究主题
        draft: 研究想法草稿
    
    Returns:
        包含评审结果的字典
    """
    try:
        logger.info(f"评审研究想法，主题: {topic}")
        
        # 创建模拟任务对象，兼容main.py中的task.request.id访问模式
        class MockTask:
            def __init__(self):
                self.id = f"review_{int(datetime.now().timestamp())}"
                # 创建request对象以兼容getattr(task, 'request', {}).get('id')的访问模式
                self.request = type('Request', (), {'id': self.id})()
        
        mock_task = MockTask()
        
        # 调用评审机制
        review_result = review_mechanism(
            topic=topic,
            draft=draft,
            user_id="mcp_user",
            task=mock_task
        )
        
        return {
            "success": True,
            "topic": topic,
            "review_result": review_result,
            "task_id": mock_task.id
        }
        
    except Exception as e:
        logger.error(f"评审研究想法时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "topic": topic
        }

@mcp.tool
def compress_paper_content(title: str, abstract: str, content: str = "") -> Dict[str, Any]:
    """
    压缩论文内容
    
    Args:
        title: 论文标题
        abstract: 论文摘要
        content: 论文正文内容（可选）
    
    Returns:
        包含压缩结果的字典
    """
    try:
        logger.info(f"压缩论文内容，标题: {title[:50]}...")
        
        # 构建论文对象
        paper = {
            "title": title,
            "abstract": abstract,
            "content": content
        }
        
        # 调用论文压缩功能
        compressed_result = paper_compression(paper)
        
        return {
            "success": True,
            "original_title": title,
            "compressed_result": compressed_result
        }
        
    except Exception as e:
        logger.error(f"压缩论文内容时出错: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "original_title": title
        }

@mcp.tool
def get_server_info() -> Dict[str, Any]:
    """
    获取服务器信息
    
    Returns:
        包含服务器信息的字典
    """
    return {
        "name": "TaShan SciSpark MCP Server",
        "version": "1.0.0",
        "description": "学术论文研究助手的MCP服务器",
        "capabilities": [
            "search_papers - 搜索学术论文",
            "extract_keywords - 提取技术关键词",
            "generate_research_idea - 生成研究想法（异步）",
            "get_task_status - 获取任务状态",
            "review_research_idea - 评审研究想法",
            "compress_paper_content - 压缩论文内容"
        ],
        "active_tasks": len(task_manager.tasks),
        "output_path": OUTPUT_PATH
    }

def main():
    """MCP服务器主入口函数"""
    logger.info("启动TaShan SciSpark MCP服务器")
    
    # 使用stdio传输启动服务器
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()