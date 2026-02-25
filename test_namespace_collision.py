#!/usr/bin/env python3
"""测试命名空间冲突修复"""


def test_namespace_collision():
    """测试当子函数名称与现有函数名冲突时的处理"""
    # 这个测试模拟了一个场景：
    # - 已经有一个名为 calculate_statistics_1 的函数
    # - 当我们拆分 calculate_statistics 函数时，第一个子函数会尝试使用 calculate_statistics_1 作为名称
    # - 修复后的实现应该能够检测到这个冲突并使用 calculate_statistics_1_1 或类似的名称
    
    source_code = """
def calculate_statistics_1():
    \"\"\"已存在的函数\"\"\"
    return 42

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
    
    # 检查是否存在命名空间冲突
    if "def calculate_statistics_1:" in rewritten:
        print("\n✅ 检测到命名空间冲突处理:")
        # 检查是否创建了新的子函数名称
        if "def calculate_statistics_1_1:" in rewritten:
            print("   冲突的名称 calculate_statistics_1 已正确处理为 calculate_statistics_1_1")
        elif "def calculate_statistics_2:" in rewritten:
            print("   冲突的名称 calculate_statistics_1 已正确跳过，使用 calculate_statistics_2")
        else:
            print("   需要进一步检查命名空间冲突处理")
            
    # 检查是否有重复的函数定义
    function_definitions = []
    for line in rewritten.splitlines():
        if line.strip().startswith("def "):
            func_name = line.strip().split()[1].split('(')[0]
            if func_name in function_definitions:
                print(f"\n❌ 发现重复函数定义: {func_name}")
            function_definitions.append(func_name)
    
    print(f"\n✅ 所有函数定义: {function_definitions}")


if __name__ == "__main__":
    test_namespace_collision()