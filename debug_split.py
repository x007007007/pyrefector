#!/usr/bin/env python3
"""
调试函数拆分功能的脚本
"""

from pyrefactor.functions import rewrite_file_for_functions, FunctionSplitter
import libcst as cst

# 测试代码
source_code = """
def process_data():
    # 初始化变量
    data = []
    count = 0
    
    # 读取数据文件
    with open('data.txt', 'r') as f:
        for line in f:
            if line.strip():
                data.append(line.strip())
    
    # 处理数据
    for item in data:
        count += 1
        print(f"处理项目: {item}")
    
    # 输出结果
    print(f"总项目数: {count}")
"""

print("原始代码:")
print("=" * 50)
print(source_code)
print()

# 测试解析过程
print("解析过程:")
print("=" * 50)
try:
    module = cst.parse_module(source_code)
    print("解析成功")
except Exception as e:
    print(f"解析失败: {e}")

# 查看解析后的结构
print()
print("模块结构:")
print("=" * 50)
if 'module' in locals():
    print(f"模块节点类型: {type(module)}")
    print(f"模块体长度: {len(module.body)}")
    for i, node in enumerate(module.body):
        print(f"\n第 {i+1} 个节点: {type(node)}")
        if hasattr(node, 'body'):
            print(f"  体节点数: {len(node.body.body)}" if hasattr(node.body, 'body') else f"  体节点: {type(node.body)}")
            
            if hasattr(node.body, 'body'):
                for j, stmt in enumerate(node.body.body):
                    print(f"    第 {j+1} 个语句: {type(stmt)}")
                    print(f"      行号: {stmt.lineno}")
                    print(f"      内容: {str(stmt)[:100]}")
                    
                    # 尝试提取注释
                    from pyrefactor.functions import extract_comment_context
                    context = extract_comment_context(stmt, source_code.splitlines())
                    print(f"      注释上下文: {repr(context)}")
else:
    print("没有解析到模块")

# 测试重写
print()
print("重写结果:")
print("=" * 50)
rewritten = rewrite_file_for_functions(source_code)
print(rewritten)

# 测试子函数创建
print()
print("子函数创建:")
print("=" * 50)
from pyrefactor.functions import create_subfunction_name
test_descs = ["初始化变量", "读取数据文件", "处理数据", "输出结果"]
for desc in test_descs:
    name = create_subfunction_name(desc)
    print(f"描述 '{desc}' -> 函数名 '{name}'")