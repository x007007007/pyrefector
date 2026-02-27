#!/usr/bin/env python3
"""
测试同时包含打印日志和 return None 的 except Exception 块
"""
def test_mixed_except():
    """测试同时包含打印日志和 return None 的 except Exception 块"""
    try:
        value = int(input("请输入一个数字: "))
        result = 100 / value
        return result
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    """主程序"""
    print("测试同时包含打印日志和 return None 的 except Exception 块")
    try:
        result = test_mixed_except()
        print(f"结果: {result}")
    except Exception as e:
        print(f"程序错误: {e}")

if __name__ == "__main__":
    main()
