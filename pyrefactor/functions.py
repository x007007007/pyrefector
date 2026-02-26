import libcst as cst
from typing import List, Optional, Tuple, Dict
from libcst.metadata import MetadataWrapper, PositionProvider
import re
import ast


class VariableScopeAnalyzer:
    """使用 ast 分析变量作用域的简单实现，仅跟踪函数内部定义的变量"""
    
    def __init__(self):
        self.defined_variables = set()
        self.used_variables = set()
        self.scope_stack = []  # 用于跟踪嵌套作用域的变量
    
    def visit_Assign(self, node):
        """处理赋值语句"""
        if self.scope_stack:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_variables.add(target.id)
    
    def visit_AnnAssign(self, node):
        """处理注释赋值"""
        if self.scope_stack and isinstance(node.target, ast.Name):
            self.defined_variables.add(node.target.id)
    
    def visit_For(self, node):
        """处理 for 循环"""
        if self.scope_stack and isinstance(node.target, ast.Name):
            self.defined_variables.add(node.target.id)
    
    def visit_Name(self, node):
        """处理变量引用"""
        if self.scope_stack and isinstance(node, ast.Name):
            self.used_variables.add(node.id)
    
    def visit_FunctionDef(self, node):
        """处理函数定义"""
        # 保存当前作用域
        previous_scope = list(self.scope_stack)
        
        # 进入新的作用域
        self.scope_stack.append(node)
        
        # 添加函数参数到定义的变量中
        for arg in node.args.args:
            self.defined_variables.add(arg.arg)
        
        # 遍历函数体
        for stmt in node.body:
            self.visit(stmt)
        
        # 恢复之前的作用域
        self.scope_stack = previous_scope
    
    def visit(self, node):
        """通用访问方法"""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """默认访问方法"""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
            elif isinstance(value, ast.AST):
                self.visit(value)
    
    def analyze(self, source_code):
        """分析源代码的变量作用域"""
        tree = ast.parse(source_code)
        
        # 遍历所有函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit_FunctionDef(node)
        
        # 过滤掉内置函数和标准库函数
        builtins = {'print', 'len', 'sum', 'min', 'max', 'open', 'float', 'ValueError'}
        filtered_used = [var for var in self.used_variables if var not in builtins]
        
        # 只返回实际使用的变量（即在函数内部使用的变量）
        actual_used = [var for var in filtered_used if var in self.defined_variables]
        
        return list(self.defined_variables), actual_used


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
    
    def __init__(self, source_lines: List[str], metadata, existing_function_names: List[str], process_methods: bool = False):
        self.source_lines = source_lines
        self.metadata = metadata
        self._in_function = 0
        self._in_class = 0  # 跟踪当前是否在类定义内部
        self._subfunctions: List[cst.FunctionDef] = []
        self._current_subfunction: List[cst.CSTNode] = []
        self._current_context: Optional[str] = None
        self._function_levels: List[int] = []
        self._class_levels: List[int] = []
        # 跟踪所有已存在的和已创建的函数名称
        self._function_names: Dict[str, int] = {}
        for func_name in existing_function_names:
            self._function_names[func_name] = 0
        self._suffix_counter: int = 0  # 每个函数的后缀计数器
        self._original_func_name: str = ""  # 当前正在处理的原函数名
        self._process_methods: bool = process_methods  # 控制是否处理类内部的方法
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """访问类定义节点"""
        self._in_class += 1
        self._class_levels.append(self._in_class)
        print(f"访问类: {node.name.value}, 嵌套级别: {self._in_class}")
        return True  # 继续访问类的内部节点
    
    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.CSTNode:
        """离开类定义节点"""
        self._in_class -= 1
        self._class_levels.pop()
        print(f"离开类: {original_node.name.value}")
        
        # 如果有子函数需要添加到类的 body 中
        if self._subfunctions:
            print(f"添加 {len(self._subfunctions)} 个子函数到类中")
            new_body = list(updated_node.body.body)
            new_body.extend(self._subfunctions)
            self._subfunctions = []  # 清空子函数列表
            return updated_node.with_changes(
                body=updated_node.body.with_changes(body=tuple(new_body))
            )
        
        return updated_node
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self._in_function += 1
        self._function_levels.append(self._in_function)
        
        print(f"访问函数: {node.name.value}, 嵌套级别: {self._in_function}, 是否在类内部: {self._in_class > 0}")
        
        # 对于每个新的顶级函数或类内部的方法（如果启用），初始化后缀计数器
        if self._in_function == 1 or (self._in_class > 0 and self._process_methods):
            self._suffix_counter = 1
            self._original_func_name = node.name.value
        
        # 确定是否应该处理当前函数：
        # 1. 顶级函数总是处理
        # 2. 类内部的方法只有在 process_methods 为 True 时才处理
        # 3. 嵌套函数不处理
        if self._in_function > 1 or (self._in_class > 0 and not self._process_methods):
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
                
                # 为子函数添加适当的参数：
                # 如果是在类内部，我们需要添加 self 参数，以便子函数可以访问实例属性
                if self._in_class > 0:
                    subfunc = cst.FunctionDef(
                        name=cst.Name(value=subfunc_name),
                        params=cst.Parameters(params=(cst.Param(name=cst.Name(value="self")),)),
                        body=cst.IndentedBlock(body=tuple(subfunc_body))
                    )
                    # 在调用子函数时也需要传递 self
                    new_body.append(
                        cst.SimpleStatementLine(
                            body=(
                                cst.Expr(
                                    value=cst.Call(
                                        func=cst.Name(value=subfunc_name),
                                        args=(cst.Arg(value=cst.Name(value="self")),),
                                    )
                                ),
                            )
                        )
                    )
                else:
                    subfunc = cst.FunctionDef(
                        name=cst.Name(value=subfunc_name),
                        params=cst.Parameters(params=()),
                        body=cst.IndentedBlock(body=tuple(subfunc_body))
                    )
                    # 顶级函数的子函数调用不需要 self
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
                
                self._subfunctions.append(subfunc)
                
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
            
            # 根据是否在类内部来确定子函数的参数
            if self._in_class > 0:
                subfunc = cst.FunctionDef(
                    name=cst.Name(value=subfunc_name),
                    params=cst.Parameters(params=(cst.Param(name=cst.Name(value="self")),)),
                    body=cst.IndentedBlock(body=tuple(subfunc_body))
                )
                new_body.append(
                    cst.SimpleStatementLine(
                        body=(
                            cst.Expr(
                                value=cst.Call(
                                    func=cst.Name(value=subfunc_name),
                                    args=(cst.Arg(value=cst.Name(value="self")),),
                                )
                            ),
                        )
                    )
                )
            else:
                subfunc = cst.FunctionDef(
                    name=cst.Name(value=subfunc_name),
                    params=cst.Parameters(params=()),
                    body=cst.IndentedBlock(body=tuple(subfunc_body))
                )
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
            
            self._subfunctions.append(subfunc)
        
        # 创建重构后的主函数
        new_func = updated_node.with_changes(
            body=cst.IndentedBlock(body=tuple(new_body))
        )
        
        print(f"子函数数量: {len(self._subfunctions)}")
        
        # 组合主函数和子函数
        if self._subfunctions:
            if self._in_class > 0:
                # 如果是在类内部，我们不能直接返回 FlattenSentinel，而是需要将子函数添加到类的 body 中
                # 这里我们需要特殊处理，但 LibCST 不允许在 FunctionDef 内部直接返回其他类型
                # 我们将子函数保留到 self._subfunctions 中，在 leave_ClassDef 中统一处理
                return new_func
            else:
                # 如果是顶级函数，可以直接使用 FlattenSentinel
                result = [new_func]
                result.extend(self._subfunctions)
                return cst.FlattenSentinel(result)
        
        return new_func


def rewrite_file_for_functions(source_code: str, process_methods: bool = False) -> str:
    """
    重写文件，将大函数切割为小函数
    
    参数:
        source_code: 源代码字符串
        process_methods: 是否同时处理类内部的方法，默认为 False
    """
    lines = source_code.splitlines()
    
    try:
        # 使用 metadata wrapper 来获取位置信息
        wrapper = MetadataWrapper(cst.parse_module(source_code))
        
        # 收集所有已存在的函数名称（包括类内部的方法）
        existing_function_names: List[str] = []
        
        # 收集顶级函数
        for node in wrapper.module.body:
            if isinstance(node, cst.FunctionDef):
                existing_function_names.append(node.name.value)
            elif isinstance(node, cst.ClassDef):
                # 收集类内部的方法
                for body_node in node.body.body:
                    if isinstance(body_node, cst.FunctionDef):
                        existing_function_names.append(body_node.name.value)
        
        # 获取 PositionProvider 元数据
        metadata = wrapper.resolve(PositionProvider)
        
        # 访问模块以建立完整的元数据
        wrapper.module.visit(cst.CSTVisitor())
        
        # 使用我们的转换器进行重构，传递已存在的函数名称和方法处理标志
        transformer = FunctionSplitter(lines, metadata, existing_function_names, process_methods)
        new_module = wrapper.module.visit(transformer)
        
        return new_module.code
    except Exception as e:
        print(f"解析错误: {e}")
        return source_code


def rewrite_directory_for_functions(path: str, dry_run: bool = False, output_diff: str = None, process_methods: bool = False) -> List[str]:
    """
    重写目录中的所有文件，将大函数切割为小函数
    
    参数:
        path: 要处理的文件或目录路径
        dry_run: 是否进行干运行（只检查不修改），默认为 False
        output_diff: 是否输出差异，默认为 None
        process_methods: 是否同时处理类内部的方法，默认为 False
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
        
        rewritten = rewrite_file_for_functions(source, process_methods)
        
        if rewritten != source:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(rewritten)
            
            changes.append(file_path)
    
    if output_diff and changes:
        pass  # TODO: 实现 diff 生成
    
    return changes