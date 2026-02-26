#!/usr/bin/env python3
"""测试变量作用域分析器"""

import libcst as cst
import ast


class VariableScopeAnalyzer:
    """使用 ast 分析变量作用域的简单实现，仅跟踪函数内部定义的变量"""
    
    def __init__(self):
        self.defined_variables = set()
        self.used_variables = set()
        self.is_in_function = False
    
    def visit_Assign(self, node):
        """处理赋值语句"""
        if self.is_in_function:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_variables.add(target.id)
    
    def visit_AnnAssign(self, node):
        """处理注释赋值"""
        if self.is_in_function and isinstance(node.target, ast.Name):
            self.defined_variables.add(node.target.id)
    
    def visit_For(self, node):
        """处理 for 循环"""
        if self.is_in_function and isinstance(node.target, ast.Name):
            self.defined_variables.add(node.target.id)
    
    def visit_Name(self, node):
        """处理变量引用"""
        if self.is_in_function and isinstance(node, ast.Name):
            self.used_variables.add(node.id)
    
    def visit_FunctionDef(self, node):
        """处理函数定义"""
        self.is_in_function = True
        
        for arg in node.args.args:
            self.defined_variables.add(arg.arg)
        
        for stmt in node.body:
            self.visit(stmt)
        
        self.is_in_function = False
    
    def visit(self, node):
        """通用访问方法"""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """默认访问方法"""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)
    
    def analyze(self, source_code):
        """分析源代码的变量作用域"""
        tree = ast.parse(source_code)
        
        # 遍历所有函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit_FunctionDef(node)
        
        # 过滤掉内置函数和标准库函数
        builtins = {'print', 'len', 'sum', 'min', 'max', 'open', 'float', 'ValueError'}
        filtered_used = [var for var in self.used_variables if var not in builtins]
        
        # 只返回实际使用的变量（即在函数内部使用的变量）
        actual_used = [var for var in filtered_used if var in self.defined_variables]
        
        return list(self.defined_variables), actual_used


def test_variable_scope_analysis():
    """测试变量作用域和依赖关系分析"""
    source_code = """def process_data():
    # 初始化数据结构
    data = []
    
    # 读取输入文件
    with open('data.txt', 'r') as f:
        for line in f:
            try:
                value = float(line.strip())
                data.append(value)
            except ValueError:
                continue
                
    # 计算基本统计值
    if data:
        average = sum(data) / len(data)
        min_value = min(data)
        max_value = max(data)
        
    # 输出结果
    print(f"平均值: {average:.2f}")
    print(f"最小值: {min_value}")
    print(f"最大值: {max_value}")
"""

    # 创建分析器
    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("=== 变量作用域分析结果 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    # 验证结果
    expected_defined = ['data', 'line', 'average', 'min_value', 'max_value']
    expected_used = ['data', 'average', 'min_value', 'max_value']
    
    assert set(expected_defined) == set(defined), "定义的变量不匹配"
    assert set(expected_used) == set(used), "使用的变量不匹配"
    
    print("\n✅ 变量作用域分析测试成功！")


def test_class_method_scope():
    """测试类方法的变量作用域"""
    source_code = """class MyClass:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = []
    
    def process_data(self):
        # 初始化数据结构
        self.data = []
        
        # 读取输入文件
        with open(self.data_file, 'r') as f:
            for line in f:
                try:
                    value = float(line.strip())
                    self.data.append(value)
                except ValueError:
                    continue
                
        # 计算基本统计值
        if self.data:
            self.average = sum(self.data) / len(self.data)
            self.min_value = min(self.data)
            self.max_value = max(self.data)
        
        # 输出结果
        print(f"平均值: {self.average:.2f}")
        print(f"最小值: {self.min_value}")
        print(f"最大值: {self.max_value}")
"""

    analyzer = VariableScopeAnalyzer()
    defined, used = analyzer.analyze(source_code)
    
    print("\n=== 类方法变量作用域分析 ===")
    print(f"定义的变量: {defined}")
    print(f"使用的变量: {used}")
    
    expected_defined = ['self', 'data_file', 'line']
    expected_used = ['self']
    
    assert set(expected_defined) == set(defined), "类方法定义的变量不匹配"
    assert set(expected_used) == set(used), "类方法使用的变量不匹配"
    
    print("\n✅ 类方法变量作用域分析测试成功！")


if __name__ == "__main__":
    test_variable_scope_analysis()
    test_class_method_scope()