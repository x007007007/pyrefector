from pyrefactor.functions import rewrite_file_for_functions

source = """
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

print("=== 调试输出 ===")
result = rewrite_file_for_functions(source)
print("\n=== 重写结果 ===")
print(result)