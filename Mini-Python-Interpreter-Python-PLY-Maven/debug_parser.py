from myparser import parser
import os

try:
    if os.path.exists('parsetab.py'):
        os.remove('parsetab.py')
    if os.path.exists('parser.out'):
        os.remove('parser.out')
except:
    pass


# Read example.py content
with open('example.py', 'r') as f:
    code = f.read()
print(f"Parsing code: {code!r}")
try:
    ast = parser.parse(code)
    print("AST Type:", type(ast))
    print("AST Content (Recursive):")
    def print_recursive(node, indent=0):
        prefix = "  " * indent
        if isinstance(node, list):
            print(f"{prefix}[")
            for item in node:
                print_recursive(item, indent + 1)
            print(f"{prefix}]")
        elif hasattr(node, "__dict__"):
            print(f"{prefix}{type(node).__name__}:")
            for k, v in node.__dict__.items():
                print(f"{prefix}  {k}:", end=" ")
                if isinstance(v, (list, object)) and not isinstance(v, (str, int, float, bool)):
                    print()
                    print_recursive(v, indent + 2)
                else:
                    print(v)
        else:
            print(f"{prefix}{node!r} (Type: {type(node)})")

    print_recursive(ast)
except Exception as e:
    print(f"Parser failed: {e}")
