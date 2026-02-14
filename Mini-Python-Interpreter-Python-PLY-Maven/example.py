# Mini-Python-Interpreter Example Code

# 1. Variables and Basic Types
print("--- 1. Variables ---")
x = 10
y = 20
z = x + y
print(z)

name = "Mini-Python"
is_fun = True

if is_fun:
    print(name + " is fun!")

# 2. String Manipulation
print("\n--- 2. String Methods ---")
greeting = "  Hello World  "
print(greeting.strip())
print(greeting.upper())
print(greeting.lower())
print(greeting.replace("World", "Interpreter"))

# 3. Control Flow
print("\n--- 3. Loops ---")
# While Loop
i = 0
while i < 3:
    print(i)
    i = i + 1

# For Loop with Range
print("Counting with range:")
for j in range(1, 4):
    print(j)

# 4. Lists and Iteration
print("\n--- 4. Lists ---")
numbers = [10, 20, 30, 40, 50]
print(numbers)
print("First element:", numbers[0])
print("Length:", len(numbers))

print("Iterating over list:")
for num in numbers:
    if num > 25:
        print(num)

# 5. Functions
print("\n--- 5. Functions ---")
def square(n):
    return n * n

def calculate_area(width, height):
    return width * height

result = square(5)
print("Square of 5:", result)

area = calculate_area(10, 5)
print("Area of 10x5:", area)

# 6. Recursion (Bonus)
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

print("Factorial of 5:", factorial(5))