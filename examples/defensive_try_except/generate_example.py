#!/usr/bin/env python3
"""
生成示例转换文件的脚本
"""
from pyrefactor.defensive_try_except import rewrite_file_for_defensive_try_except
import shutil

def generate_example():
    """生成示例转换文件"""
    original_file = "example_with_defensive_try.py"
    transformed_file = "example_without_defensive_try.py"
    
    # 执行转换，设置更低的阈值
    result = rewrite_file_for_defensive_try_except(
        original_file,
        max_try_length=20,
        dry_run=True
    )
    
    if result:
        with open(transformed_file, "w") as f:
            f.write(result)
        print(f"转换后的文件已生成: {transformed_file}")
    else:
        print("没有需要修改的内容")
        shutil.copy2(original_file, transformed_file)

if __name__ == "__main__":
    generate_example()
