import graphviz
import uuid
from .ast_nodes import *

class ASTVisualizer:
    def __init__(self):
        self.dot = graphviz.Digraph(comment='Abstract Syntax Tree')
        self.dot.attr(rankdir='TB')  # Top to Bottom
        self.node_count = 0

    def add_node(self, label, shape='ellipse', color='lightblue', style='filled'):
        node_id = str(uuid.uuid4())
        self.dot.node(node_id, label, shape=shape, color=color, style=style)
        return node_id

    def add_edge(self, start, end, label=''):
        self.dot.edge(start, end, label=label)

    def visualize(self, node):
        if isinstance(node, list):
            # Create a root node for the list
            root_id = self.add_node("Block", shape='box', color='lightgrey')
            for item in node:
                child_id = self.visualize(item)
                if child_id:
                    self.add_edge(root_id, child_id)
            return root_id
        
        if node is None:
            return None

        # Basic Literals
        if isinstance(node, (Number, String, Boolean)):
            return self.add_node(f"{type(node).__name__}\n{node.value}", shape='ellipse', color='#e1f5fe')

        if isinstance(node, Identifier):
            return self.add_node(f"ID\n{node.name}", shape='ellipse', color='#fff9c4')

        # Complex Nodes
        node_type = type(node).__name__
        root_id = self.add_node(node_type, shape='box', color='#f3e5f5')

        # Recursively visualize children
        # We check specific attributes for known node types to create meaningful edges
        
        if isinstance(node, BinaryOp):
            left_id = self.visualize(node.left)
            self.add_edge(root_id, left_id, 'left')
            
            # Op is usually a string in BinaryOp, but let's handle if it's a node
            if isinstance(node.op, str):
                op_id = self.add_node(f"Op\n{node.op}", shape='circle', color='#ffe0b2')
                self.add_edge(root_id, op_id, 'op')
            else:
                op_id = self.visualize(node.op)
                self.add_edge(root_id, op_id, 'op')
                
            right_id = self.visualize(node.right)
            self.add_edge(root_id, right_id, 'right')

        elif isinstance(node, Assign):
            name_id = self.visualize(node.name)
            self.add_edge(root_id, name_id, 'target')
            expr_id = self.visualize(node.expr)
            self.add_edge(root_id, expr_id, 'value')

        elif isinstance(node, IfElse):
            cond_id = self.visualize(node.condition)
            self.add_edge(root_id, cond_id, 'condition')
            if_id = self.visualize(node.if_body)
            self.add_edge(root_id, if_id, 'if')
            if node.else_body:
                else_id = self.visualize(node.else_body)
                self.add_edge(root_id, else_id, 'else')

        elif isinstance(node, WhileLoop):
            cond_id = self.visualize(node.condition)
            self.add_edge(root_id, cond_id, 'condition')
            body_id = self.visualize(node.body)
            self.add_edge(root_id, body_id, 'body')

        elif isinstance(node, ForLoop):
            var_id = self.visualize(node.var)
            self.add_edge(root_id, var_id, 'var')
            iter_id = self.visualize(node.iterable)
            self.add_edge(root_id, iter_id, 'iterable')
            body_id = self.visualize(node.body)
            self.add_edge(root_id, body_id, 'body')

        elif isinstance(node, FunctionDef):
            # Name shouldn't be visualized as a child node usually, but as part of the label
            # But here node.name is a string usually? Let's check ast_nodes.py
            # FunctionDef(self, name, params, body)
            pass 
            # Actually let's just inspect __dict__ for generic fallback
            # but specific handling is better for graph structure.
            
            # Recurse on all other attributes
            for attr, value in node.__dict__.items():
                if attr == 'name' and isinstance(value, str):
                   # We already included node type, maybe append name to label?
                   # For now let's just create a node for it
                   pass
                elif isinstance(value, list):
                    # List of params or statements
                    list_id = self.add_node(attr, shape='point')
                    self.add_edge(root_id, list_id, attr)
                    for item in value:
                        child_id = self.visualize(item)
                        if child_id:
                            self.add_edge(list_id, child_id)
                elif isinstance(value, (Statement, Expression, object)) and hasattr(value, '__dict__'):
                     child_id = self.visualize(value)
                     if child_id:
                         self.add_edge(root_id, child_id, attr)

        else:
            # Generic fallback
            for attr, value in node.__dict__.items():
                if isinstance(value, (int, float, str, bool)):
                     # Maybe add leaf nodes for these?
                     if attr not in ['lineno', 'lexpos']:
                        leaf_id = self.add_node(str(value), shape='plaintext')
                        self.add_edge(root_id, leaf_id, attr)
                elif isinstance(value, list):
                    for item in value:
                        child_id = self.visualize(item)
                        if child_id:
                            self.add_edge(root_id, child_id, attr)
                elif value:
                    child_id = self.visualize(value)
                    if child_id:
                        self.add_edge(root_id, child_id, attr)

        return root_id
