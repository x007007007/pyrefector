#!/usr/bin/env python3
import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider
from pyrefactor.functions import extract_comment_context, create_subfunction_name, FunctionSplitter

# 读取示例文件内容
with open('/Users/xxc/workspace/github.com/x007007007/python_rewrite/example_functions.py', 'r') as f:
    content = f.read()

print("=== 文件内容 ===")
print(content)
print("\n" + "="*50 + "\n")

# 解析为 CST
wrapper = MetadataWrapper(cst.parse_module(content))
module = wrapper.module

lines = content.split('\n')

print("=== 解析结果 ===")
print(f"文件类型: {type(module)}")
print(f"模块内容行数: {len(lines)}")

# 获取元数据
metadata = wrapper.resolve(PositionProvider)

# 遍历模块内容以查看所有函数
functions = []
for node in module.body:
    if isinstance(node, cst.FunctionDef):
        print("\n=== 找到函数 ===")
        print(f"函数名: {node.name.value}")
        print(f"类型: {type(node)}")
        print(f"函数体语句数量: {len(node.body.body)}")
        
        # 打印每个语句的信息
        print("\n语句详情:")
        for i, stmt in enumerate(node.body.body):
            print(f"  {i}: {type(stmt)}")
            
            position = metadata.get(stmt, None)
            if position:
                print(f"     位置: {position.start.line} - {position.end.line}")
                
            context = extract_comment_context(stmt, lines, metadata)
            print(f"     提取的上下文: '{context}'")

        functions.append(node)

print("\n" + "="*50 + "\n")
print(f"总计找到 {len(functions)} 个顶级函数")