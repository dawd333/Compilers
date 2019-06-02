#!/usr/bin/env python2


class Node(object):
    def accept(self, visitor):
        return visitor.visit(self)


class Instructions(Node):
    def __init__(self, lineno, nodes):
        self.lineno = lineno
        self.nodes = nodes


class Block(Node):
    def __init__(self, lineno, content):
        self.lineno = lineno
        self.content = content


class FlowKeyword(Node):
    def __init__(self, lineno, keyword):
        self.lineno = lineno
        self.keyword = keyword.upper()


class Print(Node):
    def __init__(self, lineno, arguments):
        self.lineno = lineno
        self.arguments = arguments


class Return(Node):
    def __init__(self, lineno, value=None):
        self.lineno = lineno
        self.value = value


class String(Node):
    def __init__(self, lineno, value):
        self.lineno = lineno
        self.value = value


class Vector(Node):
    def __init__(self, lineno, elements):
        self.lineno = lineno
        self.elements = elements


class Matrix(Node):
    def __init__(self, lineno, elements):
        self.lineno = lineno
        self.elements = elements


class Reference(Node):
    # Matrix cell reference

    def __init__(self, lineno, container, coords):
        self.lineno = lineno
        self.container = container
        self.name = container
        self.coords = coords


class FunctionCall(Node):
    def __init__(self, lineno, func_name, arguments):
        self.lineno = lineno
        self.name = func_name
        self.arguments = arguments


class While(Node):
    def __init__(self, lineno, condition, body):
        self.lineno = lineno
        self.condition = condition
        self.body = body


class For(Node):
    def __init__(self, lineno, iterator, start, end, body):
        self.lineno = lineno
        self.iterator = iterator
        self.range = Range(lineno, start, end)
        self.body = body


class Range(Node):
    def __init__(self, lineno, start, end):
        self.lineno = lineno
        self.start = start
        self.end = end


class Variable(Node):
    def __init__(self, lineno, name):
        self.lineno = lineno
        self.name = name

    def __str__(self):
        return "AST.Variable({})".format(self.name)

    def __repr__(self):
        return str(self)


class If(Node):
    def __init__(self, lineno, condition, body, else_body=None):
        self.lineno = lineno
        self.condition = condition
        self.body = body
        self.else_body = else_body


class BinExpr(Node):
    def __init__(self, lineno, op, left, right):
        self.lineno = lineno
        self.op = op
        self.left = left
        self.right = right


class ArithmeticOperation(BinExpr):
    pass


class Assignment(BinExpr):
    pass


class IntNum(Node):
    def __init__(self, lineno, value):
        self.lineno = lineno
        self.value = value


class FloatNum(Node):
    def __init__(self, lineno, value):
        self.lineno = lineno
        self.value = value


class UnaryExpr(Node):
    def __init__(self, lineno, operation, operand):
        self.lineno = lineno
        self.operation = operation
        self.operand = operand


class Comparison(BinExpr):
    pass


class Error(Node):
    def __init__(self):
        pass
