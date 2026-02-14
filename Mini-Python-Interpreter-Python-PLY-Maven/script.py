import tkinter as tk
from tkinter import ttk, font, filedialog, PhotoImage
import base64
import sys
import io
from lexer import lexer, tokenize, format_token_output
from myparser import parser
from interpreter import Interpreter
from semantic_analyzer import semantic_analysis
from icg_generator import generate_icg
import re
from ast_nodes import *  # Import all AST node classes at the top of script.py

# --- Tooltip Helper ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#333", foreground="#FFD700",
                         relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 10, "normal"))
        label.pack(ipadx=8, ipady=4)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# ---------- Functions ----------

def go_to_learning():
    """Show the learning screen."""
    hide_all()
    learn_screen.pack(fill=tk.BOTH, expand=True)

def go_to_testing():
    """Show the testing screen."""
    hide_all()
    testing_screen.pack(fill=tk.BOTH, expand=True)
    # Create the enhanced background when showing the screen
    root.after(100, create_testing_background)

def go_to_optimizer():
    """Show the optimizer screen."""
    hide_all()
    optimizer_screen.pack(fill=tk.BOTH, expand=True)

def go_to_compiler_phases():
    """Show the compiler phases screen."""
    hide_all()
    compiler_phases_screen.pack(fill=tk.BOTH, expand=True)
    # Create the enhanced background when showing the screen
    root.after(100, create_compiler_background)

def back_to_welcome():
    """Return to the welcome screen."""
    hide_all()
    welcome_screen.pack(fill=tk.BOTH, expand=True)
    # Refresh the background when returning to welcome screen
    create_hacking_background()

def hide_all():
    """Hide all main screens."""
    welcome_screen.pack_forget()
    testing_screen.pack_forget()
    compiler_phases_screen.pack_forget()
    optimizer_screen.pack_forget()
    learn_screen.pack_forget()

def execute_code():
    """Execute code from the testing screen."""
    code = input_text.get("1.0", tk.END)
    output_box.config(state=tk.NORMAL)
    output_box.delete("1.0", tk.END)
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(code, globals())
        output = redirected_output.getvalue()
        output_box.insert(tk.END, output)
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}")
    finally:
        sys.stdout = old_stdout
    output_box.config(state=tk.DISABLED)

def optimize_ast(node):
    # Recursively optimize AST nodes (constant folding, etc.)
    if isinstance(node, BinaryOp):
        left = optimize_ast(node.left)
        right = optimize_ast(node.right)
        if isinstance(left, Number) and isinstance(right, Number):
            if node.op == '+': return Number(left.value + right.value)
            if node.op == '-': return Number(left.value - right.value)
            if node.op == '*': return Number(left.value * right.value)
            if node.op == '/': return Number(left.value / right.value)
        return BinaryOp(left, node.op, right)
    elif isinstance(node, UnaryOp):
        expr = optimize_ast(node.expr)
        if isinstance(expr, Number):
            if node.op == '-': return Number(-expr.value)
        return UnaryOp(node.op, expr)
    elif isinstance(node, Assign):
        return Assign(node.name, optimize_ast(node.expr))
    elif isinstance(node, Print):
        return Print(optimize_ast(node.expr))
    elif isinstance(node, IfElse):
        cond = optimize_ast(node.condition)
        if isinstance(cond, Boolean):
            if cond.value:
                return [optimize_ast(stmt) for stmt in node.if_body]
            elif node.else_body:
                return [optimize_ast(stmt) for stmt in node.else_body]
            else:
                return []
        return IfElse(cond, [optimize_ast(stmt) for stmt in node.if_body], [optimize_ast(stmt) for stmt in node.else_body] if node.else_body else None)
    elif isinstance(node, WhileLoop):
        return WhileLoop(optimize_ast(node.condition), [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, ForLoop):
        return ForLoop(node.var, optimize_ast(node.iterable), [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, FunctionDef):
        return FunctionDef(node.name, node.params, [optimize_ast(stmt) for stmt in node.body])
    elif isinstance(node, FunctionCall):
        return FunctionCall(node.name, [optimize_ast(arg) for arg in node.args])
    elif isinstance(node, ListNode):
        return ListNode([optimize_ast(elem) for elem in node.elements])
    elif isinstance(node, IndexNode):
        return IndexNode(optimize_ast(node.expr), optimize_ast(node.index))
    elif isinstance(node, StringMethod):
        return StringMethod(optimize_ast(node.expr), node.method, [optimize_ast(arg) for arg in node.args])
    elif isinstance(node, LenFunction):
        return LenFunction(optimize_ast(node.expr))
    elif isinstance(node, RangeCall):
        return RangeCall(optimize_ast(node.start) if node.start else None, optimize_ast(node.stop) if node.stop else None, optimize_ast(node.step) if node.step else None)
    else:
        return node

def ast_to_code(node):
    # Recursively convert AST back to code
    if isinstance(node, Assign):
        return f"{ast_to_code(node.name)} = {ast_to_code(node.expr)}"
    elif isinstance(node, BinaryOp):
        return f"({ast_to_code(node.left)} {node.op} {ast_to_code(node.right)})"
    elif isinstance(node, UnaryOp):
        return f"{node.op}{ast_to_code(node.expr)}"
    elif isinstance(node, Number):
        return str(node.value)
    elif isinstance(node, String):
        return repr(node.value)
    elif isinstance(node, Boolean):
        return str(node.value)
    elif isinstance(node, Identifier):
        return node.name
    elif isinstance(node, Print):
        return f"print({ast_to_code(node.expr)})"
    elif isinstance(node, IfElse):
        code = f"if {ast_to_code(node.condition)}:\n"
        for stmt in node.if_body:
            code += f"    {ast_to_code(stmt)}\n"
        if node.else_body:
            code += f"else:\n"
            for stmt in node.else_body:
                code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, WhileLoop):
        code = f"while {ast_to_code(node.condition)}:\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, ForLoop):
        code = f"for {ast_to_code(node.var)} in {ast_to_code(node.iterable)}:\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, FunctionDef):
        # Handle parameters properly - they might be Identifier objects or strings
        param_strs = []
        for param in node.params:
            if isinstance(param, Identifier):
                param_strs.append(param.name)
            else:
                param_strs.append(str(param))
        
        code = f"def {node.name}({', '.join(param_strs)}):\n"
        for stmt in node.body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    elif isinstance(node, FunctionCall):
        func_name = ast_to_code(node.name) if hasattr(node.name, 'name') else node.name
        return f"{func_name}({', '.join(ast_to_code(arg) for arg in node.args)})"
    elif isinstance(node, ListNode):
        return f"[{', '.join(ast_to_code(elem) for elem in node.elements)}]"
    elif isinstance(node, IndexNode):
        return f"{ast_to_code(node.expr)}[{ast_to_code(node.index)}]"
    elif isinstance(node, StringMethod):
        return f"{ast_to_code(node.expr)}.{node.method}({', '.join(ast_to_code(arg) for arg in node.args)})"
    elif isinstance(node, LenFunction):
        return f"len({ast_to_code(node.expr)})"
    elif isinstance(node, RangeCall):
        args = [ast_to_code(arg) for arg in [node.start, node.stop, node.step] if arg is not None]
        return f"range({', '.join(args)})"
    elif isinstance(node, Return):
        return f"return {ast_to_code(node.expr)}"
    elif isinstance(node, Break):
        return "break"
    elif isinstance(node, Continue):
        return "continue"
    elif isinstance(node, TryExcept):
        code = f"try:\n"
        for stmt in node.try_body:
            code += f"    {ast_to_code(stmt)}\n"
        code += f"except:\n"
        for stmt in node.except_body:
            code += f"    {ast_to_code(stmt)}\n"
        return code.rstrip()
    else:
        return ""

def optimize_code():
    raw_code = optimizer_input.get("1.0", tk.END).strip()
    optimizer_output.config(state=tk.NORMAL)
    optimizer_output.delete("1.0", tk.END)

    if not raw_code:
        optimizer_output.insert(tk.END, "⚠️ Please enter some Python code to optimize.")
        optimizer_output.config(state=tk.DISABLED)
        return

    try:
        ast = parser.parse(raw_code)
        if ast is None:
            raise Exception("Failed to parse code")
        # Optimize each statement in the AST
        optimized_ast = []
        for node in ast:
            opt = optimize_ast(node)
            if isinstance(opt, list):
                optimized_ast.extend(opt)
            else:
                optimized_ast.append(opt)
        # Convert optimized AST back to code
        optimized_code = "\n".join(ast_to_code(node) for node in optimized_ast if node)
        optimizer_output.insert(tk.END, optimized_code)
    except Exception as e:
        optimizer_output.insert(tk.END, f"❌ Error during optimization:\n{str(e)}")

    optimizer_output.config(state=tk.DISABLED)

def copy_to_clipboard():
    optimized_code = optimizer_output.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(optimized_code)
    root.update()

def download_optimized_code():
    optimized_code = optimizer_output.get("1.0", tk.END)
    if not optimized_code.strip():
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".py",
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
        title="Save Optimized Code"
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(optimized_code)

def on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def toggle_section(frame):
    if frame.winfo_viewable():
        frame.pack_forget()
    else:
        frame.pack(fill="x", padx=20, pady=(0, 10))

# --- Helper to ensure all phase functions handle both lists and single nodes ---
def ensure_list(ast):
    if isinstance(ast, list):
        return ast
    elif ast is None:
        return []
    else:
        return [ast]

# Define the original pretty_print_ast function first
def pretty_print_ast(node, indent="", is_last=True):
    # Define prefix based on whether it's the last child
    prefix = "└── " if is_last else "├── "
    
    if isinstance(node, list):
        result = []
        for i, n in enumerate(node):
            result.append(pretty_print_ast(n, indent, i == len(node) - 1))
        return "\n".join(result)
    elif hasattr(node, "__class__"):
        cname = node.__class__.__name__
        
        if cname == "Assign":
            return f"{indent}{prefix}Assignment\n{indent}    ├── Variable: {node.name}\n{indent}    └── Value: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "BinaryOp":
            return f"{indent}{prefix}Binary Operation: {node.op}\n{indent}    ├── Left: {pretty_print_ast(node.left, indent + '    ', False)}\n{indent}    └── Right: {pretty_print_ast(node.right, indent + '    ', True)}"
        elif cname == "UnaryOp":
            return f"{indent}{prefix}Unary Operation: {node.op}\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "Number":
            return f"{indent}{prefix}Number: {node.value}"
        elif cname == "String":
            return f"{indent}{prefix}String: '{node.value}'"
        elif cname == "Boolean":
            return f"{indent}{prefix}Boolean: {node.value}"
        elif cname == "Identifier":
            return f"{indent}{prefix}Identifier: {node.name}"
        elif cname == "Print":
            return f"{indent}{prefix}Print Statement\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "IfElse":
            result = [f"{indent}{prefix}If-Else Statement"]
            result.append(f"{indent}    ├── Condition: {pretty_print_ast(node.condition, indent + '    ', False)}")
            result.append(f"{indent}    ├── If Body:")
            for i, stmt in enumerate(node.if_body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.if_body) - 1 and not node.else_body))
            if node.else_body:
                result.append(f"{indent}    └── Else Body:")
                for i, stmt in enumerate(node.else_body):
                    result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.else_body) - 1))
            return "\n".join(result)
        elif cname == "WhileLoop":
            result = [f"{indent}{prefix}While Loop"]
            result.append(f"{indent}    ├── Condition: {pretty_print_ast(node.condition, indent + '    ', False)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "ForLoop":
            result = [f"{indent}{prefix}For Loop"]
            result.append(f"{indent}    ├── Variable: {node.var}")
            result.append(f"{indent}    ├── Iterable: {pretty_print_ast(node.iterable, indent + '    ', False)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "FunctionDef":
            result = [f"{indent}{prefix}Function Definition: {node.name}"]
            # Handle parameters properly - they might be Identifier objects or strings
            param_names = []
            for p in node.params:
                if isinstance(p, Identifier):
                    param_names.append(p.name)
                else:
                    param_names.append(str(p))
            result.append(f"{indent}    ├── Parameters: {', '.join(param_names)}")
            result.append(f"{indent}    └── Body:")
            for i, stmt in enumerate(node.body):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.body) - 1))
            return "\n".join(result)
        elif cname == "FunctionCall":
            result = [f"{indent}{prefix}Function Call: {node.name}"]
            result.append(f"{indent}    └── Arguments:")
            for i, arg in enumerate(node.args):
                result.append(pretty_print_ast(arg, indent + '        ', i == len(node.args) - 1))
            return "\n".join(result)
        elif cname == "ListNode":
            result = [f"{indent}{prefix}List"]
            for i, elem in enumerate(node.elements):
                result.append(pretty_print_ast(elem, indent + '    ', i == len(node.elements) - 1))
            return "\n".join(result)
        elif cname == "IndexNode":
            return f"{indent}{prefix}List Index\n{indent}    ├── List: {pretty_print_ast(node.list_expr, indent + '    ', False)}\n{indent}    └── Index: {pretty_print_ast(node.index_expr, indent + '    ', True)}"
        elif cname == "ListAssign":
            return f"{indent}{prefix}List Assignment\n{indent}    ├── List: {pretty_print_ast(node.list_expr, indent + '    ', False)}\n{indent}    ├── Index: {pretty_print_ast(node.index_expr, indent + '    ', False)}\n{indent}    └── Value: {pretty_print_ast(node.value, indent + '    ', True)}"
        elif cname == "Return":
            return f"{indent}{prefix}Return Statement\n{indent}    └── Value: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "Break":
            return f"{indent}{prefix}Break Statement"
        elif cname == "Continue":
            return f"{indent}{prefix}Continue Statement"
        elif cname == "TryExcept":
            result = [f"{indent}{prefix}Try-Except Block"]
            result.append(f"{indent}    ├── Try Block:")
            for i, stmt in enumerate(node.try_block):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.try_block) - 1))
            result.append(f"{indent}    └── Except Block:")
            for i, stmt in enumerate(node.except_block):
                result.append(pretty_print_ast(stmt, indent + '        ', i == len(node.except_block) - 1))
            return "\n".join(result)
        elif cname == "StringMethod":
            result = [f"{indent}{prefix}String Method: {node.method}"]
            result.append(f"{indent}    ├── String: {pretty_print_ast(node.string_obj, indent + '    ', False)}")
            if hasattr(node, 'args') and node.args:
                result.append(f"{indent}    └── Arguments:")
                for i, arg in enumerate(node.args):
                    result.append(pretty_print_ast(arg, indent + '        ', i == len(node.args) - 1))
            return "\n".join(result)
        elif cname == "LenFunction":
            return f"{indent}{prefix}Length Function\n{indent}    └── Expression: {pretty_print_ast(node.expr, indent + '    ', True)}"
        elif cname == "RangeCall":
            result = [f"{indent}{prefix}Range Function"]
            if node.start:
                result.append(f"{indent}    ├── Start: {pretty_print_ast(node.start, indent + '    ', False)}")
            if node.stop:
                result.append(f"{indent}    ├── Stop: {pretty_print_ast(node.stop, indent + '    ', False)}")
            if node.step:
                result.append(f"{indent}    └── Step: {pretty_print_ast(node.step, indent + '    ', True)}")
            return "\n".join(result)
        else:
            return f"{indent}{prefix}Unknown Node: {cname}"
    else:
        return f"{indent}{prefix}Unknown: {str(node)}"

# Now patch the functions after they're defined
old_pretty_print_ast = pretty_print_ast
def pretty_print_ast(node, indent="", is_last=True):
    node = ensure_list(node)
    if isinstance(node, list) and len(node) == 1:
        return old_pretty_print_ast(node[0], indent, is_last)
    elif isinstance(node, list):
        result = []
        for i, n in enumerate(node):
            result.append(old_pretty_print_ast(n, indent, i == len(node) - 1))
        return "\n".join(result)
    else:
        return old_pretty_print_ast(node, indent, is_last)

# Note: semantic_analysis and generate_icg are now imported from standalone modules



def update_phase_output(phase_name, content):
    text_widget = phase_sections[phase_name]["text"]
    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", content)
    text_widget.config(state=tk.DISABLED)

def optimize_code_icg(icg_code):
    if not icg_code or icg_code == "<no intermediate code generated>":
        return "⚠️ No intermediate code to optimize."
        
    lines = icg_code.split('\n')
    optimized_lines = []
    optimizations = []
    
    # Skip header and legend
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip() and not line.startswith('Legend:'):
            start_idx = i
            break
            
    # Process each line
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('Legend:'):
            break
            
        # Extract the actual code part (after line number)
        code = line.split('|', 1)[1].strip() if '|' in line else line
        
        # Constant Folding
        if '=' in code and any(op in code for op in ['+', '-', '*', '/']):
            try:
                # Try to evaluate constant expressions
                left, right = code.split('=', 1)
                left = left.strip()
                right = right.strip()
                
                # Check if right side is a constant expression
                if all(c.isdigit() or c in '+-*/() ' for c in right):
                    result = eval(right)
                    optimized_lines.append(f"{left} = {result}")
                    optimizations.append(f"Constant folding: {right} → {result}")
                    i += 1
                    continue
            except:
                pass
                
        # Copy Propagation
        if '=' in code and not any(op in code for op in ['+', '-', '*', '/']):
            left, right = code.split('=', 1)
            left = left.strip()
            right = right.strip()
            
            # Check if right side is just a variable
            if right.isidentifier():
                # Look ahead for uses of left
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                    if left in next_line and '=' not in next_line:
                        optimized_lines.append(f"# {code}  # Copy propagated")
                        optimizations.append(f"Copy propagation: {left} → {right}")
                        i += 1
                        break
                else:
                    optimized_lines.append(code)
                    i += 1
                    continue
                    
        # Common Subexpression Elimination
        if i > 0 and i < len(lines) - 1:
            prev_code = lines[i-1].split('|', 1)[1].strip() if '|' in lines[i-1] else lines[i-1]
            next_code = lines[i+1].split('|', 1)[1].strip() if '|' in lines[i+1] else lines[i+1]
            
            if '=' in code and '=' in prev_code and '=' in next_code:
                prev_left, prev_right = prev_code.split('=', 1)
                curr_left, curr_right = code.split('=', 1)
                next_left, next_right = next_code.split('=', 1)
                
                if prev_right.strip() == curr_right.strip():
                    optimized_lines.append(f"# {code}  # Common subexpression eliminated")
                    optimizations.append(f"Common subexpression elimination: {curr_right} → {prev_left}")
                    i += 1
                    continue
                    
        # Loop Optimization
        if 'goto' in code and 'L' in code:
            # Check if this is a loop
            if i > 0 and 'if' in lines[i-1]:
                # Try to move loop-invariant code outside
                loop_start = i
                while i < len(lines) and 'goto' not in lines[i]:
                    i += 1
                loop_end = i
                
                # Check for loop-invariant code
                for j in range(loop_start, loop_end):
                    loop_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                    if '=' in loop_line and not any(var in loop_line for var in ['i', 'j', 'k']):
                        optimized_lines.append(f"# {loop_line}  # Moved outside loop")
                        optimizations.append(f"Loop optimization: Moved invariant code outside loop")
                        continue
                    optimized_lines.append(loop_line)
                i += 1
                continue
                
        # Dead Code Elimination
        if '=' in code:
            left = code.split('=', 1)[0].strip()
            # Check if variable is used later
            used = False
            for j in range(i + 1, len(lines)):
                next_line = lines[j].split('|', 1)[1].strip() if '|' in lines[j] else lines[j]
                if left in next_line and '=' not in next_line:
                    used = True
                    break
            if not used:
                optimized_lines.append(f"# {code}  # Dead code eliminated")
                optimizations.append(f"Dead code elimination: {left} is never used")
                i += 1
                continue
                
        optimized_lines.append(code)
        i += 1
        
    # Format the output
    output = []
    output.append("Code Optimization Analysis:")
    output.append("==========================")
    output.append("")
    
    if optimizations:
        output.append("Applied Optimizations:")
        output.append("---------------------")
        for opt in optimizations:
            output.append(f"✓ {opt}")
        output.append("")
        
    output.append("Optimized Code:")
    output.append("--------------")
    for i, line in enumerate(optimized_lines, 1):
        output.append(f"{i:3d} | {line}")
        
    output.append("\nOptimization Summary:")
    output.append("-------------------")
    output.append(f"• Total optimizations applied: {len(optimizations)}")
    output.append("• Types of optimizations:")
    output.append("  - Constant folding")
    output.append("  - Copy propagation")
    output.append("  - Common subexpression elimination")
    output.append("  - Loop optimization")
    output.append("  - Dead code elimination")
    
    return "\n".join(output)

def generate_code(optimized_code):
    if not optimized_code or "No intermediate code" in optimized_code:
        return "⚠️ No code to generate."
        
    lines = optimized_code.split('\n')
    generated_code = []
    reg_counter = [0]
    label_counter = [0]
    
    def new_reg():
        reg_counter[0] += 1
        return f"R{reg_counter[0]}"
        
    def new_label():
        label_counter[0] += 1
        return f"L{label_counter[0]}"
        
    # Skip header and summary
    start_idx = 0
    for i, line in enumerate(lines):
        if "Optimized Code:" in line:
            start_idx = i + 2
            break
            
    # Process each line
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if not line or "Optimization Summary" in line:
            break
            
        # Extract the actual code part (after line number)
        code = line.split('|', 1)[1].strip() if '|' in line else line
        
        # Skip commented lines
        if code.startswith('#'):
            i += 1
            continue
            
        # Assignment
        if '=' in code:
            left, right = code.split('=', 1)
            left = left.strip()
            right = right.strip()
            
            # Constant assignment
            if right.isdigit():
                reg = new_reg()
                generated_code.append(f"MOV {reg}, #{right}    ; Load constant {right}")
                generated_code.append(f"STR {reg}, [{left}]   ; Store in {left}")
                
            # Variable assignment
            elif right.isidentifier():
                reg1 = new_reg()
                reg2 = new_reg()
                generated_code.append(f"LDR {reg1}, [{right}]  ; Load {right}")
                generated_code.append(f"STR {reg1}, [{left}]   ; Store in {left}")
                
            # Arithmetic operation
            elif any(op in right for op in ['+', '-', '*', '/']):
                op = next(op for op in ['+', '-', '*', '/'] if op in right)
                left_op, right_op = right.split(op)
                left_op = left_op.strip()
                right_op = right_op.strip()
                
                reg1 = new_reg()
                reg2 = new_reg()
                reg3 = new_reg()
                
                # Load operands
                if left_op.isdigit():
                    generated_code.append(f"MOV {reg1}, #{left_op}  ; Load constant {left_op}")
                else:
                    generated_code.append(f"LDR {reg1}, [{left_op}] ; Load {left_op}")
                    
                if right_op.isdigit():
                    generated_code.append(f"MOV {reg2}, #{right_op}  ; Load constant {right_op}")
                else:
                    generated_code.append(f"LDR {reg2}, [{right_op}] ; Load {right_op}")
                    
                # Perform operation
                if op == '+':
                    generated_code.append(f"ADD {reg3}, {reg1}, {reg2}  ; Add operands")
                elif op == '-':
                    generated_code.append(f"SUB {reg3}, {reg1}, {reg2}  ; Subtract operands")
                elif op == '*':
                    generated_code.append(f"MUL {reg3}, {reg1}, {reg2}  ; Multiply operands")
                elif op == '/':
                    generated_code.append(f"DIV {reg3}, {reg1}, {reg2}  ; Divide operands")
                    
                generated_code.append(f"STR {reg3}, [{left}]   ; Store result in {left}")
                
        # Print statement
        elif code.startswith('print'):
            reg = new_reg()
            var = code.split('print', 1)[1].strip()
            generated_code.append(f"LDR {reg}, [{var}]  ; Load value to print")
            generated_code.append(f"PUSH {reg}         ; Push to stack for printing")
            generated_code.append(f"CALL print         ; Call print function")
            generated_code.append(f"POP {reg}          ; Clean up stack")
            
        # If statement
        elif code.startswith('if'):
            cond = code.split('goto', 1)[0].split('if', 1)[1].strip()
            label = code.split('goto', 1)[1].strip()
            
            if '==' in cond:
                left, right = cond.split('==')
                reg1 = new_reg()
                reg2 = new_reg()
                generated_code.append(f"LDR {reg1}, [{left.strip()}]  ; Load left operand")
                if right.strip().isdigit():
                    generated_code.append(f"MOV {reg2}, #{right.strip()}  ; Load constant")
                else:
                    generated_code.append(f"LDR {reg2}, [{right.strip()}]  ; Load right operand")
                generated_code.append(f"CMP {reg1}, {reg2}  ; Compare operands")
                generated_code.append(f"BNE {label}      ; Branch if not equal")
                
        # Goto statement
        elif code.startswith('goto'):
            label = code.split('goto', 1)[1].strip()
            generated_code.append(f"B {label}          ; Unconditional branch")
            
        # Label
        elif code.endswith(':'):
            generated_code.append(f"{code}             ; Label")
            
        # Function call
        elif code.startswith('call'):
            func = code.split('call', 1)[1].split('(')[0].strip()
            args = code.split('(')[1].rstrip(')').split(',')
            for arg in args:
                reg = new_reg()
                generated_code.append(f"LDR {reg}, [{arg.strip()}]  ; Load argument")
                generated_code.append(f"PUSH {reg}         ; Push argument to stack")
            generated_code.append(f"CALL {func}         ; Call function")
            for _ in args:
                generated_code.append(f"POP {new_reg()}     ; Clean up stack")
                
        # Return statement
        elif code.startswith('return'):
            val = code.split('return', 1)[1].strip()
            reg = new_reg()
            generated_code.append(f"LDR {reg}, [{val}]  ; Load return value")
            generated_code.append(f"MOV R0, {reg}      ; Set return register")
            generated_code.append(f"RET                ; Return from function")
            
        i += 1
        
    # Format the output
    output = []
    output.append("Code Generation (Assembly-like):")
    output.append("===============================")
    output.append("")
    
    if generated_code:
        output.append("Generated Code:")
        output.append("--------------")
        for i, line in enumerate(generated_code, 1):
            output.append(f"{i:3d} | {line}")
            
        output.append("\nRegister Usage:")
        output.append("--------------")
        output.append(f"• Total registers used: {reg_counter[0]}")
        output.append("• Register naming: R1, R2, R3, ...")
        
        output.append("\nLabel Usage:")
        output.append("-----------")
        output.append(f"• Total labels used: {label_counter[0]}")
        output.append("• Label naming: L1, L2, L3, ...")
        
        output.append("\nInstruction Types:")
        output.append("-----------------")
        output.append("• MOV: Move immediate value to register")
        output.append("• LDR: Load from memory to register")
        output.append("• STR: Store from register to memory")
        output.append("• ADD/SUB/MUL/DIV: Arithmetic operations")
        output.append("• CMP: Compare operands")
        output.append("• B/BNE: Branch instructions")
        output.append("• PUSH/POP: Stack operations")
        output.append("• CALL/RET: Function calls")
    else:
        output.append("No code generated.")
        
    return "\n".join(output)

def analyze_phases():
    code = code_input.get("1.0", tk.END).strip()
    if not code:
        update_phase_output("Lexical Analysis", "⚠️ Please enter some code to analyze.")
        update_phase_output("Syntax & AST Analysis", "")
        update_phase_output("Semantic Analysis", "")
        update_phase_output("Intermediate Code Generation", "")
        update_phase_output("Code Optimization", "")
        update_phase_output("Code Generation", "")
        return

    try:
        # Lexical Analysis
        tokens = tokenize(code)
        if tokens:
            update_phase_output("Lexical Analysis", format_token_output(tokens))
        else:
            update_phase_output("Lexical Analysis", "No tokens found in the input code.")

        # Syntax & AST Analysis (use Python's built-in compile for robust syntax/indentation check)
        syntax_result = ""
        ast = None
        try:
            compile(code, "<string>", "exec")
            syntax_result = "✅ Syntax and indentation are correct!"
        except Exception as e:
            syntax_result = f"❌ Syntax/Indentation Error:\n==========================\n{e}"

        # Always try to parse AST, even if compile() fails
        try:
            ast = parser.parse(code)
            ast = ensure_list(ast)
            if not ast:
                raise Exception("No AST generated (possible syntax error).")
            ast_str = pretty_print_ast(ast)
            syntax_result += ("\n\nAbstract Syntax Tree (AST):\n" +
                             "===========================\n" +
                             ast_str + "\n\n" +
                             "The AST shows the hierarchical structure of your code, where:\n" +
                             "├── Each node represents a programming construct\n" +
                             "├── Child nodes show the components of each construct\n" +
                             "└── The tree structure helps verify correct syntax")
        except Exception as ast_e:
            syntax_result += f"\n\n❌ AST generation failed:\n========================\n{ast_e}"
            ast = None

        update_phase_output("Syntax & AST Analysis", syntax_result)

        # If AST generation failed, skip further phases
        if ast is None or not ast:
            update_phase_output("Semantic Analysis", "")
            update_phase_output("Intermediate Code Generation", "")
            update_phase_output("Code Optimization", "")
            update_phase_output("Code Generation", "")
            return

        # Semantic Analysis
        try:
            sem_ok, sem_msg = semantic_analysis(ast)
            if not sem_ok:
                update_phase_output("Semantic Analysis", 
                    "❌ Semantic Errors Found:\n" +
                    "======================\n" +
                    sem_msg + "\n\n" +
                    "💡 Tips to fix semantic errors:\n" +
                    "1. Check variable declarations and types\n" +
                    "2. Verify function definitions and calls\n" +
                    "3. Ensure proper type compatibility\n" +
                    "4. Look for undefined variables or functions")
            else:
                update_phase_output("Semantic Analysis", sem_msg)
            if not sem_ok:
                update_phase_output("Intermediate Code Generation", "❌ ICG skipped due to semantic error.")
                update_phase_output("Code Optimization", "❌ Optimization skipped due to semantic error.")
                update_phase_output("Code Generation", "❌ Code Generation skipped due to semantic error.")
                return
        except Exception as e:
            update_phase_output("Semantic Analysis", 
                "❌ Error in Semantic Analysis:\n" +
                "==========================\n" +
                str(e) + "\n\n" +
                "Please check your code for:\n" +
                "1. Proper variable declarations\n" +
                "2. Correct function definitions\n" +
                "3. Valid type usage")
            update_phase_output("Intermediate Code Generation", "❌ ICG skipped due to semantic error.")
            update_phase_output("Code Optimization", "❌ Optimization skipped due to semantic error.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to semantic error.")
            return

        # Intermediate Code Generation
        try:
            icg_code = generate_icg(ast)
            update_phase_output("Intermediate Code Generation", 
                "✅ Intermediate Code Generated:\n" +
                "===========================\n" +
                icg_code)
        except Exception as e:
            update_phase_output("Intermediate Code Generation", 
                "❌ Error in Intermediate Code Generation:\n" +
                "===================================\n" +
                str(e) + "\n\n" +
                "This error occurred while converting your code to intermediate representation.")
            update_phase_output("Code Optimization", "❌ Optimization skipped due to ICG error.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to ICG error.")
            return

        # Code Optimization
        try:
            optimized_code = optimize_code_icg(icg_code)
            update_phase_output("Code Optimization", 
                "✅ Code Optimization Results:\n" +
                "=========================\n" +
                optimized_code)
        except Exception as e:
            update_phase_output("Code Optimization", 
                "❌ Error in Code Optimization:\n" +
                "=========================\n" +
                str(e) + "\n\n" +
                "This error occurred while optimizing your code.")
            update_phase_output("Code Generation", "❌ Code Generation skipped due to optimization error.")
            return

        # Code Generation
        try:
            codegen = generate_code(optimized_code)
            update_phase_output("Code Generation", 
                "✅ Final Generated Code:\n" +
                "=====================\n" +
                codegen)
        except Exception as e:
            update_phase_output("Code Generation", 
                "❌ Error in Code Generation:\n" +
                "========================\n" +
                str(e) + "\n\n" +
                "This error occurred while generating the final code.")

    except Exception as e:
        update_phase_output("Lexical Analysis", 
            "❌ Error during analysis:\n" +
            "======================\n" +
            str(e) + "\n\n" +
            "Please check your input code for any obvious errors.")
        update_phase_output("Syntax & AST Analysis", "")
        update_phase_output("Semantic Analysis", "")
        update_phase_output("Intermediate Code Generation", "")
        update_phase_output("Code Optimization", "")
        update_phase_output("Code Generation", "")

# ---------- Styling ----------

root = tk.Tk()
root.title("Python Compiler")
root.geometry("1200x700")
root.config(bg="#0F1624")  # Dark background for the entire app

# Make all screens adapt to fullscreen
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Function to handle window resizing
def on_window_resize(event):
    if event.widget == root:
        # Update screens that need special handling
        try:
            adjust_team_layout()
            create_hacking_background()
            # Update compiler phases background if visible
            if compiler_phases_screen.winfo_viewable():
                create_compiler_background()
            # Update testing screen background if visible
            if testing_screen.winfo_viewable():
                create_testing_background()
        except:
            pass



style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Montserrat", 12, "bold"),
                padding=10,
                relief="flat",
                background="#2196F3",
                foreground="white")
style.map("TButton", background=[("active", "#1976D2")])

# Configure modern fonts
default_font = font.nametofont("TkDefaultFont")
default_font.configure(family="Montserrat", size=12)

# Modern color palette
colors = {
    "bg_dark": "#0F1624",     # Darker blue-black
    "bg_medium": "#1a202c",   # Dark blue-gray
    "bg_light": "#2d3748",    # Medium blue-gray
    "accent1": "#3182ce",     # Modern blue
    "accent2": "#38b2ac",     # Teal
    "accent3": "#90cdf4",     # Light blue
    "text_primary": "#f7fafc", # Almost white
    "text_secondary": "#e2e8f0", # Light gray
    "text_accent": "#90cdf4"   # Light blue
}

button_style = {
    "font": ("Montserrat", 13, "bold"),
    "bg": colors["accent1"],
    "fg": colors["text_primary"],
    "activebackground": "#1976D2",
    "cursor": "hand2",
    "padx": 20,
    "pady": 10,
    "relief": "flat",
    "bd": 0
}

# --- Add these functions for hover effect ---
def on_enter(e):
    e.widget.config(bg="#1565C0", fg="#FFD700")

def on_leave(e):
    e.widget.config(bg="#1976D2", fg="white")

    
# ---------- Welcome Screen (Modern) ----------
welcome_screen = tk.Frame(root)
welcome_screen.pack(fill=tk.BOTH, expand=True)

# Create a background frame with modern dark theme
bg_frame = tk.Frame(welcome_screen, bg="#0F1624")
bg_frame.place(x=0, y=0, relwidth=1, relheight=1)  # Cover the entire welcome screen

# Create a canvas for the background image
bg_canvas = tk.Canvas(bg_frame, highlightthickness=0, bd=0, bg="#0F1624")
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Create modern background with code elements
def create_hacking_background():
    width = root.winfo_width()
    height = root.winfo_height()
    bg_canvas.delete("all")
    
    # Create gradient overlay
    for i in range(20):
        y = height * (i/20)
        color = f"#{10+i:02x}{15+i:02x}{30+i:02x}"
        bg_canvas.create_line(0, y, width, y, fill=color, width=height/20)
    
    # Draw subtle code elements
    for i in range(30):
        x = width * (i/30)
        y = height * 0.8 * (i % 5)/5
        code_element = ["def", "class", "import", "for", "if", "return", "while"][i % 7]
        bg_canvas.create_text(x, y, text=code_element, fill="#2d3748", font=("Consolas", 14))
        
    # Draw modern circuit pattern
    for i in range(10):
        x1 = width * (i/10)
        y1 = height * 0.2
        x2 = width * ((i+3)/10)
        y2 = height * 0.8
        bg_canvas.create_line(x1, y1, x2, y2, fill="#2d3748", width=1, dash=(8, 4))

def update_welcome_screen(event=None):
    if welcome_screen.winfo_viewable():
        create_hacking_background()
        
# Initial call to create the background
root.after(100, create_hacking_background)



# Function to update the welcome screen when window is resized
def on_window_resize(event):
    if event.widget == root:
        # Update screens that need special handling
        try:
            create_hacking_background()
            # Ensure content frame stays centered
            if welcome_screen.winfo_viewable():
                content_frame.place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass



# Content frame in the center with glass morphism effect
content_frame = tk.Frame(welcome_screen, bg="#1a202c", bd=0, highlightthickness=0)
content_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center vertically and horizontally

# Add rounded corners and shadow effect (simulated with border)
content_inner = tk.Frame(content_frame, bg="#1a202c", bd=2, relief="solid", highlightbackground="#2d3748", highlightthickness=1)
content_inner.pack(padx=20, pady=20)

# Subheader with icon
subheader_label = tk.Label(
    content_inner,
    text="🚀 Python Compiler & Interpreter",
    font=("Montserrat", 24, "bold"),
    bg="#1a202c",
    fg="#e2e8f0"
)
subheader_label.pack(pady=(20, 20))


# Project Team section
team_frame = tk.Frame(content_inner, bg="#1a202c", bd=0)
team_frame.pack(pady=(0, 20))

team_title = tk.Label(
    team_frame,
    text="Project Team",
    font=("Montserrat", 16, "bold"),
    bg="#1a202c",
    fg="#90cdf4"  # Light blue
)
team_title.pack(pady=(10, 15))

# Team members grid
team_members = ["Karan Nayal", "Diya Tiwari", "Amaan Ahmad", "Manish Bhatt"]
team_grid = tk.Frame(team_frame, bg="#1a202c")
team_grid.pack(pady=10)

# Create a grid layout for team members
for i, name in enumerate(team_members):
    row, col = i // 2, i % 2
    member_frame = tk.Frame(team_grid, bg="#2d3748", padx=20, pady=12,
                           highlightthickness=2, highlightbackground="#4a5568")
    member_frame.grid(row=row, column=col, padx=15, pady=8)
    
    member_label = tk.Label(
        member_frame,
        text=name,
        font=("Montserrat", 15, "bold"),
        bg="#2d3748",
        fg="#63b3ed",
        width=14
    )
    member_label.pack()
    
    # Add subtle glow effect on hover
    def on_enter(e, frame=member_frame, label=member_label):
        frame.config(highlightbackground="#90cdf4")
        label.config(fg="#ffffff")
        
    def on_leave(e, frame=member_frame, label=member_label):
        frame.config(highlightbackground="#4a5568")
        label.config(fg="#63b3ed")
        
    member_frame.bind("<Enter>", on_enter)
    member_frame.bind("<Leave>", on_leave)

# Function to adjust team layout based on window width
def adjust_team_layout(event=None):
    # No dynamic adjustments needed for the grid layout
    pass



# Bind window resize event to handle all responsive elements
root.bind("<Configure>", on_window_resize)

# Navigation Buttons with modern styling
nav_buttons = tk.Frame(content_inner, bg="#1a202c")
nav_buttons.pack(pady=20)

button_configs = [
    {"text": "🧪 Test Your Code", "command": go_to_testing, "bg": "#3182ce", "hover_bg": "#4299e1"},
    {"text": "🔍 Compiler Phases", "command": go_to_compiler_phases, "bg": "#3182ce", "hover_bg": "#4299e1"},
]

for i, config in enumerate(button_configs):
    # Create button container for shadow effect
    btn_container = tk.Frame(nav_buttons, bg="#2d3748", bd=0)
    btn_container.grid(row=0, column=i, padx=15)
    
    btn = tk.Button(
        btn_container, 
        text=config["text"], 
        command=config["command"], 
        font=("Montserrat", 14, "bold"),
        bg=config["bg"], 
        fg="white",
        activebackground=config["hover_bg"],
        activeforeground="white",
        cursor="hand2",
        padx=30, 
        pady=15, 
        relief="flat",
        bd=0
    )
    btn.pack()
    
    # Custom hover effect with glow
    btn.bind("<Enter>", lambda e, b=btn, c=config: b.config(bg=c["hover_bg"], fg="#ffffff"))
    btn.bind("<Leave>", lambda e, b=btn, c=config: b.config(bg=c["bg"], fg="white"))

# ---------- Learn Python Screen ----------

learn_screen = tk.Frame(root, bg=colors["bg_dark"])

# Header with modern styling
header_container = tk.Frame(learn_screen, bg=colors["bg_medium"], pady=10)
header_container.pack(fill="x", pady=(0, 20))

tk.Label(
    header_container, 
    text="Python Learning Hub", 
    font=("Montserrat", 22, "bold"), 
    bg=colors["bg_medium"], 
    fg=colors["accent3"]
).pack(pady=(10, 5))

tk.Label(
    header_container, 
    text="Master Python programming concepts with interactive examples", 
    font=("Montserrat", 12), 
    bg=colors["bg_medium"], 
    fg=colors["text_secondary"]
).pack(pady=(0, 10))

scroll_frame = tk.Frame(learn_screen, bg=colors["bg_dark"])
scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

canvas = tk.Canvas(scroll_frame, bg=colors["bg_dark"], highlightthickness=0)
scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
scrollable_content = tk.Frame(canvas, bg=colors["bg_dark"])

canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
canvas.bind_all("<MouseWheel>", on_mousewheel)

sections = {
    "🔤 Variables & Data Types": "Python supports various data types like int, float, string, and boolean.",
    "🔁 Loops": "Use 'for' or 'while' loops to iterate over sequences or repeat actions.",
    "📦 Functions": "Functions help you reuse code. Define using 'def'.",
    "📄 File Handling": "Python can open, read, and write files using the 'open' function.",
    "🧪 Exception Handling": "Use try-except blocks to manage errors gracefully."
}

for title, desc in sections.items():
    container = tk.Frame(scrollable_content, bg=colors["bg_medium"], bd=1, relief="solid")
    
    title_label = tk.Label(
        container, 
        text=title, 
        font=("Montserrat", 14, "bold"),
        bg=colors["bg_light"], 
        fg=colors["accent3"], 
        cursor="hand2", 
        anchor="w", 
        padx=15,
        pady=10
    )
    title_label.pack(fill="x")

    content = tk.Label(
        container, 
        text=desc, 
        font=("Montserrat", 12),
        wraplength=1000, 
        justify="left", 
        bg=colors["bg_medium"], 
        fg=colors["text_primary"],
        anchor="w", 
        padx=15,
        pady=10
    )
    content.pack_forget()

    title_label.bind("<Button-1>", lambda e, frame=content: toggle_section(frame))
    container.pack(fill="x", padx=20, pady=10)

back_button = tk.Button(
    learn_screen, 
    text="🔙 Back", 
    font=("Montserrat", 13, "bold"),
    bg=colors["accent2"],
    fg="white",
    command=back_to_welcome,
    cursor="hand2",
    padx=25,
    pady=12,
    relief="flat",
    bd=0
)
back_button.pack(pady=20)

# Add hover effect
back_button.bind("<Enter>", lambda e: back_button.config(bg="#0097A7"))
back_button.bind("<Leave>", lambda e: back_button.config(bg=colors["accent2"]))

# ---------- Testing Screen (Interpreter) ----------
testing_screen = tk.Frame(root, bg=colors["bg_dark"])

# Create a canvas for the background
testing_bg_canvas = tk.Canvas(testing_screen, highlightthickness=0, bd=0, bg=colors["bg_dark"])
testing_bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Function to create enhanced background for testing screen
def create_testing_background():
    width = testing_screen.winfo_width()
    height = testing_screen.winfo_height()
    testing_bg_canvas.delete("all")
    
    # Create gradient background
    for i in range(20):
        y = height * (i/20)
        color = f"#{5+i:02x}{15+i:02x}{20+i:02x}"
        testing_bg_canvas.create_line(0, y, width, y, fill=color, width=height/20)
    
    # Add code patterns
    keywords = ["def", "class", "if", "else", "for", "while", "return", "import", "try", "except"]
    for i in range(25):
        x = width * (i/25)
        y = height * (0.05 + (i % 10) * 0.08)
        keyword = keywords[i % len(keywords)]
        testing_bg_canvas.create_text(x, y, text=keyword, fill="#1a3b5c", font=("Consolas", 14))
    
    # Add decorative elements
    for i in range(8):
        x1 = width * (i/8)
        y1 = height * 0.05
        x2 = width * ((i+1)/8)
        y2 = height * 0.95
        testing_bg_canvas.create_line(x1, y1, x2, y2, fill="#1a3b5c", width=1, dash=(8, 6))

# Header with modern styling
header_container = tk.Frame(testing_screen, bg=colors["bg_medium"], pady=10)
header_container.pack(fill="x", pady=(0, 20))

tk.Label(
    header_container, 
    text="Code Playground", 
    font=("Montserrat", 22, "bold"), 
    bg=colors["bg_medium"], 
    fg=colors["accent3"]
).pack(pady=(10, 5))

tk.Label(
    header_container, 
    text="Write, test, and execute Python code in real-time", 
    font=("Montserrat", 12), 
    bg=colors["bg_medium"], 
    fg=colors["text_secondary"]
).pack(pady=(0, 10))

# Code editor and output side by side
editor_output_pane = tk.PanedWindow(testing_screen, orient=tk.HORIZONTAL, sashwidth=5, bg=colors["bg_dark"])
editor_output_pane.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

# Code editor
editor_frame = tk.LabelFrame(
    editor_output_pane, 
    text="📝 Editor",
    font=("Montserrat", 14, "bold"),
    bg="#1a365d",
    fg="#e2e8f0",
    bd=2,
    relief="raised",
    highlightthickness=2,
    highlightbackground="#4a5568"
)
editor_output_pane.add(editor_frame, stretch="always")

# Editor with line numbers and syntax highlighting
input_text = tk.Text(
    editor_frame, 
    height=20, 
    font=("Fira Mono", 13), 
    wrap="none", 
    bg="#1a202c", 
    fg="#e2e8f0", 
    insertbackground="#63b3ed", 
    selectbackground="#4299e1",
    selectforeground="white",
    undo=True,
    padx=12,
    pady=12
)
input_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Output console
output_frame = tk.LabelFrame(
    editor_output_pane, 
    text="🖥️ Console Output",
    font=("Montserrat", 14, "bold"),
    bg="#2c5282",
    fg="#e2e8f0",
    bd=2,
    relief="raised",
    highlightthickness=2,
    highlightbackground="#4a5568"
)
editor_output_pane.add(output_frame, stretch="always")

output_box = tk.Text(
    output_frame, 
    height=20, 
    font=("Fira Mono", 13), 
    wrap="none", 
    state=tk.DISABLED, 
    bg="#1a202c", 
    fg="#e2e8f0", 
    insertbackground="#63b3ed",
    selectbackground="#4299e1",
    selectforeground="white",
    padx=12,
    pady=12
)
output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Run and Back buttons
button_frame = tk.Frame(testing_screen, bg=colors["bg_dark"])
button_frame.pack(pady=20)

# Create button container for shadow effect
run_btn_container = tk.Frame(button_frame, bg="#2d3748", bd=0, highlightthickness=2, highlightbackground="#4a5568")
run_btn_container.grid(row=0, column=0, padx=15)

run_button = tk.Button(
    run_btn_container, 
    text="▶ Run Code", 
    font=("Montserrat", 14, "bold"), 
    bg="#3182ce", 
    fg="white", 
    activebackground="#1565C0", 
    command=execute_code, 
    cursor="hand2", 
    padx=30, 
    pady=15, 
    relief="flat",
    bd=0
)
run_button.pack()

# Create button container for shadow effect
back_btn_container = tk.Frame(button_frame, bg="#2d3748", bd=0, highlightthickness=2, highlightbackground="#4a5568")
back_btn_container.grid(row=0, column=1, padx=15)

back_button = tk.Button(
    back_btn_container, 
    text="🔙 Back", 
    font=("Montserrat", 14, "bold"), 
    bg="#38b2ac", 
    fg="white", 
    activebackground="#0097A7", 
    command=back_to_welcome, 
    cursor="hand2", 
    padx=30, 
    pady=15, 
    relief="flat",
    bd=0
)
back_button.pack()

# Add enhanced hover effects
def on_run_enter(e):
    run_button.config(bg="#1565C0", fg="#FFD700")
    run_btn_container.config(highlightbackground="#90cdf4")
    
def on_run_leave(e):
    run_button.config(bg="#3182ce", fg="white")
    run_btn_container.config(highlightbackground="#4a5568")
    
def on_back_enter(e):
    back_button.config(bg="#0097A7", fg="#FFD700")
    back_btn_container.config(highlightbackground="#90cdf4")
    
def on_back_leave(e):
    back_button.config(bg="#38b2ac", fg="white")
    back_btn_container.config(highlightbackground="#4a5568")

run_button.bind("<Enter>", on_run_enter)
run_button.bind("<Leave>", on_run_leave)
back_button.bind("<Enter>", on_back_enter)
back_button.bind("<Leave>", on_back_leave)

# ---------- Optimizer Screen ----------

optimizer_screen = tk.Frame(root, bg=colors["bg_dark"])

# Header with modern styling
header_container = tk.Frame(optimizer_screen, bg=colors["bg_medium"], pady=10)
header_container.pack(fill="x", pady=(0, 20))

tk.Label(
    header_container, 
    text="Code Optimizer", 
    font=("Montserrat", 22, "bold"), 
    bg=colors["bg_medium"], 
    fg=colors["accent3"]
).pack(pady=(10, 5))

tk.Label(
    header_container, 
    text="Optimize your Python code for better performance", 
    font=("Montserrat", 12), 
    bg=colors["bg_medium"], 
    fg=colors["text_secondary"]
).pack(pady=(0, 10))

# Create a PanedWindow for side-by-side layout
optimizer_pane = tk.PanedWindow(optimizer_screen, orient=tk.HORIZONTAL, bg=colors["bg_dark"])
optimizer_pane.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Left panel for input code
left_frame = tk.LabelFrame(
    optimizer_pane, 
    text="📝 Original Code",
    font=("Montserrat", 14, "bold"),
    bg=colors["bg_medium"],
    fg=colors["accent1"],
    bd=1,
    relief="solid"
)
optimizer_pane.add(left_frame, stretch="always")

optimizer_input = tk.Text(
    left_frame, 
    height=20, 
    font=("Fira Mono", 12), 
    wrap="word",
    bg=colors["bg_light"], 
    fg=colors["text_primary"], 
    insertbackground=colors["accent1"],
    padx=10,
    pady=10
)
optimizer_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Right panel for optimized code
right_frame = tk.LabelFrame(
    optimizer_pane, 
    text="✨ Optimized Code",
    font=("Montserrat", 14, "bold"),
    bg=colors["bg_medium"],
    fg=colors["accent2"],
    bd=1,
    relief="solid"
)
optimizer_pane.add(right_frame, stretch="always")

optimizer_output = tk.Text(
    right_frame, 
    height=20, 
    font=("Fira Mono", 12), 
    wrap="word",
    state=tk.DISABLED, 
    bg=colors["bg_light"], 
    fg=colors["text_primary"], 
    padx=10,
    pady=10
)
optimizer_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Button frame at the bottom
button_frame = tk.Frame(optimizer_screen, bg=colors["bg_dark"])
button_frame.pack(pady=20)

optimize_button = tk.Button(
    button_frame, 
    text="🚀 Optimize Code", 
    font=("Montserrat", 13, "bold"),
    bg=colors["accent1"],
    fg="white",
    command=optimize_code,
    cursor="hand2",
    padx=25,
    pady=12,
    relief="flat",
    bd=0
)
optimize_button.grid(row=0, column=0, padx=15)

back_button = tk.Button(
    button_frame, 
    text="🔙 Back", 
    font=("Montserrat", 13, "bold"),
    bg=colors["accent2"],
    fg="white",
    command=back_to_welcome,
    cursor="hand2",
    padx=25,
    pady=12,
    relief="flat",
    bd=0
)
back_button.grid(row=0, column=1, padx=15)

# Add hover effects
optimize_button.bind("<Enter>", lambda e: optimize_button.config(bg="#1565C0"))
optimize_button.bind("<Leave>", lambda e: optimize_button.config(bg=colors["accent1"]))
back_button.bind("<Enter>", lambda e: back_button.config(bg="#0097A7"))
back_button.bind("<Leave>", lambda e: back_button.config(bg=colors["accent2"]))

# ---------- Compiler Phases Screen ----------

compiler_phases_screen = tk.Frame(root, bg=colors["bg_dark"])

# Make the window resizable
# Allow the screen to resize with the window
compiler_phases_screen.pack_propagate(True)

# Create a canvas for the background
compiler_bg_canvas = tk.Canvas(compiler_phases_screen, highlightthickness=0, bd=0, bg=colors["bg_dark"])
compiler_bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Function to create enhanced background for compiler phases screen
def create_compiler_background():
    width = compiler_phases_screen.winfo_width()
    height = compiler_phases_screen.winfo_height()
    compiler_bg_canvas.delete("all")
    
    # Create gradient background
    for i in range(20):
        y = height * (i/20)
        color = f"#{5+i:02x}{10+i:02x}{25+i:02x}"
        compiler_bg_canvas.create_line(0, y, width, y, fill=color, width=height/20)
    
    # Add circuit-like patterns
    for i in range(15):
        x1 = width * (i/15)
        y1 = height * 0.1
        x2 = width * ((i+2)/15)
        y2 = height * 0.9
        compiler_bg_canvas.create_line(x1, y1, x2, y2, fill="#1a3b5c", width=2, dash=(10, 6))
    
    # Add code symbols
    symbols = ["{ }", "( )", "[ ]", "< >", "// ", "/* */", "=>", "->", "==", "!="]
    for i in range(20):
        x = width * (i/20)
        y = height * (0.1 + (i % 5) * 0.15)
        symbol = symbols[i % len(symbols)]
        compiler_bg_canvas.create_text(x, y, text=symbol, fill="#1a3b5c", font=("Consolas", 16))

# Header with modern styling
header_container = tk.Frame(compiler_phases_screen, bg=colors["bg_medium"], pady=10)
header_container.pack(fill="x", pady=(0, 20))

tk.Label(
    header_container, 
    text="Compiler Pipeline Visualizer", 
    font=("Montserrat", 22, "bold"), 
    bg=colors["bg_medium"], 
    fg=colors["accent3"]
).pack(pady=(10, 5))

tk.Label(
    header_container, 
    text="Explore each phase of the compilation process", 
    font=("Montserrat", 12), 
    bg=colors["bg_medium"], 
    fg=colors["text_secondary"]
).pack(pady=(0, 10))

# Use a PanedWindow to split left (input) and right (analysis)
phases_pane = tk.PanedWindow(compiler_phases_screen, orient=tk.HORIZONTAL, sashwidth=5, bg=colors["bg_dark"])
phases_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left: Code Input with its own scrollbar
input_frame = tk.LabelFrame(
    phases_pane,
    text="📝 Source Code",
    font=("Montserrat", 14, "bold"),
    bg=colors["bg_medium"],
    fg=colors["accent1"],
    bd=1,
    relief="solid"
)
input_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

input_scroll = tk.Scrollbar(input_frame, orient="vertical", width=16)
code_input = tk.Text(
    input_frame,
    height=20,
    font=("Fira Mono", 12),
    bg=colors["bg_light"],
    fg=colors["text_primary"],
    insertbackground=colors["accent1"],
    wrap=tk.NONE,
    yscrollcommand=input_scroll.set,
    padx=10,
    pady=10
)
input_scroll.config(command=code_input.yview)
input_scroll.pack(side="right", fill="y")
code_input.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)

phases_pane.add(input_frame, stretch="always")

# Right: Scrollable Analysis Area
right_frame = tk.Frame(phases_pane, bg=colors["bg_dark"])
phases_pane.add(right_frame, stretch="always")

# Add a canvas and scrollbar for the analysis area
analysis_canvas = tk.Canvas(right_frame, bg=colors["bg_dark"], highlightthickness=0)
analysis_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=analysis_canvas.yview, width=16)
analysis_canvas.configure(yscrollcommand=analysis_scrollbar.set)
analysis_scrollbar.pack(side="right", fill="y")
analysis_canvas.pack(side="left", fill="both", expand=True)

# Create a frame inside the canvas for analysis boxes
analysis_inner = tk.Frame(analysis_canvas, bg=colors["bg_dark"])
analysis_canvas.create_window((0, 0), window=analysis_inner, anchor="nw")

# Update scrollregion when content changes
analysis_inner.bind(
    "<Configure>", lambda e: analysis_canvas.configure(scrollregion=analysis_canvas.bbox("all")))

# Phase icons
phase_icons = {
    "Lexical Analysis": "🔤",
    "Syntax & AST Analysis": "🌳",
    "Semantic Analysis": "🧩",
    "Intermediate Code Generation": "⚙️",
    "Code Optimization": "🚀",
    "Code Generation": "💻"
}

# Analysis boxes with their own scrollbars
analysis_boxes = {}
phase_colors = {
    "Lexical Analysis": "#1a365d",
    "Syntax & AST Analysis": "#2a4365",
    "Semantic Analysis": "#2c5282",
    "Intermediate Code Generation": "#2b6cb0",
    "Code Optimization": "#3182ce",
    "Code Generation": "#4299e1"
}

for phase_name in [
    "Lexical Analysis",
    "Syntax & AST Analysis",
    "Semantic Analysis",
    "Intermediate Code Generation",
    "Code Optimization",
    "Code Generation"
]:
    # Create a frame with gradient background
    frame = tk.LabelFrame(
        analysis_inner,
        text=f"{phase_icons[phase_name]} {phase_name}",
        font=("Montserrat", 13, "bold"),
        bg=phase_colors[phase_name],
        fg="#e2e8f0",
        bd=2,
        relief="raised",
        highlightthickness=2,
        highlightbackground="#4a5568"
    )
    frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Add a vertical scrollbar to each analysis box
    box_scroll = tk.Scrollbar(frame, orient="vertical", width=16)
    
    # Create a container frame for the text widget and horizontal scrollbar
    text_container = tk.Frame(frame, bg="#1a202c")
    text_container.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    
    text_widget = tk.Text(
        text_container,
        height=15,  # Increased height from 10 to 15
        font=("Courier New", 11),  # Using a monospace font for better alignment
        bg="#1a202c",
        fg="#e2e8f0",
        wrap=tk.NONE,  # Changed to NONE to prevent wrapping and maintain column alignment
        yscrollcommand=box_scroll.set,
        padx=8,
        pady=8,
        insertbackground="#63b3ed",
        selectbackground="#4299e1",
        selectforeground="white"
    )
    
    # Add horizontal scrollbar at the bottom of each phase
    h_scroll = tk.Scrollbar(text_container, orient="horizontal", width=16)
    h_scroll.config(command=text_widget.xview)
    h_scroll.pack(side="bottom", fill="x")
    
    box_scroll.config(command=text_widget.yview)
    box_scroll.pack(side="right", fill="y")
    text_widget.pack(side="top", fill="both", expand=True)
    text_widget.config(state=tk.DISABLED, xscrollcommand=h_scroll.set)

    analysis_boxes[phase_name] = text_widget

# Update phase_sections to use the new analysis_boxes
phase_sections = {k: {"text": v} for k, v in analysis_boxes.items()}

# Add analyze and back buttons below the pane, always visible
button_frame = tk.Frame(compiler_phases_screen, bg=colors["bg_dark"])
button_frame.pack(fill=tk.X, pady=20)

analyze_button = tk.Button(
    button_frame,
    text="🔍 Analyze Code",
    font=("Montserrat", 13, "bold"),
    bg=colors["accent1"],
    fg="white",
    command=lambda: analyze_phases(),
    cursor="hand2",
    padx=25,
    pady=12,
    relief="flat",
    bd=0
)
analyze_button.pack(side="left", padx=20)

back_button = tk.Button(
    button_frame,
    text="🔙 Back",
    font=("Montserrat", 13, "bold"),
    bg=colors["accent2"],
    fg="white",
    command=back_to_welcome,
    cursor="hand2",
    padx=25,
    pady=12,
    relief="flat",
    bd=0
)
back_button.pack(side="right", padx=20)

# Add hover effects
analyze_button.bind("<Enter>", lambda e: analyze_button.config(bg="#1565C0"))
analyze_button.bind("<Leave>", lambda e: analyze_button.config(bg=colors["accent1"]))
back_button.bind("<Enter>", lambda e: back_button.config(bg="#0097A7"))
back_button.bind("<Leave>", lambda e: back_button.config(bg=colors["accent2"]))

root.mainloop()
