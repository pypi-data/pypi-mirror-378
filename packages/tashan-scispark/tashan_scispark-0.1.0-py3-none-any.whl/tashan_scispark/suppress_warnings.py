#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
警告抑制脚本
用于过滤第三方库（如agentscope）产生的SQLAlchemy弃用警告
"""

import warnings
import sys

def suppress_sqlalchemy_warnings():
    """
    抑制SQLAlchemy相关的弃用警告
    主要针对agentscope包中使用的过时API
    """
    # 抑制SQLAlchemy的MovedIn20Warning警告
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module=".*agentscope.*",
        message=".*declarative_base.*"
    )
    
    # 抑制所有SQLAlchemy的MovedIn20Warning
    try:
        from sqlalchemy.exc import MovedIn20Warning
        warnings.filterwarnings("ignore", category=MovedIn20Warning)
    except ImportError:
        # 如果SQLAlchemy未安装，忽略
        pass

def apply_warning_filters():
    """
    应用所有警告过滤器
    在项目启动时调用此函数
    """
    suppress_sqlalchemy_warnings()
    
    # 可以在这里添加其他警告过滤器
    print("Warning filters applied successfully", file=sys.stderr)

if __name__ == "__main__":
    apply_warning_filters()
    
    # 测试导入agentscope
    try:
        import agentscope
        print("AgentScope imported without warnings")
    except ImportError:
        print("AgentScope not available")