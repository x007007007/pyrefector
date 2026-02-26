# 架构设计文档

## 项目架构概述

Python 代码重构工具是一个基于 LibCST 的高级代码重构工具，旨在提供安全、高效的 Python 代码重构功能。项目采用模块化架构，将核心功能与命令行接口分离，便于维护和扩展。

## 核心架构组件

### 1. 命令行接口层 (CLI)
**文件**: `pyrefactor/cli.py`

负责处理用户输入和命令分发，提供以下命令：

- `split_func`: 函数拆分功能
- `refc_import`: 导入重构功能
- `remove_defensive_try`: 防御式 try-except 移除功能

### 2. 核心重构引擎层
**文件**: `pyrefactor/` 目录下的各个模块

#### a. 函数拆分模块 (`functions.py`)
- 使用抽象语法树 (AST) 分析函数结构
- 识别可拆分的代码块
- 处理变量作用域和参数传递
- 保留代码注释和文档字符串

#### b. 导入重构模块 (`imports_refactor.py`)
- 分析导入关系和依赖
- 优化导入语句
- 检测并修复导入问题

#### c. 防御式 try-except 移除模块 (`defensive_try_except.py`)
- 识别防御式 try-except 模式
- 使用 LibCST 进行代码修改
- 支持目录扫描和递归处理
- 提供预览和差异输出功能

### 3. 依赖管理层 (`deps.py`)
负责分析模块间的依赖关系，为重构提供基础支持。

### 4. 图生成层 (`graph.py`)
用于生成代码依赖图和流程图，帮助理解代码结构。

## 技术架构特点

### 1. 基于 LibCST 的代码分析
项目使用 LibCST (Concrete Syntax Tree) 库进行代码分析和修改，提供：
- 精确的代码定位
- 保留代码格式
- 安全的代码修改
- 详细的差异输出

### 2. 模块化设计
各个功能模块相互独立，具有清晰的接口和职责边界。

### 3. 分层架构
- **命令层**: 处理用户输入和命令分发
- **引擎层**: 核心重构逻辑
- **分析层**: 代码分析和检测
- **输出层**: 结果展示和报告

## 数据流

```
用户输入 (CLI)
    ↓
命令解析和验证 (cli.py)
    ↓
执行相应重构功能 (functions.py / imports_refactor.py / defensive_try_except.py)
    ↓
代码分析和修改 (LibCST)
    ↓
输出结果或保存修改
```

## 项目结构

```
python-refactor-tool/
├── examples/               # 示例代码
│   ├── function_splitter/  # 函数拆分示例
│   ├── imports/            # 导入重构示例
│   └── defensive_try_except/ # 防御式 try-except 移除示例
├── pyrefactor/             # 核心重构模块
│   ├── __init__.py
│   ├── abs_imports.py      # 绝对导入处理
│   ├── cli.py             # 命令行接口
│   ├── deps.py            # 依赖关系分析
│   ├── defensive_try_except.py # 防御式 try-except 移除实现
│   ├── functions.py       # 函数拆分实现
│   ├── graph.py           # 依赖图构建
│   └── imports_refactor.py # 导入重构实现
├── docs/                   # 文档
│   └── ARCHITECTURE.md    # 架构设计文档
├── tests/                 # 单元测试
│   ├── test_functions.py
│   ├── test_import_refactor.py
│   ├── test_defensive_try_except.py # 防御式 try-except 测试
│   └── ...
└── README.md              # 用户文档
```

## 开发架构

### 1. 测试架构
项目采用 pytest 框架进行测试，包含：
- 单元测试
- 集成测试
- 功能测试
- 代码覆盖率分析

### 2. 开发流程
- 遵循 Python 编码规范
- 使用类型注解
- 进行严格的代码审查
- 维护测试覆盖率

## 扩展架构

### 1. 功能扩展
项目设计支持新功能的快速扩展：
- 添加新命令：在 `cli.py` 中添加相应函数
- 实现重构逻辑：在 `pyrefactor/` 目录下添加新模块
- 添加测试：在 `tests/` 目录下添加测试文件

### 2. 集成点
- 与其他工具集成
- CI/CD 流程
- 代码质量检查

## 安全性考虑

- 所有代码修改均通过 LibCST 进行，确保安全性
- 提供 dry-run 模式，避免意外修改
- 详细的差异输出帮助验证修改正确性
- 恢复机制（git 集成）

## 性能考虑

- 增量分析：仅分析需要修改的部分
- 缓存机制：避免重复分析
- 并行处理：支持多核CPU
- 内存优化：高效处理大型代码库
