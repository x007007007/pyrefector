#!/usr/bin/env python3
"""
包含多种防御式 try-except 模式的测试文件
"""

def load_config():
    """加载配置的函数，包含打印日志的 except 块"""
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"无法加载配置: {e}")
        return {}


def call_external_api():
    """调用外部 API 的函数，包含重新抛出异常的 except 块"""
    try:
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API 调用失败: {e}")
        raise


def read_file_data():
    """读取文件数据的函数，包含返回 None 的 except 块"""
    try:
        with open("data.txt", "r") as f:
            data = f.read()
        return data.strip()
    except Exception:
        return None


# 模拟辅助函数（实际项目中这些函数会有实际实现）
import json
import requests
