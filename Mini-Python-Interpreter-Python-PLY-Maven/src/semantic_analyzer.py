from .ast_nodes import *

def semantic_analysis(ast):
    symbol_table = {}
    errors = []
    type_info = {}
    
    def get_type(value):
        if isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, list):
            return "list"
        elif value is None:
            return "None"
        return str(type(value).__name__)

    def visit(node):
        if isinstance(node, list):
            for n in node:
                visit(n)
            return None
        elif hasattr(node, "__class__"):
            cname = node.__class__.__name__
            
            if cname == "Assign":
                value = visit(node.expr)
                var_name = node.name.name if hasattr(node.name, 'name') else node.name
                type_info[var_name] = get_type(value)
                symbol_table[var_name] = value
                return value
                
            elif cname == "Identifier":
                var_name = node.name
                if var_name not in symbol_table:
                    errors.append(f"❌ Undeclared variable: '{var_name}'")
                    return None
                return symbol_table[var_name]
                
            elif cname == "BinaryOp":
                left = visit(node.left)
                right = visit(node.right)
                left_type = get_type(left)
                right_type = get_type(right)
                
                if left is not None and right is not None:
                    if node.op in ['+', '-', '*', '/', '%']:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            errors.append(f"❌ Type mismatch in arithmetic operation '{node.op}': {left_type} and {right_type}")
                    elif node.op in ['<', '>', '<=', '>=', '==', '!=']:
                        if left_type != right_type:
                            errors.append(f"❌ Type mismatch in comparison '{node.op}': {left_type} and {right_type}")
                    elif node.op in ['and', 'or']:
                        if left_type != 'bool' or right_type != 'bool':
                            errors.append(f"❌ Type mismatch in logical operation '{node.op}': {left_type} and {right_type}")
                return None
                
            elif cname == "Number":
                return node.value
                
            elif cname == "String":
                return node.value
                
            elif cname == "Boolean":
                return node.value
                
            elif cname == "Print":
                expr = visit(node.expr)
                if expr is not None:
                    type_info['print_expr'] = get_type(expr)
                return None
                
            elif cname == "IfElse":
                cond = visit(node.condition)
                if cond is not None and get_type(cond) != 'bool':
                    errors.append(f"❌ Condition must be a boolean, got {get_type(cond)}")
                visit(node.if_body)
                if node.else_body:
                    visit(node.else_body)
                return None
                
            elif cname == "WhileLoop":
                cond = visit(node.condition)
                if cond is not None and get_type(cond) != 'bool':
                    errors.append(f"❌ While loop condition must be a boolean, got {get_type(cond)}")
                visit(node.body)
                return None
                
            elif cname == "ForLoop":
                var_name = node.var.name if hasattr(node.var, 'name') else node.var
                iterable = visit(node.iterable)
                if iterable is not None:
                    iter_type = get_type(iterable)
                    if iter_type not in ['list', 'range']:
                        errors.append(f"❌ For loop iterable must be a list or range, got {iter_type}")
                old_symbol_table = symbol_table.copy()
                symbol_table[var_name] = None
                visit(node.body)
                symbol_table.clear()
                symbol_table.update(old_symbol_table)
                return None
                
            elif cname == "FunctionDef":
                func_name = node.name
                symbol_table[func_name] = "function"
                type_info[func_name] = "function"
                old_symbol_table = symbol_table.copy()
                for param in node.params:
                    symbol_table[param] = None
                    type_info[param] = "parameter"
                visit(node.body)
                symbol_table.clear()
                symbol_table.update(old_symbol_table)
                return None
                
            elif cname == "FunctionCall":
                func_name = node.name.name if hasattr(node.name, 'name') else node.name
                if func_name not in symbol_table:
                    errors.append(f"❌ Undeclared function: '{func_name}'")
                for arg in node.args:
                    visit(arg)
                return None
                
            elif cname == "ListNode":
                elements = [visit(elem) for elem in node.elements]
                return elements
                
            elif cname == "IndexNode":
                lst = visit(node.expr)
                idx = visit(node.index)
                if lst is not None and get_type(lst) != 'list':
                    errors.append(f"❌ Indexing requires a list, got {get_type(lst)}")
                if idx is not None and get_type(idx) != 'int':
                    errors.append(f"❌ List index must be an integer, got {get_type(idx)}")
                return None
                
            elif cname == "StringMethod":
                string_obj = visit(node.expr) # FIXED: Changed string_obj to expr
                if string_obj is not None and get_type(string_obj) != 'str':
                    errors.append(f"❌ String method '{node.method}' called on non-string type: {get_type(string_obj)}")
                for arg in getattr(node, 'args', []) or []:
                    visit(arg)
                return None
                
            elif cname == "RangeCall":
                args = [node.start, node.stop, node.step]
                for i, arg in enumerate(args):
                    val = visit(arg) if arg is not None else None
                    if val is not None and get_type(val) != 'int':
                        errors.append(f"❌ Range argument {i+1} must be an integer, got {get_type(val)}")
                return None
                
            elif cname == "Return":
                value = visit(node.expr)
                if value is not None:
                    type_info['return_value'] = get_type(value)
                return None
                
            elif cname == "TryExcept":
                visit(node.try_body)
                visit(node.except_body)
                return None
                
            elif cname == "LenFunction":
                expr = visit(node.expr)
                if expr is not None:
                    expr_type = get_type(expr)
                    if expr_type not in ['list', 'str']:
                        errors.append(f"❌ len() requires a list or string, got {expr_type}")
                return None
                
            elif cname == "UnaryOp":
                expr = visit(node.expr)
                if expr is not None:
                    expr_type = get_type(expr)
                    if node.op == '-' and expr_type not in ['int', 'float']:
                        errors.append(f"❌ Unary minus requires a number, got {expr_type}")
                    elif node.op == 'not' and expr_type != 'bool':
                        errors.append(f"❌ Logical not requires a boolean, got {expr_type}")
                return None
                
            return None
        return None

    visit(ast)
    
    # Format the output
    output = []
    if errors:
        output.append("❌ Semantic Errors Found:")
        for error in errors:
            output.append(f"  {error}")
    else:
        output.append("✅ No semantic errors found!")
        
    output.append("\nType Information:")
    output.append("----------------")
    for var, type_name in type_info.items():
        output.append(f"  {var}: {type_name}")
        
    output.append("\nSymbol Table:")
    output.append("-------------")
    for var, value in symbol_table.items():
        if value == "function":
            output.append(f"  {var}: function")
        else:
            output.append(f"  {var}: {get_type(value)}")
            
    return len(errors) == 0, "\n".join(output)
