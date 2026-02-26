#!/usr/bin/env python3
"""
示例文件：包含防御式 try-except 语句的代码
"""


def process_data(data):
    """处理数据的函数，包含防御式 try-except"""
    try:
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
    except:
        print("发生异常，但继续执行")
        return False


def validate_data(data):
    """验证数据"""
    print("验证数据")
    return True


def transform_data(data):
    """转换数据"""
    print("转换数据")
    return data


def is_empty(data):
    """检查数据是否为空"""
    print("检查数据是否为空")
    return False


def save_to_database(data):
    """保存到数据库"""
    print("保存到数据库")
    return True


def send_notification(message):
    """发送通知"""
    print("发送通知:", message)


def perform_calculations(data):
    """执行计算"""
    print("执行计算")
    return data


def analyze_result(result):
    """分析结果"""
    print("分析结果")
    return True


def generate_report(result):
    """生成报告"""
    print("生成报告")
    return True


def archive_results(result):
    """归档结果"""
    print("归档结果")
    return True


def cleanup_temporary_files():
    """清理临时文件"""
    print("清理临时文件")
    return True


def update_logs(message):
    """更新日志"""
    print("更新日志:", message)
    return True


def check_system_health():
    """检查系统健康"""
    print("检查系统健康")
    return True


def refresh_cache():
    """刷新缓存"""
    print("刷新缓存")
    return True


def synchronize_data():
    """同步数据"""
    print("同步数据")
    return True


def validate_system_state():
    """验证系统状态"""
    print("验证系统状态")
    return True


def perform_backup():
    """执行备份"""
    print("执行备份")
    return True


def test_connections():
    """测试连接"""
    print("测试连接")
    return True


def reset_counters():
    """重置计数器"""
    print("重置计数器")
    return True


def calculate_statistics(data):
    """计算统计信息，包含 except Exception 模式"""
    try:
        # 较短的 try 块，不会被识别为防御式
        print("计算统计信息")
        stats = {}
        stats['count'] = len(data)
        stats['sum'] = sum(data)
        stats['average'] = stats['sum'] / stats['count']
        return stats
    except Exception as e:
        print(f"计算统计信息失败: {e}")
        return {}


def main():
    """主函数"""
    data = [1, 2, 3, 4, 5]
    
    print("=== 示例1：包含防御式 try-except 的函数 ===")
    success = process_data(data)
    print(f"处理结果: {'成功' if success else '失败'}")
    
    print("\n=== 示例2：正常的 try-except 模式 ===")
    stats = calculate_statistics(data)
    print(f"统计信息: {stats}")
    
    print("\n=== 示例3：无 try-except 的函数 ===")
    validate_data(data)


if __name__ == "__main__":
    main()
