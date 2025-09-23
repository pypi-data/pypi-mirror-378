# TaShan SciSpark

TaShan SciSpark是一个基于MCP协议的假设生成框架。具备 "文献检索与内容处理 - 假设生成与初始草稿构建 - 多轮迭代优化（技术实体重排、MoA 协作、圆桌讨论）- 效果评估验证" 等核心功能。集成多个学术数据源，采用多阶段迭代 + 人机协作架构，实现从主题输入到完整研究想法生成的流程化处理。为研究人员提供从文献处理到创新想法生成的一站式解决方案。

## 核心功能

### 🔍 文献检索与内容处理
- 集成多个学术数据源（arXiv、Google Scholar等）
- 智能文献筛选和内容提取
- PDF文档解析和结构化处理

### 💡 假设生成与初始草稿构建
- 基于文献分析的研究假设生成
- 多维度创新点挖掘
- 初始研究想法草稿构建

### 🔄 多轮迭代优化
- **技术实体重排**：智能重组研究要素
- **MoA协作**：多智能体协同优化
- **圆桌讨论**：多角度评估和改进

### ✅ 效果评估验证
- 研究想法可行性评估
- 创新性和实用性验证
- 质量评分和改进建议

## 技术架构

- **MCP协议支持**：标准化的模型上下文协议集成
- **多阶段迭代**：渐进式优化研究想法质量
- **人机协作**：结合人工智能和专家知识
- **流程化处理**：从输入到输出的完整工作流

## Python文件和编码规约

  - `.py` 文件编码为 `utf-8`
  

## Git 贡献提交规范

  - `feat` 增加新功能
  - `fix` 修复问题/BUG
  - `style` 代码风格相关无影响运行结果的
  - `perf` 优化/性能提升
  - `refactor` 重构
  - `revert` 撤销修改
  - `test` 测试相关
  - `docs` 文档/注释
  - `chore` 依赖更新/脚手架配置修改等
  - `ci` 持续集成
  - `types` 类型定义文件更改
  - `wip` 开发中

## 启动服务

### 启动 Celery Worker

#### 方式一：使用优化启动脚本（推荐）

**Windows系统：**
```bash
# 直接运行批处理文件
start_celery_worker.bat

# 或使用Python脚本
python start_celery_worker.py
```

**Linux/Mac系统：**
```bash
python start_celery_worker.py
```

#### 方式二：传统启动方式
```bash
python -m celery -A app.task.paper_assistant worker --pool=solo -l info
```

**注意：** 推荐使用方式一，它包含了内存优化配置，能够有效防止内存爆炸问题。

### MCP工具异步任务支持

**重要提醒：** 当使用MCP工具中的异步功能（如研究想法生成）时，必须先启动Celery Worker：

```bash
# 启动Celery Worker以支持异步任务
python start_celery_worker.py
```

**异步MCP工具包括：**
- `generate_research_idea` - 生成研究想法（需要Celery Worker支持）
- `get_task_status` - 获取异步任务状态

如果未启动Celery Worker，异步MCP工具将无法正常工作。建议在使用MCP服务器前先启动Celery Worker。