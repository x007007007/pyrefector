#!/usr/bin/env python3
import libcst as cst

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

module = cst.parse_module(source_code)

# 找到函数
function = module.body[0]

print("函数名称:", function.name.value)
print("函数位置:", hasattr(function, 'position'))
if hasattr(function, 'position'):
    print("函数起始位置:", function.position.start.line)

print("\n函数体语句数量:", len(function.body.body))

for i, stmt in enumerate(function.body.body):
    print(f"\n=== 语句 {i}: {type(stmt)} ===")
    
    # 检查语句的属性
    attributes = dir(stmt)
    print("常用属性:", [attr for attr in attributes if attr.lower().find('lineno') != -1 or attr.lower().find('position') != -1])
    
    if hasattr(stmt, 'position'):
        print("position 属性:")
        print(f"  start: {stmt.position.start}")
        print(f"  end: {stmt.position.end}")
    
    if hasattr(stmt, 'body'):
        print(f"body 属性: {type(stmt.body)}")