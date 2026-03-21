import sys
sys.path.append(r"k:\PROJECTS\Mini-Python-Interpreter\Mini-Python-Interpreter-Python-PLY-Maven")
from src.myparser import parser

code = """
def greet(name):
    print("Hello", name)

greet("User")
"""
ast = parser.parse(code)
for stmt in ast:
    print(type(stmt).__name__)
    if type(stmt).__name__ == 'FunctionDef':
        print("Function body length:", len(stmt.body))
