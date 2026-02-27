#!/usr/bin/env python3
"""
测试不同参数配置下的行为
"""
from pyrefactor.defensive_try_except import rewrite_file_for_defensive_try_except
import os

def test_check_return_none():
    """测试 --no-return-none 参数的行为"""
    original_file = "example_with_defensive_try.py"
    test_file1 = "test_with_return_none.py"
    test_file2 = "test_without_return_none.py"
    
    # 复制原文件用于测试
    import shutil
    shutil.copy(original_file, test_file1)
    shutil.copy(original_file, test_file2)
    
    print("=== 测试1: 默认参数（包含 return None 检查） ===")
    result1 = rewrite_file_for_defensive_try_except(
        test_file1,
        max_try_length=20,
        dry_run=False
    )
    
    if result1:
        print("  发现需要修改的内容")
        
        # 检查 read_file_data 函数是否被修改
        if "def read_file_data" in result1:
            print("  read_file_data 函数仍然存在")
            if "except Exception:" in result1:
                print("  except Exception 块仍然存在")
                if "return None" in result1:
                    print("  ❌ return None 没有被移除")
                else:
                    print("  ✓ return None 已被移除")
            else:
                print("  except Exception 块已被移除")
        else:
            print("  ❌ read_file_data 函数不存在")
    else:
        print("  没有发现需要修改的内容")
    
    print("\n=== 测试2: --no-return-none 参数（不包含 return None 检查） ===")
    result2 = rewrite_file_for_defensive_try_except(
        test_file2,
        max_try_length=20,
        dry_run=False,
        check_return_none=False
    )
    
    if result2:
        print("  发现需要修改的内容")
        
        # 检查 read_file_data 函数是否被修改
        if "def read_file_data" in result2:
            print("  read_file_data 函数仍然存在")
            if "except Exception:" in result2:
                print("  except Exception 块仍然存在")
                if "return None" in result2:
                    print("  ✓ return None 没有被移除（符合预期）")
                else:
                    print("  ❌ return None 已被移除（不符合预期）")
            else:
                print("  ❌ except Exception 块已被移除（不符合预期）")
        else:
            print("  ❌ read_file_data 函数不存在")
    else:
        print("  没有发现需要修改的内容")
    
    # 清理临时文件
    os.remove(test_file1)
    os.remove(test_file2)
    if os.path.exists(f"{test_file1}.modified"):
        os.remove(f"{test_file1}.modified")
    if os.path.exists(f"{test_file2}.modified"):
        os.remove(f"{test_file2}.modified")


def test_check_print_log():
    """测试 --no-print-log 参数的行为"""
    test_file = "test_no_print_log.py"
    
    import shutil
    shutil.copy("example_with_defensive_try.py", test_file)
    
    print("\n=== 测试3: --no-print-log 参数（不包含 print 检查） ===")
    result = rewrite_file_for_defensive_try_except(
        test_file,
        max_try_length=20,
        dry_run=False,
        check_print_log=False,
        check_rethrow=False,
        check_return_none=False
    )
    
    if result:
        print("  发现需要修改的内容")
    else:
        print("  没有发现需要修改的内容（符合预期，因为所有检查都被禁用）")
    
    os.remove(test_file)


if __name__ == "__main__":
    test_check_return_none()
    test_check_print_log()
    print("\n=== 所有测试完成 ===")
