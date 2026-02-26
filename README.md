# Python 代码重构工具

这是一个用于 Python 代码重构的工具，主要包含函数拆分和导入重构功能。

## 功能概述

### 1. 函数拆分（Function Splitting）

该工具可以帮助您将大型函数自动拆分为更小、更易于维护的函数，同时保持代码的功能完整性。主要功能包括：

- 自动分析函数结构
- 识别潜在的重构机会
- 基于变量作用域分析进行参数传递
- 处理 self 参数的类方法
- 保留代码注释和文档字符串

### 2. 导入重构（Import Refactoring）

该工具还提供了强大的导入重构功能，支持：

- 相对导入到绝对导入的转换
- 导入路径的优化
- 依赖图分析
- 循环依赖检测

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/python-refactor-tool.git
cd python-refactor-tool

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 函数拆分

```python
from pyrefactor.functions import rewrite_file_for_functions

# 读取源文件
with open("your_file.py", "r") as f:
    source_code = f.read()

# 执行函数拆分
refactored_code = rewrite_file_for_functions(source_code)

# 保存重构后的代码
with open("your_file_refactored.py", "w") as f:
    f.write(refactored_code)
```

### 导入重构

```python
from pyrefactor.imports_refactor import refactor_imports

# 重构单个文件
refactor_imports("path/to/your/file.py")

# 或重构整个目录
refactor_imports("path/to/your/directory")
```

## 命令行接口

该工具还提供了命令行接口：

```bash
# 函数拆分
python -m pyrefactor.cli functions --help

# 导入重构
python -m pyrefactor.cli imports --help
```

## 测试

该项目包含全面的测试覆盖：

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_functions.py -v

# 运行函数传参分析测试
pytest tests/test_function_parameter_analysis.py -v
```

## 项目结构

```
python-refactor-tool/
├── examples/               # 示例代码
│   ├── function_splitter/  # 函数拆分示例
│   └── imports/            # 导入重构示例
├── pyrefactor/             # 核心重构模块
│   ├── __init__.py
│   ├── abs_imports.py      # 绝对导入处理
│   ├── cli.py             # 命令行接口
│   ├── deps.py            # 依赖关系分析
│   ├── functions.py       # 函数拆分实现
│   ├── graph.py           # 依赖图构建
│   └── imports_refactor.py # 导入重构实现
├── tests/                 # 单元测试
│   ├── test_functions.py
│   ├── test_import_refactor.py
│   ├── test_function_parameter_analysis.py
│   └── ...
└── README.md
```

## 开发

### 环境要求

- Python 3.7+
- libcst（用于抽象语法树解析）
- pytest（用于测试）

### 贡献

欢迎提交问题和拉取请求。在提交代码之前，请确保所有测试都通过。

## 许可证

该项目使用 **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)** 许可证。

### 许可证说明

根据 CC BY-NC-SA 4.0 许可证，您可以：
- **非商业使用**：自由使用、复制和分发本软件
- **修改**：自由修改本软件
- **共享**：自由分发修改后的版本

但您必须：
- **署名**：保留原作者的署名信息
- **非商业**：不得用于商业目的
- **相同方式共享**：任何修改后的版本必须使用相同的许可证

### 商业化限制

- 本软件仅供非商业使用
- 任何商业化使用必须获得原作者的书面授权
- 所有衍生作品的商业化同样需要获得原作者授权

详细的许可证条款请参阅 LICENSE 文件。
