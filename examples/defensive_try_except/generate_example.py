#!/usr/bin/env python3
"""
生成包含各种防御式 try-except 模式的示例文件的脚本
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from pyrefactor.defensive_try_except import rewrite_file_for_defensive_try_except

def create_example_file():
    """创建包含各种防御式 try-except 模式的示例文件"""
    example_code = '''#!/usr/bin/env python3
\"\"\"
包含各种防御式 try-except 模式的示例文件
用于测试参数化的防御式 try-except 移除
\"\"\"

import json
import requests

def load_config():
    \"\"\"加载配置的函数，包含打印日志的 except 块\"\"\"
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"无法加载配置: {e}")
        return {}


def call_external_api():
    \"\"\"调用外部 API 的函数，包含重新抛出异常的 except 块\"\"\"
    try:
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API 调用失败: {e}")
        raise


def read_file_data():
    \"\"\"读取文件数据的函数，包含返回 None 的 except 块\"\"\"
    try:
        with open("data.txt", "r") as f:
            data = f.read()
        return data.strip()
    except Exception:
        return None


def complex_function():
    \"\"\"包含多个异常处理的复杂函数，保留非 Exception 类型的异常捕获\"\"\"
    try:
        # 一些操作
        with open("important_file.txt", "r") as f:
            content = f.read()
        
        value = int(content)
        result = 100 / value
        
        return result
    except FileNotFoundError:
        print("文件未找到，使用默认值")
        return 10
    except ValueError as e:
        print(f"值错误: {e}，使用默认值")
        return 10
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None


def function_with_finally():
    \"\"\"包含 finally 块的函数，保留其他 try 结构\"\"\"
    try:
        file = open("temp_file.txt", "w")
        file.write("一些数据")
        return True
    except Exception as e:
        print(f"操作失败: {e}")
        return False
    finally:
        file.close()


def function_with_else():
    \"\"\"包含 else 块的函数，保留其他 try 结构\"\"\"
    try:
        value = int(input("请输入一个数字: "))
    except Exception as e:
        print(f"输入错误: {e}")
        return None
    else:
        print(f"你输入的是: {value}")
        return value


# 主程序示例
if __name__ == "__main__":
    print("测试各种防御式 try-except 模式")
    
    config = load_config()
    print(f"配置: {config}")
    
    try:
        api_data = call_external_api()
        print(f"API 数据: {api_data}")
    except Exception as e:
        print(f"API 调用失败: {e}")
    
    file_data = read_file_data()
    print(f"文件数据: {file_data}")
    
    result = complex_function()
    print(f"复杂函数结果: {result}")
    
    success = function_with_finally()
    print(f"带 finally 的函数成功: {success}")
    
    number = function_with_else()
    print(f"带 else 的函数结果: {number}")
'''

    with open("example_with_defensive_try.py", "w") as f:
        f.write(example_code)

def generate_transformed_file():
    """生成转换后的文件，演示参数化的效果"""
    result = rewrite_file_for_defensive_try_except(
        "example_with_defensive_try.py",
        max_try_length=20,
        dry_run=True,
        check_print_log=True,
        check_rethrow=True,
        check_return_none=False
    )
    
    if result:
        with open("example_without_return_none_defensive_try.py", "w") as f:
            f.write(result)
        print("转换后的文件已生成: example_without_return_none_defensive_try.py")
    else:
        print("没有需要修改的内容")

def main():
    """主函数"""
    create_example_file()
    print("示例文件已创建: example_with_defensive_try.py")
    generate_transformed_file()
    print("演示文件已生成")

if __name__ == "__main__":
    main()
