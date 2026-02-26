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
echo "   包含两个函数："
echo "   - process_data(): 包含防御式 try-except（except:）"
echo "   - calculate_statistics(): 包含捕获具体异常的 try-except（ValueError, ZeroDivisionError）"
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
echo "   已移除 process_data() 函数中的防御式 try-except，但保留了 calculate_statistics() 中的具体异常捕获"
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
echo ""
echo "而 calculate_statistics() 函数中的 try-except 语句保留不变，因为："
echo "- 它捕获的是具体的异常类型（ValueError 和 ZeroDivisionError）"
echo "- 它的 try 块长度只有 3 行，远低于阈值"
echo ""
echo "这表明该工具能够正确地区分防御式 try-except 和合理的异常处理"
