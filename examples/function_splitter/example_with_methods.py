#!/usr/bin/env python3
"""函数拆分示例 - 包含类和方法的处理"""

from pyrefactor.functions import rewrite_file_for_functions


def main():
    """主函数，展示函数拆分功能"""
    source_code = """class Calculator:
    def __init__(self, numbers):
        self.numbers = numbers
        self.results = {}
    
    def process_statistics(self):
        # 计算总和
        total = sum(self.numbers)
        
        # 计算平均值
        average = total / len(self.numbers)
        
        # 计算最小值
        min_value = min(self.numbers)
        
        # 计算最大值
        max_value = max(self.numbers)
        
        # 保存结果
        self.results['total'] = total
        self.results['average'] = average
        self.results['min'] = min_value
        self.results['max'] = max_value
        
        # 打印结果
        print("统计结果:")
        print(f"总和: {total}")
        print(f"平均值: {average:.2f}")
        print(f"最小值: {min_value}")
        print(f"最大值: {max_value}")


def analyze_data():
    # 准备数据
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # 创建计算器实例
    calc = Calculator(data)
    
    # 处理统计数据
    calc.process_statistics()
    
    # 返回结果
    return calc.results


# 运行示例
if __name__ == "__main__":
    results = analyze_data()
    print(f"最终结果: {results}")
"""

    print("=== 原始代码 ===")
    print(source_code)
    
    print("\n=== 处理后的代码 ===")
    try:
        processed_code = rewrite_file_for_functions(source_code, process_methods=True)
        print(processed_code)
        
        print("\n✅ 函数拆分成功！")
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    main()