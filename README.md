# Python 代码重构工具

这是一个用于 Python 代码自动重构的工具，专注于以下几个核心功能：

## 1. 函数拆分
- 将过长的函数自动拆分为更小、更易维护的函数
- 保留代码功能和行为不变
- 支持处理带有 `self` 参数的方法

## 2. 导入优化
- 优化 Python 文件中的导入语句
- 处理未使用的导入
- 规范导入顺序

## 3. 防御式 Try-Except 移除
- 自动识别并移除常见的防御式编程模式中的 try-except 语句
- 支持对不同类型的防御式模式进行开关控制

### 3.1 识别的防御式 Try-Except 模式

#### a. 基本模式
- **过长的 try 块**：超过指定行数阈值的 try 块（默认 30 行）
- **无类型异常捕获**：使用 `except:` 或 `except Exception:` 的语句

#### b. 防御式处理模式
以下是常见的防御式异常处理模式，现在支持单独开关控制：

1. **仅打印日志**：`check_print_log=True`（默认）
   - 仅包含 `print()`、`logger()` 或类似日志记录语句的 except 块
   - 示例：
     ```python
     try:
         # 一些操作
     except Exception as e:
         print(f"Error: {e}")
         return None
     ```

2. **重新抛出异常**：`check_rethrow=True`（默认）
   - 在打印日志后重新抛出异常的 except 块
   - 示例：
     ```python
     try:
         # 一些操作
     except Exception as e:
         print(f"Error: {e}")
         raise
     ```

3. **返回 None**：`check_return_none=True`（默认）
   - 捕获异常后直接返回 None 的 except 块
   - 示例：
     ```python
     try:
         # 一些操作
     except Exception:
         return None
     ```

### 3.2 使用方法

#### 命令行接口
```bash
python -m pyrefactor remove_defensive_try <文件或目录路径>
```

#### 可选参数
- `--max-length <长度>`：设置 try 块长度阈值（默认 30 行）
- `--no-print-log`：不检查仅打印日志的防御式模式
- `--no-rethrow`：不检查重新抛出异常的防御式模式
- `--no-return-none`：不检查返回 None 的防御式模式
- `--dry-run`：仅显示修改预览，不实际修改文件
- `--output-diff <文件>`：将修改差异输出到指定文件

#### Python API
```python
from pyrefactor.defensive_try_except import rewrite_file_for_defensive_try_except, rewrite_directory_for_defensive_try_except

# 处理单个文件
result = rewrite_file_for_defensive_try_except(
    "path/to/your/file.py",
    max_try_length=30,
    check_print_log=True,
    check_rethrow=True,
    check_return_none=True,
    dry_run=False
)

# 处理整个目录
modified_files = rewrite_directory_for_defensive_try_except(
    "path/to/your/directory",
    max_try_length=30,
    check_print_log=True,
    check_rethrow=True,
    check_return_none=True,
    dry_run=False,
    output_diff="defensive_try_changes.diff"
)
```

### 3.3 使用示例

#### 示例场景 1：移除所有防御式模式
```bash
python -m pyrefactor remove_defensive_try examples/defensive_try_except/ --max-length 20 --dry-run
```

#### 示例场景 2：只移除仅打印日志的模式
```bash
python -m pyrefactor remove_defensive_try examples/defensive_try_except/ --max-length 20 --no-rethrow --no-return-none --dry-run
```

#### 示例场景 3：只移除重新抛出异常的模式
```bash
python -m pyrefactor remove_defensive_try examples/defensive_try_except/ --max-length 20 --no-print-log --no-return-none --dry-run
```

### 3.4 工作原理
1. 识别所有包含 `except:` 或 `except Exception:` 的 try-except 语句
2. 检查 try 块长度是否超过阈值
3. 分析 except 块的内容，判断是否是防御式处理模式
4. 根据配置的开关决定是否移除该 try-except 语句
5. 输出修改后的代码

### 3.5 注意事项
- 该功能会改变代码的错误处理行为，请在使用前确保对代码有充分的测试覆盖
- 使用 `--dry-run` 参数可以先查看修改预览，避免意外
- 某些情况下，防御式 try-except 可能是有意设计的，请谨慎使用

## 项目结构
```
python-refactor-tool/
├── examples/               # 示例代码
│   ├── function_splitter/  # 函数拆分示例
│   └── defensive_try_except/  # 防御式 try-except 示例
├── pyrefactor/             # 核心重构模块
│   ├── __init__.py
│   ├── functions.py        # 函数拆分实现
│   ├── defensive_try_except.py  # 防御式 try-except 实现
│   └── imports_refactor.py  # 导入优化实现
├── tests/                  # 单元测试
│   ├── test_functions.py
│   └── test_defensive_try_except.py
└── README.md               # 项目说明文档
```

## 安装和使用

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/python-refactor-tool.git
   cd python-refactor-tool
   ```

2. 创建并激活虚拟环境（可选但推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -e .
   ```

4. 运行示例：
   ```bash
   # 函数拆分示例
   python -m pyrefactor split_func examples/function_splitter/ --dry-run
   
   # 防御式 try-except 移除示例
   python -m pyrefactor remove_defensive_try examples/defensive_try_except/ --max-length 20 --dry-run
   ```

## 运行测试

```bash
python -m pytest tests/ -v
```

## 许可证
MIT License
