#!/usr/bin/env python3
"""示例函数拆分功能测试文件"""


def test_function_splitting():
    """测试函数拆分功能"""
    # 准备测试内容
    source_code = """
def calculate_statistics():
    # 初始化数据结构
    data = []
    
    # 读取输入文件
    with open('data.txt', 'r') as f:
        for line in f:
            try:
                value = float(line.strip())
                data.append(value)
            except ValueError:
                continue
                
    # 计算基本统计值
    if data:
        average = sum(data) / len(data)
        min_value = min(data)
        max_value = max(data)
        
    # 输出结果
    print(f"平均值: {average:.2f}")
    print(f"最小值: {min_value}")
    print(f"最大值: {max_value}")
"""

    from pyrefactor.functions import rewrite_file_for_functions
    
    rewritten = rewrite_file_for_functions(source_code)
    
    print("=== 原始代码 ===")
    print(source_code)
    print("\n=== 重写后的代码 ===")
    print(rewritten)


if __name__ == "__main__":
    test_function_splitting()