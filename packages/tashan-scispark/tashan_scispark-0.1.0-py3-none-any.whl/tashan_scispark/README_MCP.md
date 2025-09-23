# TaShan SciSpark MCP Server

TaShan SciSpark学术论文研究助手的MCP（Model Context Protocol）服务器实现。

## 功能特性

### 🔍 核心功能
- **论文搜索**: 基于关键词搜索学术论文
- **关键词提取**: 从文本中提取技术关键词和实体
- **研究想法生成**: 基于论文分析生成研究想法（异步任务）
- **研究评审**: 对研究想法进行评审和优化建议
- **论文压缩**: 压缩论文内容，提取核心信息

### 🛠 MCP工具列表
1. `search_papers` - 搜索学术论文
2. `extract_keywords` - 提取技术关键词
3. `generate_research_idea` - 生成研究想法（异步）
4. `get_task_status` - 获取任务状态
5. `review_research_idea` - 评审研究想法
6. `compress_paper_content` - 压缩论文内容
7. `get_server_info` - 获取服务器信息

## 快速开始

### 1. 安装依赖

```bash
# 安装MCP服务器依赖
python start_mcp_server.py --mode install

# 或手动安装
pip install -r requirements_mcp.txt
```

### 2. 启动Celery Worker（异步任务支持）

**重要：** 在启动MCP服务器之前，必须先启动Celery Worker以支持异步任务：

```bash
# 启动Celery Worker
python start_celery_worker.py
```

**异步功能说明：**
- `generate_research_idea` - 研究想法生成是异步任务，需要Celery Worker支持
- `get_task_status` - 用于查询异步任务的执行状态
- 如果未启动Celery Worker，异步MCP工具将无法正常工作

### 3. 启动MCP服务器

#### STDIO传输（推荐用于Claude Desktop）
```bash
python start_mcp_server.py --mode stdio
```

#### HTTP传输（用于网络部署）
```bash
python start_mcp_server.py --mode http --host 127.0.0.1 --port 8000
```

### 4. 测试服务器
```bash
python start_mcp_server.py --mode test
```

### 5. 生成Claude Desktop配置
```bash
python start_mcp_server.py --mode config
```

## Claude Desktop集成

### 自动配置
运行以下命令自动生成Claude Desktop配置：
```bash
python start_mcp_server.py --mode config
```

### 手动配置
编辑Claude Desktop配置文件：
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下配置：
```json
{
  "mcpServers": {
    "tashan_scispark": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/TaShan-SciSpark-main",
      "env": {
        "PYTHONPATH": "/path/to/TaShan-SciSpark-main",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

## 使用示例

### 1. 搜索论文
```python
# 在Claude中使用
search_papers(keyword="machine learning", limit=5)
```

### 2. 提取关键词
```python
# 从文本中提取技术关键词
extract_keywords(
    text="This paper presents a novel deep learning approach...",
    split_section="Paper Abstract"
)
```

### 3. 生成研究想法
```python
# 异步生成研究想法
task_result = generate_research_idea(
    keyword="natural language processing",
    paper_count=3
)

# 查询任务状态
get_task_status(task_id=task_result["task_id"])
```

### 4. 评审研究想法
```python
review_research_idea(
    topic="AI in Healthcare",
    draft="This research proposes..."
)
```

## 工具详细说明

### search_papers
搜索学术论文并返回相关信息。

**参数:**
- `keyword` (str): 搜索关键词
- `limit` (int): 返回论文数量限制，默认5

**返回:**
```json
{
  "success": true,
  "keyword": "machine learning",
  "related_keywords": ["deep learning", "neural networks"],
  "papers": [
    {
      "title": "论文标题",
      "abstract": "论文摘要",
      "authors": ["作者1", "作者2"],
      "published": "2024-01-01",
      "url": "https://arxiv.org/abs/...",
      "topic": "machine learning"
    }
  ],
  "count": 5
}
```

### extract_keywords
从文本中提取技术关键词和实体。

**参数:**
- `text` (str): 要分析的文本内容
- `split_section` (str): 文本分割部分，默认"Paper Abstract"

**返回:**
```json
{
  "success": true,
  "keywords": [
    {
      "entity": "deep learning",
      "relevance": 0.95,
      "count": 5
    }
  ],
  "count": 10
}
```

### generate_research_idea
异步生成研究想法，基于关键词和相关论文。

**参数:**
- `keyword` (str): 研究关键词
- `paper_count` (int): 参考论文数量，默认3

**返回:**
```json
{
  "success": true,
  "task_id": "task_1_1234567890",
  "message": "研究想法生成任务已启动"
}
```

### get_task_status
获取异步任务的状态和结果。

**参数:**
- `task_id` (str): 任务ID

**返回:**
```json
{
  "success": true,
  "task": {
    "id": "task_1_1234567890",
    "type": "generate_research_idea",
    "status": "completed",
    "result": "生成的研究想法内容...",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:05:00"
  }
}
```

## 配置说明

### 环境变量
- `PYTHONPATH`: 项目根目录路径
- `PYTHONIOENCODING`: 设置为"utf-8"以支持中文
- `OUTPUT_PATH`: 输出文件路径（在app/core/config.py中配置）

### 日志配置
服务器日志保存在`mcp_server.log`文件中，同时输出到stderr。

## 故障排除

### 常见问题

1. **ImportError: No module named 'fastmcp'**
   ```bash
   pip install fastmcp
   ```

2. **编码错误**
   确保设置了正确的环境变量：
   ```bash
   set PYTHONIOENCODING=utf-8
   ```

3. **Claude Desktop无法连接**
   - 检查配置文件路径是否正确
   - 确保Python路径正确
   - 重启Claude Desktop

4. **任务执行失败**
   - 检查日志文件`mcp_server.log`
   - 确保所有依赖已正确安装
   - 检查API密钥配置

### 调试模式
启用详细日志：
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 开发说明

### 项目结构
```
TaShan-SciSpark-main/
├── mcp_server.py           # MCP服务器主文件
├── start_mcp_server.py     # 启动脚本
├── requirements_mcp.txt    # MCP依赖
├── mcp_config.json        # MCP配置
├── README_MCP.md          # 本文档
├── app/                   # 原有应用代码
├── main.py               # 原有主程序
└── ...
```

### 添加新工具
在`mcp_server.py`中添加新的工具函数：

```python
@mcp.tool
def new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    新工具的描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述，默认10
    
    Returns:
        返回值描述
    """
    try:
        # 工具逻辑
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## 许可证

本项目遵循原TaShan SciSpark项目的许可证。

## 支持

如有问题或建议，请查看：
1. 日志文件`mcp_server.log`
2. 运行测试：`python start_mcp_server.py --mode test`
3. 检查依赖：`python start_mcp_server.py --check-deps`