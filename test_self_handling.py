#!/usr/bin/env python3
"""测试 self 参数处理功能"""

from pyrefactor.functions import rewrite_file_for_functions


def test_self_handling():
    """测试类方法中 self 参数的处理"""
    source_code = """class MyClass:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = []
    
    def process_data(self):
        # 初始化数据结构
        self.data = []
        
        # 读取输入文件
        with open(self.data_file, 'r') as f:
            for line in f:
                try:
                    value = float(line.strip())
                    self.data.append(value)
                except ValueError:
                    continue
                
        # 计算基本统计值
        if self.data:
            self.average = sum(self.data) / len(self.data)
            self.min_value = min(self.data)
            self.max_value = max(self.data)
        
        # 输出结果
        print(f"平均值: {self.average:.2f}")
        print(f"最小值: {self.min_value}")
        print(f"最大值: {self.max_value}")
"""

    # 测试处理包含 self 的方法
    print("=== 处理包含 self 参数的方法 ===")
    result = rewrite_file_for_functions(source_code, process_methods=True)
    print(result)
    
    # 验证结果
    assert "def process_data_1(self):" in result, "子函数应该有 self 参数"
    assert "def process_data_2(self):" in result, "子函数应该有 self 参数"
    assert "def process_data_3(self):" in result, "子函数应该有 self 参数"
    assert "def process_data_4(self):" in result, "子函数应该有 self 参数"
    assert "process_data_1(self)" in result, "调用子函数时应该传递 self"
    assert "self.data" in result, "应该保留 self 属性访问"
    
    print("\n✅ self 参数处理功能测试成功！")


if __name__ == "__main__":
    test_self_handling()