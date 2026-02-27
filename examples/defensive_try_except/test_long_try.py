#!/usr/bin/env python3
"""
包含长 try 块的测试文件
"""

import json
import requests


def process_large_data():
    """处理大型数据的函数，包含长 try 块"""
    try:
        # 这是一个很长的 try 块
        with open("large_data.json", "r") as f:
            data = json.load(f)
            
        # 处理数据的复杂逻辑
        results = []
        for item in data:
            # 各种数据处理步骤
            if "value" in item:
                results.append(item["value"] * 2)
            elif "price" in item:
                results.append(item["price"] * 1.1)
            else:
                results.append(0)
                
        # 进一步处理
        filtered_results = [x for x in results if x > 0]
        sorted_results = sorted(filtered_results, reverse=True)
        
        # 计算统计信息
        average = sum(sorted_results) / len(sorted_results) if sorted_results else 0
        maximum = max(sorted_results) if sorted_results else 0
        
        # 发送通知
        requests.post("https://api.example.com/notify", json={
            "count": len(sorted_results),
            "average": average,
            "maximum": maximum
        })
        
        return sorted_results
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return []


def main():
    """主函数"""
    try:
        results = process_large_data()
        print(f"处理了 {len(results)} 条记录")
        return True
    except Exception as e:
        print(f"程序执行失败: {e}")
        return False


if __name__ == "__main__":
    main()

