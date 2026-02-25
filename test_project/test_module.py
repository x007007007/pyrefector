#!/usr/bin/env python3
"""测试项目文件"""


def process_data():
    初始化变量()
    读取数据文件()
    处理数据()
    输出结果()
def 初始化变量():
    # 初始化变量
    data = []
    count = 0
def 读取数据文件():
    
    # 读取数据文件
    with open('data.txt', 'r') as f:
        for line in f:
            if line.strip():
                data.append(line.strip())
def 处理数据():
    
    # 处理数据
    for item in data:
        count += 1
        print(f"处理项目: {item}")
def 输出结果():
    
    # 输出结果
    print(f"总项目数: {count}")


def calculate_statistics():
    输出结果_1()
    收集数据()
    计算平均值()
    计算最大值和最小值()
    输出统计结果()
def 初始化变量():
    # 初始化变量
    data = []
    count = 0
def 读取数据文件():
    
    # 读取数据文件
    with open('data.txt', 'r') as f:
        for line in f:
            if line.strip():
                data.append(line.strip())
def 处理数据():
    
    # 处理数据
    for item in data:
        count += 1
        print(f"处理项目: {item}")
def 输出结果():
    
    # 输出结果
    print(f"总项目数: {count}")
def 输出结果_1():
    
    # 输出结果
    print(f"总项目数: {count}")
def 收集数据():
    # 收集数据
    items = []
    with open('results.txt', 'r') as f:
        for line in f:
            try:
                value = float(line.strip())
                items.append(value)
            except ValueError:
                continue
def 计算平均值():
    
    # 计算平均值
    if items:
        average = sum(items) / len(items)
def 计算最大值和最小值():
    
    # 计算最大值和最小值
    if items:
        min_val = min(items)
        max_val = max(items)
def 输出统计结果():
    
    # 输出统计结果
    print(f"平均值: {average:.2f}")
    print(f"最小值: {min_val}")
    print(f"最大值: {max_val}")