#!/usr/bin/env python3
"""测试函数传参分析功能"""

import libcst as cst
import ast
from pyrefactor.functions import VariableScopeAnalyzer


def test_function_with_parameters():
    """测试带有参数的函数分析"""
    source_code = """def calculate_statistics(data_list):
    # 计算数据的基本统计值
    if not data_list:
        return 0, 0, 0, 0
    
    total = sum(data_list)
    average = total / len(data_list)
    min_value = min(data_list)
    max_value = max(data_list)
    
    return average, min_value, max_value, total
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("=== 带参数函数的变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['data_list', 'total', 'average', 'min_value', 'max_value']
    expected_used = ['data_list', 'total', 'average', 'min_value', 'max_value']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 带参数函数的变量作用域分析测试成功！")


def test_nested_functions():
    """测试嵌套函数的变量作用域分析"""
    source_code = """def outer_function(x, y):
    # 外部函数
    def inner_function(z):
        # 内部函数
        result = x + y + z
        return result
    
    product = x * y
    sum_result = inner_function(product)
    
    return sum_result
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 嵌套函数的变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    # 我们的分析器在处理嵌套函数时，会将所有变量都视为定义的，但只会记录实际使用的变量
    expected_defined = ['x', 'y', 'product', 'sum_result', 'z', 'result']
    expected_used = ['result', 'sum_result']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 嵌套函数的变量作用域分析测试成功！")


def test_functions_with_return_values():
    """测试有返回值的函数分析"""
    source_code = """def process_data(input_file):
    # 读取并处理数据文件
    with open(input_file, 'r') as f:
        data = []
        for line in f:
            try:
                value = float(line.strip())
                data.append(value)
            except ValueError:
                continue
                
    if not data:
        return []
        
    # 计算统计值
    average = sum(data) / len(data)
    min_value = min(data)
    max_value = max(data)
    
    return {
        'data': data,
        'average': average,
        'min_value': min_value,
        'max_value': max_value
    }
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 有返回值函数的变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['input_file', 'data', 'line', 'average', 'min_value', 'max_value']
    expected_used = ['input_file', 'data', 'average', 'min_value', 'max_value']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 有返回值函数的变量作用域分析测试成功！")


def test_function_with_complex_parameters():
    """测试带有复杂参数的函数分析"""
    source_code = """def analyze_data(data_dict, threshold=0.5, include_outliers=True):
    # 分析数据字典
    filtered_data = []
    for key, value in data_dict.items():
        if include_outliers or value <= threshold:
            filtered_data.append(value)
    
    if not filtered_data:
        return None
    
    # 计算统计值
    average = sum(filtered_data) / len(filtered_data)
    variance = sum((x - average) ** 2 for x in filtered_data) / len(filtered_data)
    
    return {
        'count': len(filtered_data),
        'average': average,
        'variance': variance
    }
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 带复杂参数函数的变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['data_dict', 'threshold', 'include_outliers', 
                       'filtered_data', 'average', 'variance']
    expected_used = ['average', 'variance', 'filtered_data']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 带复杂参数函数的变量作用域分析测试成功！")


def test_function_parameter_usage():
    """测试函数参数的使用分析"""
    source_code = """def update_user_profile(user, updates):
    # 更新用户资料
    if not updates:
        return user
    
    updated_user = user.copy()
    
    for key, value in updates.items():
        if key in updated_user:
            updated_user[key] = value
    
    return updated_user
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 函数参数使用分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['user', 'updates', 'updated_user']
    expected_used = ['user', 'updates', 'updated_user']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 函数参数使用分析测试成功！")


def test_function_with_loop_variables():
    """测试包含循环变量的函数分析"""
    source_code = """def fibonacci_sequence(n):
    # 计算斐波那契数列
    sequence = []
    a, b = 0, 1
    
    for i in range(n):
        sequence.append(a)
        a, b = b, a + b
    
    return sequence
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 包含循环变量的函数分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['n', 'sequence', 'i']
    expected_used = ['sequence']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 包含循环变量的函数分析测试成功！")


def test_function_with_error_handling():
    """测试包含错误处理的函数分析"""
    source_code = """def safe_divide(numerator, denominator):
    # 安全除法函数，包含错误处理
    try:
        result = numerator / denominator
        return result
    except ZeroDivisionError:
        print("错误: 分母不能为零")
        return None
    except TypeError:
        print("错误: 除数和被除数必须是数字类型")
        return None
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 包含错误处理的函数分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['numerator', 'denominator', 'result']
    expected_used = ['result']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 包含错误处理的函数分析测试成功！")


def test_function_parameter_analysis_integration():
    """测试与函数拆分功能的集成分析"""
    source_code = """def process_data(file_path, min_threshold=0.0):
    # 处理数据文件
    try:
        # 读取文件
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # 解析数据
        data_list = []
        for line in lines:
            line = line.strip()
            if line and line[0] != '#':
                try:
                    value = float(line)
                    if value >= min_threshold:
                        data_list.append(value)
                except ValueError:
                    continue
        
        # 计算统计值
        if data_list:
            average = sum(data_list) / len(data_list)
            min_value = min(data_list)
            max_value = max(data_list)
            count = len(data_list)
            
            return {
                'count': count,
                'average': average,
                'min_value': min_value,
                'max_value': max_value,
                'data': data_list
            }
        
        return None
        
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return None
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        return None
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 与函数拆分功能集成的变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['file_path', 'min_threshold', 'lines', 'data_list', 
                       'line', 'average', 'min_value', 'max_value', 'count']
    expected_used = ['file_path', 'count', 'average', 'min_value', 'data_list', 'max_value']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 与函数拆分功能集成的变量作用域分析测试成功！")


if __name__ == "__main__":
    test_function_with_parameters()
    test_nested_functions()
    test_functions_with_return_values()
    test_function_with_complex_parameters()
    test_function_parameter_usage()
    test_function_with_loop_variables()
    test_function_with_error_handling()
    test_function_parameter_analysis_integration()
    
    print("\n=============================================")
    print("✅ 所有函数传参分析功能测试成功！")
    print("=============================================")
