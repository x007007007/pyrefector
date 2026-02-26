import libcst as cst
from typing import List, Optional, Set, Tuple
import os
import difflib


def is_defensive_try_except(try_node: cst.Try, max_try_length: int = 30) -> bool:
    """判断是否是防御式 try-except 语句
    
    防御式 try-except 的特点：
    1. 包含至少一个 except 子句
    2. 捕获所有异常（except: 或 except Exception:）
    3. try 块过长（超过指定长度）
    """
    print("Checking try node:", type(try_node))
    
    # 检查是否有 except 子句
    if not try_node.handlers:
        print("No handlers")
        return False
    
    # 检查 except 子句是否捕获所有异常
    has_catch_all = False
    for handler in try_node.handlers:
        print(f"Handler type: {handler.type}")
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
    print(f"Try length: {try_length}, max allowed: {max_try_length}")
    
    # 判断是否是防御式 try-except
    if has_catch_all and try_length > max_try_length:
        print(f"✓ 检测到防御式 try-except: 长度 {try_length}（阈值: {max_try_length}）")
        return True
    
    print("✗ Not a defensive try-except")
    return False


class DefensiveTryExceptTransformer(cst.CSTTransformer):
    """用于移除防御式 try-except 的转换器"""
    
    def __init__(self, max_try_length: int = 30, dry_run: bool = False):
        self.max_try_length = max_try_length
        self.dry_run = dry_run
        self.changes_made = False
    
    def visit_Everything(self, node: cst.CSTNode) -> Optional[bool]:
        """访问所有节点，专门寻找 Try 节点"""
        if isinstance(node, cst.Try):
            print(f"Found try node at visit")
            return True
        return True
    
    def leave_Try(self, original_node: cst.Try, updated_node: cst.Try) -> cst.CSTNode:
        """处理 Try 节点"""
        print(f"Leaving try node, checking if defensive")
        if is_defensive_try_except(original_node, self.max_try_length):
            self.changes_made = True
            print(f"✓ 移除防御式 try-except")
            # 移除 try-except，直接返回 try 块的内容
            return cst.FlattenSentinel(original_node.body.body)
        return updated_node


def rewrite_file_for_defensive_try_except(
    file_path: str,
    max_try_length: int = 30,
    dry_run: bool = False
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
        transformer = DefensiveTryExceptTransformer(max_try_length, dry_run)
        
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
    directory: str,
    max_try_length: int = 30,
    dry_run: bool = False,
    output_diff: Optional[str] = None
) -> List[str]:
    """重写目录中的所有 Python 文件以移除防御式 try-except"""
    modified_files = []
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                
                # 重写文件
                transformed_code = rewrite_file_for_defensive_try_except(
                    file_path,
                    max_try_length,
                    dry_run
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
