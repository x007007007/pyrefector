#!/usr/bin/env python3
import pytest
import tempfile
import os
from pyrefactor.defensive_try_except import (
    is_defensive_try_except,
    rewrite_file_for_defensive_try_except
)
import libcst as cst


def test_is_defensive_try_except_basic():
    """测试基本的防御式 try-except 检测"""
    
    # 测试1：简单的 except:
    code1 = '''try:
    print("test")
except:
    pass
'''
    
    module = cst.parse_module(code1)
    for node in module.body:
        if isinstance(node, cst.Try):
            result = is_defensive_try_except(node, max_try_length=1)
            assert result == False, "Try block is too short"
            result = is_defensive_try_except(node, max_try_length=0)
            assert result == True, "Should detect defensive try-except"


def test_is_defensive_try_except_except_exception():
    """测试 except Exception: 的检测"""
    
    code2 = '''try:
    print("test")
    a = 1
    b = 2
except Exception:
    pass
'''
    
    module = cst.parse_module(code2)
    for node in module.body:
        if isinstance(node, cst.Try):
            result = is_defensive_try_except(node, max_try_length=2)
            assert result == True, "Should detect except Exception"


def test_is_defensive_try_except_specific_except():
    """测试捕获特定异常的 try-except 不应被检测"""
    
    code3 = '''try:
    print("test")
    a = 1 / 0
except ZeroDivisionError:
    pass
'''
    
    module = cst.parse_module(code3)
    for node in module.body:
        if isinstance(node, cst.Try):
            result = is_defensive_try_except(node, max_try_length=1)
            assert result == False, "Should not detect specific exception"


def test_rewrite_file_for_defensive_try_except():
    """测试文件重写功能"""
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp:
        temp.write('''#!/usr/bin/env python3
def func():
    try:
        print("Start")
        x = 1
        y = 2
        z = x + y
        a = [1, 2, 3]
        b = a[10]
        c = "test"
        d = c.upper()
        e = True
        f = False
        g = e and f
        print("End")
    except:
        print("Error")
''')
        temp_file_path = temp.name
    
    try:
        # 执行重写
        result = rewrite_file_for_defensive_try_except(temp_file_path, max_try_length=5, dry_run=True)
        
        assert result is not None, "File should be modified"
        
        # 检查是否移除了 try-except
        assert "try:" not in result
        assert "except:" not in result
        
        # 检查内容是否保持原样（除了 try-except 部分）
        assert "print(\"Start\")" in result
        assert "x = 1" in result
        assert "y = 2" in result
        assert "z = x + y" in result
        assert "a = [1, 2, 3]" in result
        assert "b = a[10]" in result
        assert "c = \"test\"" in result
        assert "d = c.upper()" in result
        assert "e = True" in result
        assert "f = False" in result
        assert "g = e and f" in result
        assert "print(\"End\")" in result
        
        print("✅ File rewrite test passed")
        
    finally:
        os.unlink(temp_file_path)


def test_rewrite_file_no_changes():
    """测试没有防御式 try-except 的文件不应被修改"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp:
        temp.write('''#!/usr/bin/env python3
def func():
    print("test")
''')
        temp_file_path = temp.name
    
    try:
        result = rewrite_file_for_defensive_try_except(temp_file_path, max_try_length=5, dry_run=True)
        assert result is None, "File should not be modified"
        print("✅ No changes test passed")
        
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
