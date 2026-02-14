class Statement:
    pass

class Number:
    def __init__(self, value):
        self.value = value

class String:
    def __init__(self, value):
        self.value = value

class Boolean:
    def __init__(self, value):
        self.value = value

class Identifier:
    def __init__(self, name):
        self.name = name

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Print:
    def __init__(self, expr):
        self.expr = expr
        
class ListNode:
    def __init__(self, elements):
        self.elements = elements
        
class IndexNode:
    def __init__(self, expr, index):
        self.expr = expr
        self.index = index
        
class StringMethod:
    def __init__(self, expr, method, args):
        self.expr = expr
        self.method = method
        self.args = args
        
class LenFunction:
    def __init__(self, expr):
        self.expr = expr
        
class ListAssign:
    def __init__(self, name, index, value):
        self.name = name
        self.index = index
        self.value = value
        
class TryExcept:
    def __init__(self, try_body, except_body):
        self.try_body = try_body
        self.except_body = except_body
        
class ListNode:
    def __init__(self, elements):
        self.elements = elements
        
class IndexNode:
    def __init__(self, expr, index):
        self.expr = expr
        self.index = index
        
class StringMethod:
    def __init__(self, expr, method, args):
        self.expr = expr
        self.method = method
        self.args = args
        
class LenFunction:
    def __init__(self, expr):
        self.expr = expr
        
class ListAssign:
    def __init__(self, name, index, value):
        self.name = name
        self.index = index
        self.value = value
        
class TryExcept:
    def __init__(self, try_body, except_body):
        self.try_body = try_body
        self.except_body = except_body

class Return:
    def __init__(self, expr):
        self.expr = expr

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class IfElse:
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileLoop:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop:
    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class RangeCall:
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step

class Break(Statement):
    pass

class Continue(Statement):
    pass