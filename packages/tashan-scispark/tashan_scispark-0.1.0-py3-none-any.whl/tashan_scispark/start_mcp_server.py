#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TaShan SciSpark MCP Server 启动脚本

基于MCP协议的假设生成框架服务器启动脚本
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastmcp
        print("✓ FastMCP已安装")
    except ImportError:
        print("✗ FastMCP未安装，请运行: pip install fastmcp")
        return False
    
    # 检查其他关键依赖
    required_modules = ['fastapi', 'uvicorn', 'pydantic', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module}未安装")
    
    if missing_modules:
        print(f"\n请安装缺失的依赖: pip install {' '.join(missing_modules)}")
        return False
    
    return True

def install_dependencies():
    """安装MCP服务器依赖"""
    print("正在安装MCP服务器依赖...")
    
    requirements_file = "requirements_mcp.txt"
    if not os.path.exists(requirements_file):
        print(f"错误: {requirements_file} 文件不存在")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True)
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def start_stdio_server():
    """启动STDIO传输的MCP服务器"""
    print("启动TaShan SciSpark MCP服务器 (STDIO传输)...")
    
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        # 直接运行mcp_server.py
        subprocess.run([sys.executable, "mcp_server.py"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"服务器启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n服务器已停止")
        return True

def start_http_server(host="127.0.0.1", port=8000):
    """启动HTTP传输的MCP服务器"""
    print(f"启动TaShan SciSpark MCP服务器 (HTTP传输) - {host}:{port}")
    
    # 修改mcp_server.py以使用HTTP传输
    server_code = f"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="{host}", port={port})
"""
    
    # 创建临时HTTP服务器文件
    with open("mcp_server_http.py", "w", encoding="utf-8") as f:
        f.write(server_code)
    
    try:
        subprocess.run([sys.executable, "mcp_server_http.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"HTTP服务器启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\nHTTP服务器已停止")
        return True
    finally:
        # 清理临时文件
        if os.path.exists("mcp_server_http.py"):
            os.remove("mcp_server_http.py")

def test_server():
    """测试MCP服务器功能"""
    print("测试MCP服务器功能...")
    
    test_code = """
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import Client
from mcp_server import mcp

async def test_mcp_server():
    print("开始测试MCP服务器...")
    
    # 使用内存传输进行测试
    client = Client(mcp)
    
    async with client:
        # 测试获取服务器信息
        print("测试: 获取服务器信息")
        result = await client.call_tool("get_server_info", {})
        print(f"结果: {result}")
        
        # 测试搜索论文
        print("\\n测试: 搜索论文")
        result = await client.call_tool("search_papers", {
            "keyword": "machine learning",
            "limit": 2
        })
        print(f"结果: 找到 {result.get('count', 0)} 篇论文")
        
        # 测试提取关键词
        print("\\n测试: 提取关键词")
        test_text = "This paper presents a novel approach to deep learning using transformer architectures for natural language processing tasks."
        result = await client.call_tool("extract_keywords", {
            "text": test_text
        })
        print(f"结果: 提取到 {result.get('count', 0)} 个关键词")
        
    print("\\n✓ 所有测试完成")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
"""
    
    # 创建测试文件
    with open("test_mcp_server.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    try:
        subprocess.run([sys.executable, "test_mcp_server.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists("test_mcp_server.py"):
            os.remove("test_mcp_server.py")

def generate_claude_config():
    """生成Claude Desktop配置"""
    config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    
    # 确保目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 当前工作目录
    current_dir = os.path.abspath(".")
    
    config = {
        "mcpServers": {
            "tashan_scispark": {
                "command": "python",
                "args": ["mcp_server.py"],
                "cwd": current_dir,
                "env": {
                    "PYTHONPATH": current_dir,
                    "PYTHONIOENCODING": "utf-8"
                }
            }
        }
    }
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Claude Desktop配置已生成: {config_path}")
        print("\n请重启Claude Desktop以加载新的MCP服务器配置")
        return True
        
    except Exception as e:
        print(f"✗ 生成Claude Desktop配置失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="TaShan SciSpark MCP服务器启动脚本")
    parser.add_argument("--mode", choices=["stdio", "http", "test", "install", "config"], 
                       default="stdio", help="运行模式")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="HTTP服务器端口")
    parser.add_argument("--check-deps", action="store_true", help="检查依赖")
    
    args = parser.parse_args()
    
    print("TaShan SciSpark MCP服务器启动脚本")
    print("=" * 40)
    
    if args.check_deps or args.mode == "install":
        if not check_dependencies():
            if args.mode == "install":
                install_dependencies()
            else:
                print("\n请先安装依赖: python start_mcp_server.py --mode install")
                return
    
    if args.mode == "stdio":
        start_stdio_server()
    elif args.mode == "http":
        start_http_server(args.host, args.port)
    elif args.mode == "test":
        test_server()
    elif args.mode == "config":
        generate_claude_config()
    elif args.mode == "install":
        install_dependencies()

if __name__ == "__main__":
    main()