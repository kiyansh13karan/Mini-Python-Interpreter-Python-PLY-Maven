from .ast_nodes import *

def generate_icg(ast):
    code_lines = []
    temp_counter = [0]
    label_counter = [0]
    
    def new_temp():
        temp_counter[0] += 1
        return f"t{temp_counter[0]}"
        
    def new_label():
        label_counter[0] += 1
        return f"L{label_counter[0]}"
        
    def visit(node):
        if isinstance(node, list):
            for n in node:
                visit(n)
            return None
        elif hasattr(node, "__class__"):
            cname = node.__class__.__name__
            
            if cname == "Assign":
                rhs = visit(node.expr)
                code_lines.append(f"{node.name} = {rhs}")
                return node.name
                
            elif cname == "Number":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.value}")
                return temp
                
            elif cname == "String":
                temp = new_temp()
                code_lines.append(f"{temp} = '{node.value}'")
                return temp
                
            elif cname == "Boolean":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.value}")
                return temp
                
            elif cname == "Identifier":
                temp = new_temp()
                code_lines.append(f"{temp} = {node.name}")
                return temp
                
            elif cname == "BinaryOp":
                left = visit(node.left)
                right = visit(node.right)
                temp = new_temp()
                code_lines.append(f"{temp} = {left} {node.op} {right}")
                return temp
                
            elif cname == "UnaryOp":
                expr = visit(node.expr)
                temp = new_temp()
                code_lines.append(f"{temp} = {node.op} {expr}")
                return temp
                
            elif cname == "Print":
                val = visit(node.expr)
                code_lines.append(f"print {val}")
                return None
                
            elif cname == "IfElse":
                cond = visit(node.condition)
                else_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"if {cond} == False goto {else_label}")
                for stmt in node.if_body:
                    visit(stmt)
                code_lines.append(f"goto {end_label}")
                code_lines.append(f"{else_label}:")
                if node.else_body:
                    for stmt in node.else_body:
                        visit(stmt)
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "WhileLoop":
                start_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"{start_label}:")
                cond = visit(node.condition)
                code_lines.append(f"if {cond} == False goto {end_label}")
                for stmt in node.body:
                    visit(stmt)
                code_lines.append(f"goto {start_label}")
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "ForLoop":
                start_label = new_label()
                end_label = new_label()
                iter_var = new_temp()
                
                # Initialize iterator
                iter_expr = visit(node.iterable)
                code_lines.append(f"{iter_var} = {iter_expr}")
                
                code_lines.append(f"{start_label}:")
                # Check if iteration is complete
                code_lines.append(f"if {iter_var} == None goto {end_label}")
                
                # Assign current value to loop variable
                code_lines.append(f"{node.var} = {iter_var}")
                
                # Execute loop body
                for stmt in node.body:
                    visit(stmt)
                    
                # Move to next iteration
                code_lines.append(f"goto {start_label}")
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "FunctionDef":
                code_lines.append(f"function {node.name}:")
                for param in node.params:
                    code_lines.append(f"param {param}")
                for stmt in node.body:
                    visit(stmt)
                return None
                
            elif cname == "FunctionCall":
                args = [visit(arg) for arg in node.args]
                # Convert None to 'None' string to avoid join error
                safe_args = [str(a) if a is not None else "None" for a in args]
                temp = new_temp()
                code_lines.append(f"{temp} = call {node.name}({', '.join(safe_args)})")
                return temp
                
            elif cname == "ListNode":
                temp = new_temp()
                code_lines.append(f"{temp} = []")
                for elem in node.elements:
                    elem_temp = visit(elem)
                    code_lines.append(f"{temp}.append({elem_temp})")
                return temp
                
            elif cname == "IndexNode":
                lst = visit(node.expr)
                idx = visit(node.index)
                temp = new_temp()
                code_lines.append(f"{temp} = {lst}[{idx}]")
                return temp
                
            elif cname == "ListAssign":
                lst = visit(node.expr)
                idx = visit(node.index)
                val = visit(node.value)
                code_lines.append(f"{lst}[{idx}] = {val}")
                return None
                
            elif cname == "Return":
                val = visit(node.expr)
                code_lines.append(f"return {val}")
                return None
                
            elif cname == "Break":
                code_lines.append("break")
                return None
                
            elif cname == "Continue":
                code_lines.append("continue")
                return None
                
            elif cname == "TryExcept":
                try_label = new_label()
                except_label = new_label()
                end_label = new_label()
                
                code_lines.append(f"{try_label}:")
                for stmt in node.try_body: # FIXED: Changed try_block to try_body
                    visit(stmt)
                code_lines.append(f"goto {end_label}")
                
                code_lines.append(f"{except_label}:")
                for stmt in node.except_body: # FIXED: Changed except_block to except_body
                    visit(stmt)
                    
                code_lines.append(f"{end_label}:")
                return None
                
            elif cname == "StringMethod":
                string_obj = visit(node.expr) # FIXED: Changed string_obj to expr
                temp = new_temp()
                if node.method == "upper":
                    code_lines.append(f"{temp} = {string_obj}.upper()")
                elif node.method == "lower":
                    code_lines.append(f"{temp} = {string_obj}.lower()")
                elif node.method == "strip":
                    code_lines.append(f"{temp} = {string_obj}.strip()")
                elif node.method == "replace":
                    args = [visit(arg) for arg in node.args]
                    code_lines.append(f"{temp} = {string_obj}.replace({args[0]}, {args[1]})")
                return temp
                
            elif cname == "LenFunction":
                expr = visit(node.expr)
                temp = new_temp()
                code_lines.append(f"{temp} = len({expr})")
                return temp
                
            elif cname == "RangeCall":
                start = visit(node.start) if node.start else "0"
                stop = visit(node.stop) if node.stop else "None"
                step = visit(node.step) if node.step else "1"
                temp = new_temp()
                code_lines.append(f"{temp} = range({start}, {stop}, {step})")
                return temp
                
            return None
        return None

    visit(ast)
    
    # Format the output
    output = []
    output.append("Intermediate Code (Three-Address Code):")
    output.append("=====================================")
    output.append("")
    
    for i, line in enumerate(code_lines, 1):
        output.append(f"{i:3d} | {line}")
        
    output.append("\nLegend:")
    output.append("-------")
    output.append("tN    : Temporary variable")
    output.append("LN    : Label")
    output.append("goto  : Jump instruction")
    output.append("call  : Function call")
    output.append("param : Function parameter")
    
    return "\n".join(output)
