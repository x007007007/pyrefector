#!/usr/bin/env python3
import os
from pyrefactor.functions import rewrite_file_for_functions

def main():
    file_path = '/Users/xxc/workspace/github.com/x007007007/python_rewrite/example_functions.py'
    
    # 读取原始内容
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    print("=== 原始内容 ===")
    print(source)
    print("\n" + "="*80 + "\n")
    
    # 重写文件
    rewritten = rewrite_file_for_functions(source)
    
    print("=== 重写后的内容 ===")
    print(rewritten)
    print("\n" + "="*80 + "\n")
    
    print(f"文件是否有变化: {rewritten != source}")
    
    if rewritten != source:
        print("变化的行数:")
        import difflib
        for line in difflib.ndiff(source.splitlines(), rewritten.splitlines()):
            if line.startswith('+') or line.startswith('-'):
                print(line)


if __name__ == "__main__":
    main()