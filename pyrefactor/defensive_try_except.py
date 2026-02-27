import libcst as cst
from typing import List, Optional, Set, Tuple
import os
import difflib


def is_defensive_try_except(
    try_node: cst.Try, 
    max_try_length: int = 30,
    check_print_log: bool = True,
    check_rethrow: bool = True,
    check_return_none: bool = True,
    filename: str = "",
    line_number: int = 0
) -> bool:
    """判断是否是防御式 try-except 语句
    
    防御式 try-except 的特点：
    1. 包含至少一个 except 子句
    2. 捕获所有异常（except: 或 except Exception:）
    3. try 块过长（超过指定长度）
    4. except 块只做简单的处理：
       - 只打印日志（check_print_log=True）
       - 重新抛出异常（check_rethrow=True）
       - 只返回 None（check_return_none=True）
    """
    if filename and line_number:
        print(f"=== 文件: {filename}:{line_number} ===")
    
    # 检查是否有 except 子句
    if not try_node.handlers:
        return False
    
    # 检查 except 子句是否捕获所有异常
    has_catch_all = False
    for handler in try_node.handlers:
        # except: 没有类型参数
        if handler.type is None:
            has_catch_all = True
        # except Exception: 捕获所有异常
        elif isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
            has_catch_all = True
    
    # 检查 try 块长度
    if hasattr(try_node.body, 'body'):
        try_length = len(try_node.body.body)
    else:
        try_length = 0
    
    # 检查 except 块的内容
    has_defensive_handler = False
    defensive_reason = ""
    for handler in try_node.handlers:
        if has_catch_all:
            # 检查 except 块是否是防御式的
            if is_defensive_except_body(handler.body, check_print_log, check_rethrow, check_return_none):
                has_defensive_handler = True
                # 确定具体的防御式类型
                defensive_reason = get_defensive_reason(handler.body, check_print_log, check_rethrow, check_return_none)
                break
    
    # 判断是否是防御式 try-except
    if has_catch_all and (
        (has_defensive_handler) or  # 有防御式的处理
        (try_length > max_try_length)  # 或 try 块过长
    ):
        decision = "✓ 移除防御式的 try-except"
        if has_defensive_handler:
            reason = f"原因：{defensive_reason}"
        else:
            reason = f"原因：try 块过长 ({try_length} 行 > {max_try_length} 行)"
        
        if filename and line_number:
            print(f"{filename}:{line_number} - {decision}")
            print(f"  {reason}")
        else:
            print(f"{decision}")
            print(f"  {reason}")
        
        return True
    
    return False


def get_defensive_reason(body, check_print_log, check_rethrow, check_return_none):
    """获取防御式的具体原因"""
    # 确保我们处理的是可迭代的 body
    statements = []
    
    if hasattr(body, 'body'):
        statements = body.body
    elif isinstance(body, list):
        statements = body
    else:
        statements = [body]
    
    has_print = False
    has_raise = False
    has_return_none = False
    
    for stmt in statements:
        def check_stmt(s):
            nonlocal has_print, has_raise, has_return_none
            if has_print_statement(s):
                has_print = True
            elif has_raise_statement(s):
                has_raise = True
            elif is_return_none(s):
                has_return_none = True
        
        if isinstance(stmt, cst.SimpleStatementLine):
            for part in stmt.body:
                check_stmt(part)
        else:
            check_stmt(stmt)
    
    if has_print and not has_raise and not has_return_none:
        return "except 块仅打印日志"
    if has_raise and not has_print and not has_return_none:
        return "except 块仅重新抛出异常"
    if has_return_none and not has_print and not has_raise:
        return "except 块仅返回 None"
    if has_print and has_raise and not has_return_none:
        return "except 块打印日志后重新抛出异常"
    if has_print and not has_raise and has_return_none:
        return "except 块打印日志后返回 None"
    
    return "except 块包含防御式处理"


def is_defensive_except_body(
    body: cst.FlattenSentinel | cst.BaseSuite | cst.SimpleStatementLine,
    check_print_log: bool,
    check_rethrow: bool,
    check_return_none: bool
) -> bool:
    """判断 except 块是否是防御式的
    
    防御式 except 块的特点：
    - 只打印日志（check_print_log=True）
    - 重新抛出异常（check_rethrow=True）
    - 只返回 None（check_return_none=True）
    """
    # 确保我们处理的是可迭代的 body
    statements = []
    
    if hasattr(body, 'body'):
        statements = body.body
    elif isinstance(body, list):
        statements = body
    else:
        statements = [body]
    
    has_print = False
    has_raise = False
    has_return_none = False
    other_statements = 0
    
    for stmt in statements:
        def check_stmt(s):
            nonlocal has_print, has_raise, has_return_none, other_statements
            if has_print_statement(s):
                has_print = True
            elif has_raise_statement(s):
                has_raise = True
            elif is_return_none(s):
                has_return_none = True
            else:
                other_statements += 1
        
        if isinstance(stmt, cst.SimpleStatementLine):
            for part in stmt.body:
                check_stmt(part)
        else:
            check_stmt(stmt)
    
    # 判断是否是防御式异常处理
    if other_statements > 0:
        return False
    
    # 检查各种模式组合
    if check_print_log and check_return_none:
        if (has_print and not has_raise and has_return_none):
            return True
    elif check_print_log and not check_return_none:
        if (has_print and not has_raise and has_return_none):
            return False
    elif not check_print_log and check_return_none:
        if (has_print and not has_raise and has_return_none):
            return False
    else:
        return False
    
    if has_print and not has_raise and not has_return_none:
        return True
    if has_raise and not has_print and not has_return_none:
        return True
    if has_return_none and not has_print and not has_raise:
        return True
    if has_print and has_raise and not has_return_none:
        return True
    
    return False


def is_return_none(return_stmt: cst.CSTNode) -> bool:
    """检查返回语句是否返回 None"""
    if not isinstance(return_stmt, cst.Return):
        return False
    return return_stmt.value is None or (
        isinstance(return_stmt.value, cst.Name) and return_stmt.value.value == "None"
    )


def has_print_statement(stmt: cst.CSTNode) -> bool:
    """检查是否有 print 语句"""
    # 如果是 SimpleStatementLine，检查其 body 内容
    if isinstance(stmt, cst.SimpleStatementLine):
        for part in stmt.body:
            if isinstance(part, cst.Expr) and isinstance(part.value, cst.Call):
                func = part.value.func
                if isinstance(func, cst.Name) and func.value == "print":
                    return True
    # 如果是直接的 Expr/Call
    elif isinstance(stmt, cst.Expr) and isinstance(stmt.value, cst.Call):
        func = stmt.value.func
        if isinstance(func, cst.Name) and func.value == "print":
            return True
    return False


def has_raise_statement(stmt: cst.CSTNode) -> bool:
    """检查是否有 raise 语句"""
    # 如果是 SimpleStatementLine，检查其 body 内容
    if isinstance(stmt, cst.SimpleStatementLine):
        for part in stmt.body:
            if isinstance(part, cst.Raise):
                return True
    # 如果是直接的 Raise
    elif isinstance(stmt, cst.Raise):
        return True
    return False


class DefensiveTryExceptTransformer(cst.CSTTransformer):
    """用于移除防御式 try-except 的转换器"""
    
    def __init__(self, 
                 max_try_length: int = 30,
                 dry_run: bool = False,
                 check_print_log: bool = True,
                 check_rethrow: bool = True,
                 check_return_none: bool = True,
                 filename: str = ""):
        self.max_try_length = max_try_length
        self.dry_run = dry_run
        self.changes_made = False
        self.check_print_log = check_print_log
        self.check_rethrow = check_rethrow
        self.check_return_none = check_return_none
        self.filename = filename
    
    def visit_Everything(self, node: cst.CSTNode) -> Optional[bool]:
        """访问所有节点，专门寻找 Try 节点"""
        if isinstance(node, cst.Try):
            return True
        return True
    
    def leave_Try(self, original_node: cst.Try, updated_node: cst.Try) -> cst.CSTNode:
        """处理 Try 节点"""
        # 获取行号信息的最简单方法：
        # 我们使用自定义状态变量在访问过程中跟踪行号
        if not hasattr(self, '_line_counter'):
            self._line_counter = 0
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
                
            # 使用简单的模式匹配查找 try 语句的行号
            self._line_mapping = []
            for i, line in enumerate(source_lines):
                if 'try:' in line:
                    self._line_mapping.append(i + 1)
        
        line_number = 0
        if hasattr(self, '_line_mapping') and len(self._line_mapping) > self._line_counter:
            line_number = self._line_mapping[self._line_counter]
            self._line_counter += 1
        else:
            # 如果未找到匹配，使用简单估算方法
            node_str = str(original_node)
            line_number = node_str.count('\n') + 1
        
        # 找到所有防御式的 except Exception 处理程序
        defensive_handlers = []
        non_defensive_handlers = []
        
        for handler in original_node.handlers:
            # 检查是否是捕获所有异常的处理程序
            is_catch_all = False
            if handler.type is None:
                is_catch_all = True
            elif isinstance(handler.type, cst.Name) and handler.type.value == "Exception":
                is_catch_all = True
            
            if is_catch_all:
                # 检查是否是防御式处理
                if is_defensive_except_body(handler.body, self.check_print_log, self.check_rethrow, self.check_return_none):
                    defensive_handlers.append(handler)
                else:
                    non_defensive_handlers.append(handler)
            else:
                non_defensive_handlers.append(handler)
        
        # 判断是否有防御式处理
        has_defensive_handlers = len(defensive_handlers) > 0
        has_catch_all = len(defensive_handlers) > 0 or any(
            h.type is None or (isinstance(h.type, cst.Name) and h.type.value == "Exception") 
            for h in non_defensive_handlers
        )
        
        # 检查 try 块长度
        if hasattr(original_node.body, 'body'):
            try_length = len(original_node.body.body)
        else:
            try_length = 0
        
        # 判断是否是防御式 try-except
        if (has_defensive_handlers) or (has_catch_all and try_length > self.max_try_length):
            self.changes_made = True
            
            # 获取具体的防御式原因
            reason = ""
            if has_defensive_handlers:
                first_defensive_body = defensive_handlers[0].body
                reason = get_defensive_reason(first_defensive_body, self.check_print_log, self.check_rethrow, self.check_return_none)
            else:
                reason = f"try 块过长 ({try_length} 行 > {self.max_try_length} 行)"
            
            # 处理后的 try 语句必须至少有一个有效的 except 或 finally 块
            if non_defensive_handlers or original_node.finalbody:
                # 还有其他处理程序或 finally 块，只移除防御式的 handler
                decision = "✓ 移除防御式的 except Exception 处理"
                filename = os.path.basename(self.filename)
                print(f"{filename}:{line_number} - {decision}")
                print(f"  原因：{reason}")
                return original_node.with_changes(
                    handlers=non_defensive_handlers
                )
            elif original_node.orelse:
                # 只有 else 块而没有 except 或 finally 块，这是无效的，需要移除整个 try 块
                decision = "✓ 移除整个防御式 try-except (else 块无效)"
                filename = os.path.basename(self.filename)
                print(f"{filename}:{line_number} - {decision}")
                print(f"  原因：{reason}")
                return cst.FlattenSentinel(original_node.body.body)
            else:
                # 没有其他结构，移除整个 try 块
                decision = "✓ 移除整个防御式 try-except"
                filename = os.path.basename(self.filename)
                print(f"{filename}:{line_number} - {decision}")
                print(f"  原因：{reason}")
                return cst.FlattenSentinel(original_node.body.body)
        
        return updated_node


def rewrite_file_for_defensive_try_except(
    file_path: str,
    max_try_length: int = 30,
    dry_run: bool = False,
    check_print_log: bool = True,
    check_rethrow: bool = True,
    check_return_none: bool = True
) -> Optional[str]:
    """重写单个文件以移除防御式 try-except"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 解析代码
        try:
            module = cst.parse_module(source_code)
        except Exception as e:
            print(f"解析文件 {file_path} 时出错: {e}")
            return None
        
        # 创建转换器
        transformer = DefensiveTryExceptTransformer(
            max_try_length, 
            dry_run,
            check_print_log,
            check_rethrow,
            check_return_none,
            file_path  # 传递完整路径
        )
        
        # 应用转换
        transformed_module = module.visit(transformer)
        
        # 检查是否有变化
        if not transformer.changes_made:
            return None
        
        transformed_code = transformed_module.code
        
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transformed_code)
        
        return transformed_code
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return None


def rewrite_directory_for_defensive_try_except(
    path: str,
    max_try_length: int = 30,
    dry_run: bool = False,
    output_diff: Optional[str] = None,
    check_print_log: bool = True,
    check_rethrow: bool = True,
    check_return_none: bool = True
) -> List[str]:
    """重写目录或单个文件中的所有 Python 文件以移除防御式 try-except"""
    modified_files = []
    
    if os.path.isfile(path) and path.endswith('.py'):
        # 处理单个文件
        transformed_code = rewrite_file_for_defensive_try_except(
            path,
            max_try_length,
            dry_run,
            check_print_log,
            check_rethrow,
            check_return_none
        )
        
        if transformed_code is not None:
            modified_files.append(path)
            
            # 如果需要输出 diff 且是 dry_run
            if dry_run and output_diff:
                with open(path, 'r', encoding='utf-8') as f:
                    original_code = f.read()
                
                # 生成 diff
                diff_text = ''.join(difflib.unified_diff(
                    original_code.splitlines(True),
                    transformed_code.splitlines(True),
                    fromfile=path,
                    tofile=f"{path}.modified"
                ))
                
                # 写入 diff 文件
                with open(output_diff, 'a', encoding='utf-8') as f:
                    f.write(diff_text)
    
    elif os.path.isdir(path):
        # 遍历目录
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    
                    # 重写文件
                    transformed_code = rewrite_file_for_defensive_try_except(
                        file_path,
                        max_try_length,
                        dry_run,
                        check_print_log,
                        check_rethrow,
                        check_return_none
                    )
                    
                    if transformed_code is not None:
                        modified_files.append(file_path)
                        
                        # 如果需要输出 diff 且是 dry_run
                        if dry_run and output_diff:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                original_code = f.read()
                            
                            # 生成 diff
                            diff_text = ''.join(difflib.unified_diff(
                                original_code.splitlines(True),
                                transformed_code.splitlines(True),
                                fromfile=file_path,
                                tofile=f"{file_path}.modified"
                            ))
                            
                            # 写入 diff 文件
                            with open(output_diff, 'a', encoding='utf-8') as f:
                                f.write(diff_text)
    
    return modified_files
