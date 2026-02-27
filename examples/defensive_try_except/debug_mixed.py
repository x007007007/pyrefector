#!/usr/bin/env python3
"""
调试 test_mixed.py 文件中的防御式 try-except 识别问题
"""
import libcst as cst
from pyrefactor.defensive_try_except import is_defensive_try_except, is_defensive_except_body

def debug_test_mixed():
    """调试 test_mixed.py 文件"""
    with open("test_mixed.py", "r") as f:
        code = f.read()
    
    module = cst.parse_module(code)
    
    # 遍历所有函数
    for node in module.body:
        if isinstance(node, cst.FunctionDef):
            print(f"\n=== 函数: {node.name.value} ===")
            for stmt in node.body.body:
                if isinstance(stmt, cst.Try):
                    print("找到 try 语句")
                    
                    # 打印 try 长度
                    if hasattr(stmt.body, 'body'):
                        print(f"try 块长度: {len(stmt.body.body)}")
                    
                    # 检查是否是防御式的
                    is_defensive = is_defensive_try_except(
                        stmt, 
                        max_try_length=20,
                        check_print_log=True,
                        check_rethrow=True,
                        check_return_none=False
                    )
                    print(f"是防御式: {is_defensive}")


if __name__ == "__main__":
    debug_test_mixed()
