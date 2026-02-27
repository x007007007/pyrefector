#!/usr/bin/env python3
"""
检查 LibCST 节点的 lineno 属性的脚本
"""
import os
import sys
import libcst as cst
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

def check_lineno():
    test_code = '''#!/usr/bin/env python3
"""测试文件"""

def test1():
    try:
        print("执行操作")
        result = 1 / 0
        return result
    except Exception as e:
        print(f"错误: {e}")
        return None

def test2():
    try:
        with open("nonexistent.txt", "r") as f:
            content = f.read()
        return content
    except Exception:
        print("文件未找到")
        raise
'''
    
    module = cst.parse_module(test_code)
    
    print("解析后的模块:")
    print(f"Module: {module}")
    print()
    
    print("Try 节点信息:")
    for i, node in enumerate(module.body):
        if isinstance(node, cst.FunctionDef):
            print(f"\n函数 {node.name.value}:")
            for j, stmt in enumerate(node.body.body):
                if isinstance(stmt, cst.Try):
                    print(f"  Try语句: {stmt}")
                    print(f"  类型: {type(stmt)}")
                    
                    # 使用 LibCST 的位置信息获取行号
                    position = None
                    if hasattr(stmt, 'location'):
                        position = stmt.location
                    elif hasattr(stmt, 'range'):
                        position = stmt.range
                    
                    if position:
                        if hasattr(position, 'start'):
                            print(f"  行号: {position.start.line}")
                        elif hasattr(position, 'lineno'):
                            print(f"  行号: {position.lineno}")
                    else:
                        # 简单的估算方法
                        # 这里我们尝试通过统计到该节点为止的换行符数量来估算行号
                        code_str = str(module.code)
                        # 获取到该语句前的所有代码
                        import ast
                        import asttokens
                        
                        # 创建 AST 和 ASTTokens
                        tree = ast.parse(test_code)
                        atok = asttokens.ASTTokens(test_code, tree=tree)
                        
                        # 找到对应的函数
                        for func_node in ast.walk(tree):
                            if isinstance(func_node, ast.FunctionDef) and func_node.name == node.name.value:
                                # 在函数体中找到 try 语句
                                for stmt_node in func_node.body:
                                    if isinstance(stmt_node, ast.Try):
                                        print(f"  行号: {stmt_node.lineno}")
                    
                    print(f"  所有属性: {dir(stmt)}")
                    print()

if __name__ == "__main__":
    check_lineno()
