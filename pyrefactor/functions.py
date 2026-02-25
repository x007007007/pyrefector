import libcst as cst
import re
from typing import List, Optional, Tuple, Dict
from libcst.metadata import MetadataWrapper, PositionProvider


def extract_comment_context(node: cst.CSTNode, lines: List[str], metadata) -> Optional[str]:
    """
    从函数体或语句前的注释中提取上下文描述
    """
    # 使用 libcst 的元数据获取位置信息
    position = metadata.get(node, None)
    
    if position is None:
        return None
    
    lineno = position.start.line
    
    # 查找前导注释
    comments: List[str] = []
    line_num = lineno - 2
    
    while line_num >= 0 and line_num < len(lines):
        line = lines[line_num].strip()
        
        # 如果是空行，继续向上查找
        if not line:
            line_num -= 1
            continue
            
        # 如果是注释，添加到列表
        if line.startswith('#'):
            # 去除 # 和可选的空格
            comment_text = line[1:].strip()
            if comment_text:
                comments.append(comment_text)
            line_num -= 1
        else:
            # 遇到非注释、非空行，停止查找
            break
    
    # 反转注释列表（从上到下）
    comments.reverse()
    
    # 检查是否有有意义的注释
    if comments:
        return ' '.join(comments)
    
    return None


def create_subfunction_name(original_func_name: str, context_desc: str, suffix_counter: int) -> str:
    """
    根据原函数名和上下文描述生成安全的子函数名称
    """
    # 首先创建基础名称：原函数名 + 后缀编号
    base_name = f"{original_func_name}_{suffix_counter}"
    
    # 确保名称符合 Python 标识符规范
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
    
    # 确保名称不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = f"_{safe_name}"
    
    return safe_name


class FunctionSplitter(cst.CSTTransformer):
    """
    将大函数切割为多个小函数的 CST 转换器
    """
    
    def __init__(self, source_lines: List[str], metadata, existing_function_names: List[str]):
        self.source_lines = source_lines
        self.metadata = metadata
        self._in_function = 0
        self._subfunctions: List[cst.FunctionDef] = []
        self._current_subfunction: List[cst.CSTNode] = []
        self._current_context: Optional[str] = None
        self._function_levels: List[int] = []
        # 跟踪所有已存在的和已创建的函数名称
        self._function_names: Dict[str, int] = {}
        for func_name in existing_function_names:
            self._function_names[func_name] = 0
        self._suffix_counter: int = 0  # 每个函数的后缀计数器
        self._original_func_name: str = ""  # 当前正在处理的原函数名
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self._in_function += 1
        self._function_levels.append(self._in_function)
        
        print(f"访问函数: {node.name.value}, 嵌套级别: {self._in_function}")
        
        # 对于每个新的顶级函数，初始化后缀计数器
        if self._in_function == 1:
            self._suffix_counter = 1
            self._original_func_name = node.name.value
        
        # 只处理非嵌套函数
        if self._in_function > 1:
            return False
        return True
    
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.CSTNode:
        self._in_function -= 1
        self._function_levels.pop()
        
        print(f"离开函数: {original_node.name.value}")
        
        # 只处理非嵌套函数
        if self._in_function > 0:
            return updated_node
        
        # 重构函数体
        new_body: List[cst.CSTNode] = []
        
        print(f"函数体语句数量: {len(original_node.body.body)}")
        
        for i, node in enumerate(original_node.body.body):
            print(f"\n处理语句 {i}: {type(node)}")
            
            # 尝试提取当前节点的上下文
            context = extract_comment_context(node, self.source_lines, self.metadata)
            print(f"提取到的上下文: {repr(context)}")
            
            if context and self._current_subfunction:
                # 如果有新的上下文描述且当前正在收集子函数，保存当前子函数
                subfunc_name = create_subfunction_name(self._original_func_name, self._current_context, self._suffix_counter)
                self._suffix_counter += 1
                
                # 确保子函数名称不重复
                if subfunc_name in self._function_names:
                    # 如果名称已存在，添加数字后缀
                    counter = self._function_names[subfunc_name] + 1
                    while f"{subfunc_name}_{counter}" in self._function_names:
                        counter += 1
                    subfunc_name = f"{subfunc_name}_{counter}"
                    self._function_names[subfunc_name] = counter
                else:
                    self._function_names[subfunc_name] = 0
                
                print(f"创建子函数: {subfunc_name}")
                
                # 创建新的子函数，包含文档字符串
                docstring = None
                if self._current_context:
                    docstring = cst.SimpleStatementLine(
                        body=(
                            cst.Expr(
                                value=cst.SimpleString(
                                    value=f'"""{" ".join(self._current_context.splitlines())}"""'
                                )
                            ),
                        )
                    )
                
                # 构造子函数体
                subfunc_body = []
                if docstring:
                    subfunc_body.append(docstring)
                subfunc_body.extend(self._current_subfunction)
                
                subfunc = cst.FunctionDef(
                    name=cst.Name(value=subfunc_name),
                    params=cst.Parameters(params=()),
                    body=cst.IndentedBlock(body=tuple(subfunc_body))
                )
                
                self._subfunctions.append(subfunc)
                
                # 在主函数中添加对子函数的调用
                new_body.append(
                    cst.SimpleStatementLine(
                        body=(
                            cst.Expr(
                                value=cst.Call(
                                    func=cst.Name(value=subfunc_name),
                                    args=(),
                                )
                            ),
                        )
                    )
                )
                
                self._current_subfunction = []
            
            if context:
                # 开始新的子函数
                print(f"开始新的子函数，上下文: {context}")
                self._current_context = context
            
            # 添加到当前子函数或主函数体
            if self._current_context:
                self._current_subfunction.append(node)
                print(f"添加到当前子函数 (共 {len(self._current_subfunction)} 个语句)")
            else:
                new_body.append(node)
                print("添加到主函数体")
        
        # 处理最后一个子函数
        if self._current_subfunction and self._current_context:
            subfunc_name = create_subfunction_name(self._original_func_name, self._current_context, self._suffix_counter)
            self._suffix_counter += 1
            
            # 确保子函数名称不重复
            if subfunc_name in self._function_names:
                # 如果名称已存在，添加数字后缀
                counter = self._function_names[subfunc_name] + 1
                while f"{subfunc_name}_{counter}" in self._function_names:
                    counter += 1
                subfunc_name = f"{subfunc_name}_{counter}"
                self._function_names[subfunc_name] = counter
            else:
                self._function_names[subfunc_name] = 0
            
            print(f"创建最后一个子函数: {subfunc_name}")
            
            # 创建新的子函数，包含文档字符串
            docstring = None
            if self._current_context:
                docstring = cst.SimpleStatementLine(
                    body=(
                        cst.Expr(
                            value=cst.SimpleString(
                                value=f'"""{" ".join(self._current_context.splitlines())}"""'
                            )
                        ),
                    )
                )
            
            # 构造子函数体
            subfunc_body = []
            if docstring:
                subfunc_body.append(docstring)
            subfunc_body.extend(self._current_subfunction)
            
            subfunc = cst.FunctionDef(
                name=cst.Name(value=subfunc_name),
                params=cst.Parameters(params=()),
                body=cst.IndentedBlock(body=tuple(subfunc_body))
            )
            
            self._subfunctions.append(subfunc)
            
            new_body.append(
                cst.SimpleStatementLine(
                    body=(
                        cst.Expr(
                            value=cst.Call(
                                func=cst.Name(value=subfunc_name),
                                args=(),
                            )
                        ),
                    )
                )
            )
        
        # 创建重构后的主函数
        new_func = updated_node.with_changes(
            body=cst.IndentedBlock(body=tuple(new_body))
        )
        
        print(f"子函数数量: {len(self._subfunctions)}")
        
        # 组合主函数和子函数
        if self._subfunctions:
            result = [new_func]
            result.extend(self._subfunctions)
            return cst.FlattenSentinel(result)
        
        return new_func


def rewrite_file_for_functions(source_code: str) -> str:
    """
    重写文件，将大函数切割为小函数
    """
    lines = source_code.splitlines()
    
    try:
        # 使用 metadata wrapper 来获取位置信息
        wrapper = MetadataWrapper(cst.parse_module(source_code))
        
        # 收集所有已存在的函数名称
        existing_function_names: List[str] = []
        for node in wrapper.module.body:
            if isinstance(node, cst.FunctionDef):
                existing_function_names.append(node.name.value)
        
        # 获取 PositionProvider 元数据
        metadata = wrapper.resolve(PositionProvider)
        
        # 访问模块以建立完整的元数据
        wrapper.module.visit(cst.CSTVisitor())
        
        # 使用我们的转换器进行重构，传递已存在的函数名称
        transformer = FunctionSplitter(lines, metadata, existing_function_names)
        new_module = wrapper.module.visit(transformer)
        
        return new_module.code
    except Exception as e:
        print(f"解析错误: {e}")
        return source_code


def rewrite_directory_for_functions(path: str, dry_run: bool = False, output_diff: str = None) -> List[str]:
    """
    重写目录中的所有文件，将大函数切割为小函数
    """
    import os
    import difflib
    from .deps import list_python_files
    
    changes: List[str] = []
    
    # 确定要处理的文件列表
    if os.path.isfile(path):
        file_paths = [path]
    elif os.path.isdir(path):
        file_paths = list_python_files(path)
    else:
        print(f"错误：路径 '{path}' 不存在")
        return changes
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        rewritten = rewrite_file_for_functions(source)
        
        if rewritten != source:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(rewritten)
            
            changes.append(file_path)
    
    if output_diff and changes:
        pass  # TODO: 实现 diff 生成
    
    return changes
