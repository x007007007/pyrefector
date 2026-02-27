#!/usr/bin/env python3
"""
包含各种防御式 try-except 模式的示例代码
"""

def process_data(data):
    """处理数据的函数，包含多种防御式 try-except"""
    # 这里有很多语句，超过了默认阈值（30行）
    print("开始处理数据")
    validated_data = validate_data(data)
    
    if not validated_data:
        raise ValueError("数据验证失败")
        
    processed_data = transform_data(data)
    
    if is_empty(processed_data):
        raise ValueError("处理后的数据为空")
        
    saved_data = save_to_database(processed_data)
    
    if not saved_data:
        raise IOError("保存数据失败")
        
    send_notification("数据处理成功")
    
    # 添加更多语句以确保超过默认长度
    temp_result = perform_calculations(data)
    analyze_result(temp_result)
    generate_report(temp_result)
    archive_results(temp_result)
    cleanup_temporary_files()
    update_logs("处理完成")
    check_system_health()
    refresh_cache()
    synchronize_data()
    validate_system_state()
    perform_backup()
    test_connections()
    reset_counters()
    
    return True


def calculate_statistics(data):
    """计算统计数据的函数，包含捕获具体异常的 try-except"""
    try:
        # 这是一个较短的 try 块，捕获具体的异常
        result = compute_average(data)
        if result < 0:
            raise ValueError("平均值不能为负数")
        return result
    except ValueError as e:
        print(f"计算统计数据时出错: {e}")
        return 0
    except ZeroDivisionError as e:
        print(f"计算统计数据时出错: {e}")
        return 0


def load_config():
    """加载配置的函数，包含打印日志的 except 块"""
    with open("config.json", "r") as f:
        config = json.load(f)
    return config


def call_external_api():
    """调用外部 API 的函数，包含重新抛出异常的 except 块"""
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()


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

def validate_data(data):
    """验证数据"""
    return True


def transform_data(data):
    """转换数据"""
    return data


def is_empty(data):
    """检查数据是否为空"""
    return False


def save_to_database(data):
    """保存到数据库"""
    return True


def send_notification(message):
    """发送通知"""
    print("发送通知:", message)


def perform_calculations(data):
    """执行计算"""
    return data


def analyze_result(result):
    """分析结果"""
    pass


def generate_report(result):
    """生成报告"""
    pass


def archive_results(result):
    """归档结果"""
    pass


def cleanup_temporary_files():
    """清理临时文件"""
    pass


def update_logs(message):
    """更新日志"""
    print("更新日志:", message)


def check_system_health():
    """检查系统健康"""
    pass


def refresh_cache():
    """刷新缓存"""
    pass


def synchronize_data():
    """同步数据"""
    pass


def validate_system_state():
    """验证系统状态"""
    pass


def perform_backup():
    """执行备份"""
    pass


def test_connections():
    """测试连接"""
    pass


def reset_counters():
    """重置计数器"""
    pass


def compute_average(data):
    """计算平均值"""
    if not data:
        raise ZeroDivisionError("数据为空")
    return sum(data) / len(data)
