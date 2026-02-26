# Python代码重构工具

这是一个用于自动重构 Python 代码的工具，专注于以下核心功能：

## 功能概览

### 1. 函数拆分

自动分析和重构长函数为较小的、更易维护的函数单元。

### 2. 导入优化

分析和优化 Python 导入语句，以提高代码质量和可读性。

### 3. 防御式Try-Except移除（新增功能）

自动识别并移除防御式 try-except 语句，同时保留合理的异常处理。

## 安装

```bash
pip install -e .
```

## 使用方法

### 函数拆分

```bash
python -m pyrefactor split_func <文件或目录> [--options]
```

### 导入优化

```bash
python -m pyrefactor refc_import <文件或目录> [--options]
```

### 防御式Try-Except移除

```bash
python -m pyrefactor remove_defensive_try <文件或目录> [--options]
```

## 功能详解：防御式Try-Except移除

### 问题背景

防御式 try-except 语句（如 `except:` 或 `except Exception:`）通常用于捕获所有可能的异常，但这种做法往往会隐藏真正的问题，并导致难以调试的代码。

### 识别标准

该功能会识别以下模式的 try-except 语句：
1. 使用 `except:`（无类型异常捕获）
2. 使用 `except Exception:`（捕获所有异常）
3. try 块长度超过指定阈值（默认 30 行）

### 使用示例

```bash
# 处理单个文件，阈值设为20行
python -m pyrefactor remove_defensive_try example_with_defensive_try.py --max-length 20

# 处理整个目录，使用默认阈值30行
python -m pyrefactor remove_defensive_try src/

# 预览变更（dry run）
python -m pyrefactor remove_defensive_try src/ --dry-run
```

### 功能特点

1. **精确识别**：能够正确地区分防御式 try-except 和合理的异常处理
2. **阈值可调**：支持自定义 try 块长度阈值
3. **预览功能**：提供 dry run 模式，可预览变更而不修改文件
4. **目录处理**：支持递归处理整个目录
5. **报告输出**：提供详细的变更报告和差异输出

## 示例说明

在 `examples/defensive_try_except/` 目录中，包含一个完整的示例：

### 原始代码

```python
def process_data(data):
    """处理数据的函数，包含防御式 try-except"""
    try:
        # 这里有很多语句，超过了默认阈值（30行）
        print("开始处理数据")
        validated_data = validate_data(data)
        
        if not validated_data:
            raise ValueError("数据验证失败")
            
        processed_data = transform_data(data)
        
        if is_empty(processed_data):
            raise ValueError("处理后的数据为空")
            
        saved_data = save_to_database(processed_data)
        
        if not saved_data:
            raise IOError("保存数据失败")
            
        send_notification("数据处理成功")
        
        # 添加更多语句以确保超过默认长度
        temp_result = perform_calculations(data)
        analyze_result(temp_result)
        generate_report(temp_result)
        archive_results(temp_result)
        cleanup_temporary_files()
        update_logs("处理完成")
        check_system_health()
        refresh_cache()
        synchronize_data()
        validate_system_state()
        perform_backup()
        test_connections()
        reset_counters()
        
        return True
    except:
        print("发生异常，但继续执行")
        return False

def calculate_statistics(data):
    """计算统计数据的函数，包含捕获具体错误的 try-except"""
    try:
        # 这是一个较短的 try 块，捕获具体的异常
        result = compute_average(data)
        if result < 0:
            raise ValueError("平均值不能为负数")
        return result
    except ValueError as e:
        print(f"计算统计数据时出错: {e}")
        return 0
    except ZeroDivisionError as e:
        print(f"计算统计数据时出错: {e}")
        return 0
```

### 转换后的代码

```python
def process_data(data):
    """处理数据的函数，包含防御式 try-except"""
    # 这里有很多语句，超过了默认阈值（30行）
    print("开始处理数据")
    validated_data = validate_data(data)
    
    if not validated_data:
        raise ValueError("数据验证失败")
        
    processed_data = transform_data(data)
    
    if is_empty(processed_data):
        raise ValueError("处理后的数据为空")
        
    saved_data = save_to_database(processed_data)
    
    if not saved_data:
        raise IOError("保存数据失败")
        
    send_notification("数据处理成功")
    
    # 添加更多语句以确保超过默认长度
    temp_result = perform_calculations(data)
    analyze_result(temp_result)
    generate_report(temp_result)
    archive_results(temp_result)
    cleanup_temporary_files()
    update_logs("处理完成")
    check_system_health()
    refresh_cache()
    synchronize_data()
    validate_system_state()
    perform_backup()
    test_connections()
    reset_counters()
    
    return True

def calculate_statistics(data):
    """计算统计数据的函数，包含捕获具体错误的 try-except"""
    try:
        # 这是一个较短的 try 块，捕获具体的异常
        result = compute_average(data)
        if result < 0:
            raise ValueError("平均值不能为负数")
        return result
    except ValueError as e:
        print(f"计算统计数据时出错: {e}")
        return 0
    except ZeroDivisionError as e:
        print(f"计算统计数据时出错: {e}")
        return 0
```

### 说明

1. **移除了防御式 try-except**：`process_data()` 函数中的 `except:` 语句被移除
2. **保留了合理的异常处理**：`calculate_statistics()` 函数中的 `except ValueError` 和 `except ZeroDivisionError` 保留不变
3. **提高了代码质量**：移除了隐藏真正问题的防御式 try-except，同时保留了精确的错误处理

## 测试

运行所有测试：

```bash
pytest tests/
```

运行特定功能的测试：

```bash
# 函数拆分
pytest tests/test_functions.py -v

# 导入优化
pytest tests/test_import_refactor.py -v

# 防御式Try-Except移除
pytest tests/test_defensive_try_except.py -v
```

## 贡献

欢迎提交 PR 和问题。

## 许可证

MIT
