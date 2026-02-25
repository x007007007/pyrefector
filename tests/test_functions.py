import os
import tempfile
import unittest
from pyrefactor.functions import rewrite_file_for_functions, rewrite_directory_for_functions


class TestFunctionSplitting(unittest.TestCase):
    """测试函数拆分功能的单元测试"""
    
    def test_simple_function_with_comments(self):
        """测试一个包含注释的简单函数拆分"""
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

        rewritten = rewrite_file_for_functions(source_code)

        # 检查是否生成了子函数
        self.assertIn("def process_data_1", rewritten)
        self.assertIn("def process_data_2", rewritten)
        self.assertIn("def process_data_3", rewritten)
        self.assertIn("def process_data_4", rewritten)
        
        # 检查主函数是否调用了子函数
        self.assertIn("process_data_1()", rewritten)
        self.assertIn("process_data_2()", rewritten)
        self.assertIn("process_data_3()", rewritten)
        self.assertIn("process_data_4()", rewritten)
        
        # 检查子函数是否有文档字符串
        self.assertIn('"""初始化变量"""', rewritten)
        self.assertIn('"""读取数据文件"""', rewritten)
        self.assertIn('"""处理数据"""', rewritten)
        self.assertIn('"""输出结果"""', rewritten)
    
    def test_function_without_comments(self):
        """测试一个没有注释的函数（不应该被拆分）"""
        source_code = """
def simple_function():
    x = 10
    y = 20
    return x + y
"""
        
        rewritten = rewrite_file_for_functions(source_code)
        self.assertEqual(source_code.strip(), rewritten.strip())
    
    def test_nested_function(self):
        """测试嵌套函数（不应该被拆分）"""
        source_code = """
def outer_function():
    def inner_function():
        # 内部函数的注释
        return 42
    
    return inner_function()
"""
        
        rewritten = rewrite_file_for_functions(source_code)
        self.assertEqual(source_code.strip(), rewritten.strip())
    
    def test_function_with_empty_comments(self):
        """测试包含空注释的函数"""
        source_code = """
def function_with_empty_comments():
    # 
    x = 10
    
    # 
    y = 20
    
    return x + y
"""
        
        rewritten = rewrite_file_for_functions(source_code)
        self.assertEqual(source_code.strip(), rewritten.strip())
    
    def test_function_with_mixed_comments(self):
        """测试包含有效和无效注释的函数"""
        source_code = """
def mixed_comments():
    # 有效的注释
    x = 10
    
    # 
    y = 20
    
    # 另一个有效注释
    z = 30
    
    return x + y + z
"""
        
        rewritten = rewrite_file_for_functions(source_code)
        
        # 检查是否只生成了有有效注释的子函数
        self.assertIn("def mixed_comments_1", rewritten)
        self.assertIn("def mixed_comments_2", rewritten)
        # 检查子函数是否有文档字符串
        self.assertIn('"""有效的注释"""', rewritten)
        self.assertIn('"""另一个有效注释"""', rewritten)
    
    def test_rewrite_file_function(self):
        """测试文件重写功能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_module.py")
            with open(test_file, "w") as f:
                f.write("""
def main_function():
    # 初始化
    print("初始化")
    
    # 处理
    print("处理")
    
    # 完成
    print("完成")
""")
            
            result = rewrite_directory_for_functions(tmpdir)
            self.assertEqual(len(result), 1)
            self.assertEqual(os.path.abspath(result[0]), os.path.abspath(test_file))
    
    def test_rewrite_file_unchanged(self):
        """测试处理没有需要拆分的函数的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_module.py")
            with open(test_file, "w") as f:
                f.write("""
def simple_function():
    x = 1
    y = 2
    return x + y
""")
            
            result = rewrite_directory_for_functions(tmpdir)
            self.assertEqual(len(result), 0)
    
    def test_directory_processing(self):
        """测试处理整个目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建两个测试文件
            file1 = os.path.join(tmpdir, "file1.py")
            with open(file1, "w") as f:
                f.write("""
def function1():
    # 处理数据
    data = [1, 2, 3]
    return sum(data)
""")
            
            file2 = os.path.join(tmpdir, "file2.py")
            with open(file2, "w") as f:
                f.write("""
def function2():
    # 计算结果
    return 42
""")
            
            result = rewrite_directory_for_functions(tmpdir)
            self.assertEqual(len(result), 2)
    
    def test_dry_run(self):
        """测试 dry_run 选项"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test_module.py")
            with open(test_file, "w") as f:
                f.write("""
def main_function():
    # 初始化
    print("初始化")
""")
            
            # 使用 dry_run=True 应该不会修改文件
            result = rewrite_directory_for_functions(tmpdir, dry_run=True)
            self.assertEqual(len(result), 1)
            
            with open(test_file, "r") as f:
                content = f.read()
            
            # 文件内容应该没有变化
            self.assertIn("def main_function", content)
            self.assertNotIn("def 初始化", content)


if __name__ == "__main__":
    unittest.main()