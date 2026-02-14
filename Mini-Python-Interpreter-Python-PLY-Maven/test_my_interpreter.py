from interpreter import Interpreter

code = """
x = 10
y = 5
print("x + y =", x + y)

def add(a, b):
    return a + b

result = add(x, y)
print("Function result:", result)

numbers = [1, 2, 3]
print("List element:", numbers[0])
"""

try:
    interp = Interpreter()
    print("--- Starting Interpretation ---")
    interp.execute(code)
    print("--- Finished Interpretation ---")
except Exception as e:
    print(f"Error: {e}")
