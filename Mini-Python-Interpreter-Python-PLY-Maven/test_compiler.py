import tokenize
from io import StringIO
import ast
import sys
import io

def lexical_analysis(code):
    try:
        tokens = list(tokenize.generate_tokens(StringIO(code).readline))
        return "\n".join([f"{tokenize.tok_name[tok.type]}: {repr(tok.string)}" for tok in tokens])
    except Exception as e:
        return f"Error: {e}"

def syntax_analysis(code):
    try:
        tree = ast.parse(code)
        return ast.dump(tree, indent=4)
    except Exception as e:
        return f"Error: {e}"

def semantic_analysis(code):
    try:
        tree = ast.parse(code)
        # For demo: just return "No semantic errors found."
        return "No semantic errors found (basic check)."
    except Exception as e:
        return f"Error: {e}"

def intermediate_code(code):
    try:
        tree = ast.parse(code)
        lines = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                lines.append(f"STORE {ast.unparse(node.targets[0])} <- {ast.unparse(node.value)}")
            elif isinstance(node, ast.BinOp):
                lines.append(f"BINOP {ast.unparse(node)}")
            elif isinstance(node, ast.Call):
                lines.append(f"CALL {ast.unparse(node)}")
        return "\n".join(lines) if lines else "No intermediate code generated."
    except Exception as e:
        return f"Error: {e}"

def optimization(code):
    try:
        # For demo, just return the code (no real optimization)
        return code
    except Exception as e:
        return f"Error: {e}"

def code_generation(code):
    try:
        # For demo, just return the code (no real code generation)
        return code
    except Exception as e:
        return f"Error: {e}"

def execution_output(code):
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        exec(code, {})
        output = mystdout.getvalue()
    except Exception as e:
        output = f"Error: {e}"
    finally:
        sys.stdout = old_stdout
    return output

def analyze_python_code(code):
    return {
        "lexical": lexical_analysis(code),
        "syntax": syntax_analysis(code),
        "semantic": semantic_analysis(code),
        "intermediate": intermediate_code(code),
        "optimization": optimization(code),
        "codegen": code_generation(code),
        "execution": execution_output(code)
    }

# Example usage for backend/UI integration:
if __name__ == "__main__":
    print("Enter Python code (end with Ctrl+D on Linux/Mac or Ctrl+Z on Windows):")
    code = sys.stdin.read()
    results = analyze_python_code(code)
    print("\n--- Lexical Analysis ---\n", results["lexical"])
    print("\n--- Syntax Analysis ---\n", results["syntax"])
    print("\n--- Semantic Analysis ---\n", results["semantic"])
    print("\n--- Intermediate Code ---\n", results["intermediate"])
    print("\n--- Optimization ---\n", results["optimization"])
    print("\n--- Code Generation ---\n", results["codegen"])
    print("\n--- Execution Output ---\n", results["execution"]) 