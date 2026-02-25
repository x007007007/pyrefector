import libcst as cst

# 查看 CSTNode 类型
print("=== libcst 版本 ===")
print(cst._version)

# 查看可以用于函数调用的类型
print("\n=== dir(cst) 中的相关类型 ===")
for attr in dir(cst):
    if 'Arg' in attr or 'Call' in attr or 'Param' in attr:
        print(attr)

# 查看函数调用的结构
print("\n=== 函数调用结构 ===")
src = "func()"
node = cst.parse_expression(src)
print(type(node))
print(dir(node))
if hasattr(node, 'args'):
    print(f"参数类型: {type(node.args)}")
    print(f"参数内容: {node.args}")