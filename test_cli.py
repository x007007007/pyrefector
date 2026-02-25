#!/usr/bin/env python3
import os
import sys
from pyrefactor.functions import rewrite_directory_for_functions
from pyrefactor.deps import list_python_files

def main():
    # 测试 list_python_files 函数
    path = '/Users/xxc/workspace/github.com/x007007007/python_rewrite'
    files = list_python_files(path)
    
    print("=== 目录中的 Python 文件 ===")
    for file_path in sorted(files):
        if 'example' in file_path:
            print(file_path)
    
    print("\n" + "="*50 + "\n")
    
    # 测试 rewrite_directory_for_functions
    changes = rewrite_directory_for_functions('/Users/xxc/workspace/github.com/x007007007/python_rewrite/example_functions.py', dry_run=True)
    
    print(f"处理的文件数量: {len(changes)}")
    for file_path in changes:
        print(f"  - {file_path}")
    
    print("\n" + "="*50 + "\n")
    
    print("命令执行完成")

if __name__ == "__main__":
    main()