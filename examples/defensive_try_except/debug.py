#!/usr/bin/env python3
"""
调试脚本，测试对 read_file_data 函数中 except Exception: return None 的识别
"""
import libcst as cst
from pyrefactor.defensive_try_except import is_defensive_except_body

def debug_read_file_data():
    """调试 read_file_data 函数"""
    code = """
def read_file_data():
    \"\"\"读取文件数据的函数，包含返回 None 的 except 块\"\"\"
    try:
        with open("data.txt", "r") as f:
            data = f.read()
        return data.strip()
    except Exception:
        return None
"""
    
    module = cst.parse_module(code)
    
    # 查找 try 语句
    for node in module.body:
        if isinstance(node, cst.FunctionDef) and node.name.value == "read_file_data":
            for stmt in node.body.body:
                if isinstance(stmt, cst.Try):
                    print("找到 try 语句")
                    
                    # 查找 except Exception: 块
                    for handler in stmt.handlers:
                        if isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
                            print(f"找到 except Exception 块")
                            print(f"body 类型: {type(handler.body)}")
                            print(f"body: {handler.body}")
                            
                            # 测试 is_defensive_except_body 函数
                            is_defensive = is_defensive_except_body(
                                handler.body, 
                                check_print_log=True, 
                                check_rethrow=True, 
                                check_return_none=True
                            )
                            print(f"is_defensive: {is_defensive}")


def debug_other_cases():
    """调试其他情况"""
    # 测试 except Exception as e: return None
    code1 = """
def func1():
    try:
        pass
    except Exception as e:
        return None
"""
    
    module1 = cst.parse_module(code1)
    for node in module1.body:
        if isinstance(node, cst.FunctionDef) and node.name.value == "func1":
            for stmt in node.body.body:
                if isinstance(stmt, cst.Try):
                    for handler in stmt.handlers:
                        if isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
                            print(f"=== except Exception as e: return None ===")
                            is_defensive = is_defensive_except_body(
                                handler.body, 
                                check_print_log=True, 
                                check_rethrow=True, 
                                check_return_none=True
                            )
                            print(f"is_defensive: {is_defensive}")
    
    # 测试 except Exception as e: print(e); return None
    code2 = """
def func2():
    try:
        pass
    except Exception as e:
        print(e)
        return None
"""
    
    module2 = cst.parse_module(code2)
    for node in module2.body:
        if isinstance(node, cst.FunctionDef) and node.name.value == "func2":
            for stmt in node.body.body:
                if isinstance(stmt, cst.Try):
                    for handler in stmt.handlers:
                        if isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
                            print(f"\n=== except Exception as e: print(e); return None ===")
                            is_defensive = is_defensive_except_body(
                                handler.body, 
                                check_print_log=True, 
                                check_rethrow=True, 
                                check_return_none=True
                            )
                            print(f"is_defensive: {is_defensive}")


if __name__ == "__main__":
    print("调试 read_file_data 函数")
    debug_read_file_data()
    print("\n\n调试其他情况")
    debug_other_cases()
