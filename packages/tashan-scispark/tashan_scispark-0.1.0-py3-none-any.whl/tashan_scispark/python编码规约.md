以下是一份详细的 Python 编码规范范例，遵循 PEP 8 并补充常见最佳实践：

---

### Python 编码规范范例

#### 1. 文件命名
- **模块/脚本文件**：全小写，可使用下划线分隔
  ```python
  # 正确
  account_service.py
  http_utils.py

  # 避免
  AccountService.py
  http-utils.py
  ```

- **测试文件**：以 `test_` 开头
  ```python
  test_account_service.py
  ```

#### 2. 导入规范
```python
# 标准库导入
import os
import sys
from typing import List, Dict

# 第三方库导入
import numpy as np
from flask import Flask

# 本地模块导入
from my_package.module import MyClass
```

#### 3. 类命名
- **PascalCase 风格**，首字母大写
```python
class UserAccount:
    """用户账户类"""

    def __init__(self, username: str):
        self.username = username
```

#### 4. 方法/函数命名
- **snake_case 风格**，全小写加下划线
```python
def calculate_total_price(items: List[Dict], discount: float = 0.0) -> float:
    """计算商品总价（含折扣）
    
    Args:
        items: 商品列表，每个商品是包含'price'的字典
        discount: 折扣率 (0.0-1.0)
    
    Returns:
        折后总价
    """
    total = sum(item['price'] for item in items)
    return total * (1 - discount)
```

#### 5. 变量命名
- **snake_case 风格**
```python
# 普通变量
user_count = 10
max_connections = 100

# 常量（全大写）
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

#### 6. 注释规范
```python
# 单行注释（# 后空一格）
# 这是单行注释

# 多行字符串作为函数/类文档
def process_data(data: bytes) -> str:
    """处理二进制数据并返回字符串
    
    Args:
        data: 输入的二进制数据
        
    Returns:
        处理后的字符串
        
    Raises:
        ValueError: 如果数据无效
    """
    if not data:
        raise ValueError("Empty data")
    return data.decode('utf-8')

# 行内注释（与代码保持2空格间隔）
result = some_function()  # 这是行内注释
```

#### 7. 类型提示（Python 3.6+）
```python
from typing import Optional, Union

def greet_user(name: str, age: Optional[int] = None) -> str:
    """带类型提示的函数"""
    if age:
        return f"Hello {name}, you are {age} years old"
    return f"Hello {name}"

# 复杂类型
Vector = List[Union[float, int]]

def scale_vector(vector: Vector, scalar: float) -> Vector:
    return [x * scalar for x in vector]
```

#### 8. 代码格式
```python
# 正确的缩进（4空格）
if user.is_active:
    message = "Welcome back!"
    print(message)

# 长表达式换行（括号内自然换行）
result = some_function_with_long_name(
    argument1,
    argument2,
    keyword_argument=value,
)

# 字典字面量换行
config = {
    'debug': True,
    'log_path': '/var/log/app.log',
    'max_connections': 100,
}
```

#### 9. 异常处理
```python
try:
    value = int(user_input)
except ValueError as err:
    logger.error("Invalid input: %s", err)
    raise  # 重新抛出或处理
else:
    # 只有try成功时执行
    process_value(value)
finally:
    # 无论是否异常都会执行
    cleanup_resources()
```

#### 10. 字符串处理
```python
# 使用f-string（Python 3.6+）
greeting = f"Hello, {user.name}!"

# 多行字符串
message = """\
This is a long message
that spans multiple lines
"""

# 需要转义时使用r前缀
path = r"C:\Users\Name\Documents"
```

#### 11. 单元测试示例
```python
import unittest

class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual('hello'.upper(), 'HELLO')

    def test_isupper(self):
        self.assertTrue('HELLO'.isupper())
        self.assertFalse('Hello'.isupper())
```

#### 12. 主程序入口
```python
def main():
    """主函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='input file')
    args = parser.parse_args()
    
    # 程序逻辑
    if args.input:
        process_file(args.input)

if __name__ == '__main__':
    main()
```

---

### 关键原则总结：
1. **一致性**：整个项目保持统一风格
2. **可读性**：代码是写给人看的
3. **明确性**：变量名/函数名要表达意图
4. **简洁性**：避免过度复杂的表达式
5. **文档化**：关键逻辑要有注释说明

建议使用工具自动检查：
- `flake8`：代码风格检查
- `mypy`：静态类型检查
- `black`：自动格式化
- `isort`：自动整理import

实际项目中可根据团队需求调整，但应保持团队内统一。