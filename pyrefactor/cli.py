import argparse
import sys
from .imports_refactor import rewrite_directory
from .graph import build_import_graph_mermaid, build_call_graph_mermaid, build_function_flow_mermaid
from .functions import rewrite_directory_for_functions
from .defensive_try_except import rewrite_directory_for_defensive_try_except


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyrefactor", description="AST 重构与图生成工具")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    p_refactor = subparsers.add_parser("refc_import", help="提升安全的 import 到顶层")
    p_refactor.add_argument("path", help="要处理的目录或文件路径")
    p_refactor.add_argument("--include-relative", action="store_true", help="包含相对导入")
    p_refactor.add_argument("--allow-control-blocks", action="store_true", help="允许控制块导入提升")
    p_refactor.add_argument("--dry-run", action="store_true", help="仅输出 diff")
    p_refactor.add_argument("--output-diff", help="将统一 diff 输出到文件")
    p_refactor.add_argument("--absimport", action="store_true", help="先将相对导入改写为绝对导入再进行提升")
    p_refactor.add_argument("--modify-under", help="仅修改此子目录下的文件，分析范围仍为path")
    p_refactor.add_argument("--failfirst", action="store_true", help="将 try/except ImportError 中的导入提前并移除 ImportError 处理")
    p_refactor.add_argument("--package-path", action="append", help="额外的包根目录，可重复指定", dest="package_path")

    p_graph = subparsers.add_parser("graph", help="生成 Mermaid 图")
    p_graph.add_argument("type", choices=["imports", "calls"], help="图类型")
    p_graph.add_argument("path", help="目录路径")

    p_flow = subparsers.add_parser("flow", help="生成函数流程图（Mermaid）")
    p_flow.add_argument("file", help="文件路径")
    p_flow.add_argument("--function", required=True, help="函数名")
    
    p_split = subparsers.add_parser("split_func", help="将大函数切割为多个小函数（基于注释边界，非嵌套函数）")
    p_split.add_argument("path", help="要处理的目录或文件路径")
    p_split.add_argument("--dry-run", action="store_true", help="仅输出 diff")
    p_split.add_argument("--output-diff", help="将统一 diff 输出到文件")
    p_split.add_argument("--process-methods", action="store_true", help="同时处理类内部的方法")

    p_remove_try = subparsers.add_parser("remove_defensive_try", help="移除防御式 try-except 语句（捕获所有异常且 try 块过长的）")
    p_remove_try.add_argument("path", help="要处理的目录或文件路径")
    p_remove_try.add_argument("--max-length", type=int, default=30, help="try 块长度阈值（默认: 30）")
    p_remove_try.add_argument("--dry-run", action="store_true", help="仅输出 diff")
    p_remove_try.add_argument("--output-diff", help="将统一 diff 输出到文件")
    
    # 新增参数
    p_remove_try.add_argument("--no-print-log", action="store_false", dest="check_print_log", help="不检查只打印日志的 except 块")
    p_remove_try.add_argument("--no-rethrow", action="store_false", dest="check_rethrow", help="不检查重新抛出异常的 except 块")
    p_remove_try.add_argument("--no-return-none", action="store_false", dest="check_return_none", help="不检查返回 None 的 except 块")

    args = parser.parse_args()
    if args.cmd == "refc_import":
        if args.absimport:
            from .abs_imports import rewrite_abs_directory
            rewrite_abs_directory(args.modify_under or args.path, package_paths=args.package_path)
        changes = rewrite_directory(args.path, include_relative=args.include_relative, allow_control_blocks=args.allow_control_blocks, dry_run=args.dry_run, output_diff=args.output_diff, modify_under=args.modify_under, failfirst=args.failfirst, package_paths=args.package_path)
        if not changes:
            print("没有发现需要更新的导入")
            return
        if args.dry_run:
            if args.output_diff:
                print(f"已写出 diff 到 {args.output_diff}")
            else:
                print("已生成 diff")
        else:
            print(f"已更新 {len(changes)} 个文件")
    elif args.cmd == "graph":
        if args.type == "imports":
            out = build_import_graph_mermaid(args.path)
        else:
            out = build_call_graph_mermaid(args.path)
        sys.stdout.write(out + "\n")
    elif args.cmd == "flow":
        out = build_function_flow_mermaid(args.file, args.function)
        if not out:
            print("无法生成流程图")
            return
        sys.stdout.write(out + "\n")
    elif args.cmd == "split_func":
        changes = rewrite_directory_for_functions(args.path, dry_run=args.dry_run, output_diff=args.output_diff, process_methods=args.process_methods)
        if not changes:
            print("没有发现需要拆分的函数")
            return
        if args.dry_run:
            if args.output_diff:
                print(f"已写出 diff 到 {args.output_diff}")
            else:
                print("已生成 diff")
        else:
            print(f"已更新 {len(changes)} 个文件")
    elif args.cmd == "remove_defensive_try":
        # 准备输出 diff 文件
        if args.output_diff:
            with open(args.output_diff, 'w', encoding='utf-8') as f:
                pass  # 清空文件
        
        changes = rewrite_directory_for_defensive_try_except(
            args.path,
            max_try_length=args.max_length,
            dry_run=args.dry_run,
            output_diff=args.output_diff,
            check_print_log=args.check_print_log,
            check_rethrow=args.check_rethrow,
            check_return_none=args.check_return_none
        )
        
        if not changes:
            print("没有发现需要移除的防御式 try-except 语句")
            return
        
        if args.dry_run:
            if args.output_diff:
                print(f"已写出 diff 到 {args.output_diff}")
            else:
                print("已生成 diff")
        else:
            print(f"已更新 {len(changes)} 个文件")


if __name__ == "__main__":
    main()
