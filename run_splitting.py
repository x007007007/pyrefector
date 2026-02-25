#!/usr/bin/env python3
import libcst as cst
from libcst.metadata import MetadataWrapper, PositionProvider
from pyrefactor.functions import extract_comment_context, create_subfunction_name, FunctionSplitter

def main():
    # 读取示例文件内容
    with open('/Users/xxc/workspace/github.com/x007007007/python_rewrite/example_functions.py', 'r') as f:
        content = f.read()

    # 解析为 CST
    wrapper = MetadataWrapper(cst.parse_module(content))
    module = wrapper.module
    metadata = wrapper.resolve(PositionProvider)
    lines = content.split('\n')

    # 应用转换
    transformer = FunctionSplitter(lines, metadata)
    new_module = module.visit(transformer)

    # 输出结果
    print("=== 原始文件 ===")
    print(content)
    print("\n" + "="*80 + "\n")
    print("=== 转换后的文件 ===")
    print(new_module.code)

    # 保存结果
    with open('/Users/xxc/workspace/github.com/x007007007/python_rewrite/example_functions_transformed.py', 'w') as f:
        f.write(new_module.code)

    print("\n" + "="*80 + "\n")
    print("=== 结果已保存到 example_functions_transformed.py ===")


if __name__ == "__main__":
    main()