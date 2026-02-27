#!/usr/bin/env python3
"""
测试日志输出格式的脚本
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from pyrefactor.defensive_try_except import rewrite_file_for_defensive_try_except

def create_test_file():
    """创建测试文件"""
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

def test3():
    try:
        data = {}
        return data["key"]
    except Exception:
        pass

if __name__ == "__main__":
    print("测试函数")
    test1()
    try:
        test2()
    except:
        pass
    test3()
'''
    
    with open("temp_test_file.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    
    return "temp_test_file.py"

def run_test():
    """运行测试"""
    test_file = create_test_file()
    
    try:
        print("开始测试修改后的日志输出格式...\n")
        
        # 运行重写函数
        result = rewrite_file_for_defensive_try_except(
            test_file,
            max_try_length=5,
            dry_run=True,
            check_print_log=True,
            check_rethrow=True,
            check_return_none=True
        )
        
        if result is not None:
            print("\n文件内容已修改")
        else:
            print("\n文件未修改")
    
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    run_test()
