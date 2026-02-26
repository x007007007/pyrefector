#!/bin/bash
# 测试防御式 try-except 移除功能的脚本

# 显示脚本说明
echo "=== 测试防御式 try-except 移除功能 ==="
echo "此脚本将演示如何使用 pyrefactor 工具移除代码中的防御式 try-except 语句"
echo ""

# 检查命令是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 Python 3.x"
    exit 1
fi

# 显示原始示例
echo "1. 原始示例文件: example_with_defensive_try.py"
echo "   包含一个包含防御式 try-except 语句的函数 process_data()"
echo ""

# 显示转换命令
echo "2. 执行转换命令:"
echo "   python -m pyrefactor remove_defensive_try \\"
echo "          example_with_defensive_try.py \\"
echo "          --max-length 20 \\"
echo "          --dry-run"
echo ""

# 执行实际转换
echo "3. 执行转换 (dry run 模式):"
python3 -m pyrefactor remove_defensive_try example_with_defensive_try.py --max-length 20 --dry-run
echo ""

# 显示转换后的文件
echo "4. 转换后的文件: example_without_defensive_try.py"
echo "   已移除防御式 try-except 语句"
echo ""

# 比较两个文件
echo "5. 原始文件与转换后文件的差异:"
diff -u example_with_defensive_try.py example_without_defensive_try.py
echo ""

# 说明
echo "=== 说明 ==="
echo "在原始代码中，process_data() 函数使用了："
echo "- 无类型的 except 子句（except:）"
echo "- 包含 22 行语句的长 try 块"
echo ""
echo "当 --max-length 设置为 20 时，该 try-except 语句被识别为防御式并被移除"
echo "而 calculate_statistics() 函数中的 except Exception 模式（长度为 6）未被修改"
