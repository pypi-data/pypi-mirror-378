# TaShan SciSpark PyPI 发布指南

## 准备工作

### 1. 注册 PyPI 账号
- 访问 [PyPI官网](https://pypi.org/) 注册账号
- 访问 [TestPyPI](https://test.pypi.org/) 注册测试账号（推荐先在测试环境发布）

### 2. 安装发布工具
```bash
pip install twine build
```

### 3. 配置 API Token（推荐）
在 PyPI 账号设置中创建 API Token，然后配置：

创建 `~/.pypirc` 文件：
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## 发布流程

### 1. 更新版本号
在 `pyproject.toml` 中更新版本号：
```toml
version = "0.1.1"  # 根据需要调整
```

### 2. 构建包
```bash
# 清理之前的构建
rm -rf dist/ build/ *.egg-info/

# 构建新包
python -m build
```

### 3. 检查包内容
```bash
# 检查构建的包
twine check dist/*
```

### 4. 上传到 TestPyPI（推荐先测试）
```bash
twine upload --repository testpypi dist/*
```

### 5. 测试安装
```bash
# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ tashan-scispark
```

### 6. 上传到正式 PyPI
```bash
twine upload dist/*
```

## 版本管理建议

### 语义化版本控制
- `MAJOR.MINOR.PATCH` (例如: 1.2.3)
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的功能新增
- PATCH: 向后兼容的问题修正

### 预发布版本
- `1.0.0a1` (alpha)
- `1.0.0b1` (beta) 
- `1.0.0rc1` (release candidate)

## 自动化发布（可选）

### 使用 GitHub Actions
创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## 注意事项

1. **包名唯一性**: 确保包名在 PyPI 上未被占用
2. **版本不可覆盖**: 一旦发布某个版本，不能再次上传相同版本号
3. **依赖管理**: 确保依赖版本兼容性
4. **文档完整**: README、LICENSE 等文档要完整
5. **测试充分**: 发布前充分测试功能

## 常见问题

### 1. 包名冲突
如果包名已被占用，需要修改 `pyproject.toml` 中的 `name` 字段。

### 2. 上传失败
- 检查网络连接
- 确认 API Token 正确
- 检查包格式是否正确

### 3. 依赖问题
- 使用 `requirements-core.txt` 作为最小依赖
- 可选依赖放在 `requirements-full.txt`

## 发布后维护

1. **监控下载量**: 在 PyPI 页面查看统计信息
2. **处理问题**: 及时响应用户反馈和 Issue
3. **定期更新**: 修复 bug 和添加新功能
4. **文档维护**: 保持文档与代码同步

## 相关链接

- [PyPI官网](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Python打包指南](https://packaging.python.org/)
- [Twine文档](https://twine.readthedocs.io/)