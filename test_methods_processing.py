#!/usr/bin/env python3
"""测试处理类内部方法的功能"""

from pyrefactor.functions import rewrite_file_for_functions


def test_process_methods():
    """测试处理类内部方法的功能"""
    source_code = """class MyClass:
    def process_data(self):
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


def top_level_function():
    # 初始化变量
    x = 0
    y = 0
    
    # 计算总和
    total = x + y
    
    # 返回结果
    return total
"""

    # 测试默认行为（不处理方法）
    print("=== 默认行为（不处理方法） ===")
    result1 = rewrite_file_for_functions(source_code, process_methods=False)
    print(result1)
    
    # 测试处理方法
    print("\n=== 处理类内部方法 ===")
    result2 = rewrite_file_for_functions(source_code, process_methods=True)
    print(result2)
    
    # 验证处理结果
    assert "def process_data_1" in result2, "应该生成子函数 process_data_1"
    assert "def top_level_function_1" in result2, "应该生成子函数 top_level_function_1"
    print("\n✅ 测试成功！方法处理功能正常工作")


if __name__ == "__main__":
    test_process_methods()