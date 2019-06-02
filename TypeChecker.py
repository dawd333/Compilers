#!/usr/bin/env python2

import AST
from collections import defaultdict
from copy import copy
from SymbolTable import Variable, SymbolTable

allowed_operations = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: "")))

allowed_operations["+"]["int"]["int"] = "int"
allowed_operations["+"]["float"]["int"] = "float"
allowed_operations["+"]["int"]["float"] = "float"
allowed_operations["+"]["float"]["float"] = "float"
allowed_operations["+"]["vector"]["vector"] = "vector"
allowed_operations["+"]["matrix"]["matrix"] = "matrix"
allowed_operations["+"]["string"]["string"] = "string"

allowed_operations["-"]["int"]["int"] = "int"
allowed_operations["-"]["float"]["int"] = "float"
allowed_operations["-"]["int"]["float"] = "float"
allowed_operations["-"]["float"]["float"] = "float"

allowed_operations["*"]["int"]["int"] = "int"
allowed_operations["*"]["float"]["int"] = "float"
allowed_operations["*"]["int"]["float"] = "float"
allowed_operations["*"]["float"]["float"] = "float"
allowed_operations["*"]["matrix"]["matrix"] = "matrix"

allowed_operations["/"]["int"]["int"] = "int"
allowed_operations["/"]["float"]["int"] = "float"
allowed_operations["/"]["int"]["float"] = "float"
allowed_operations["/"]["float"]["float"] = "float"

allowed_operations[".+"]["matrix"]["matrix"] = "matrix"
allowed_operations[".+"]["vector"]["vector"] = "vector"

allowed_operations[".-"]["matrix"]["matrix"] = "matrix"
allowed_operations[".-"]["vector"]["vector"] = "vector"

allowed_operations[".*"]["matrix"]["matrix"] = "matrix"
allowed_operations[".*"]["vector"]["vector"] = "vector"

allowed_operations["./"]["matrix"]["matrix"] = "matrix"
allowed_operations["./"]["vector"]["vector"] = "vector"

allowed_operations["NEGATE"]["int"]["int"] = "int"
allowed_operations["NEGATE"]["float"]["float"] = "float"
allowed_operations["NEGATE"]["matrix"]["matrix"] = "matrix"
allowed_operations["TRANSPOSE"]["matrix"]["matrix"] = "matrix"
allowed_operations

operation_to_string = {
    '=': 'ASSIGN',
    '+': 'ADD',
    '-': 'SUB',
    '*': 'MUL',
    '/': 'DIV',
    '.+': 'DOTADD',
    '.-': 'DOTSUB',
    '.*': 'DOTMUL',
    './': 'DOTDIV',
    '+=': 'ADDASSIGN',
    '-=': 'SUBASSIGN',
    '*=': 'MULASSIGN',
    '/=': 'DIVASSIGN'
}


class Undefined(Variable):
    def __init__(self, name=""):
        Variable.__init__(self, 'undefined', [], name)


class NodeVisitor(object):
    loop = 0
    symbols = SymbolTable()

    def visit(self, node, *args, **kwargs):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method)
        return visitor(node, *args, **kwargs)


class TypeChecker(NodeVisitor):
    encountered_error = False

    def ensure_defined(self, node, variable):
        if variable.type == "undefined":
            self.print_error(node, "undefined variable")
            return False
        return True

    def visit_Instructions(self, node):
        for n in node.nodes:
            self.visit(n)

    def visit_Block(self, node):
        self.symbols = self.symbols.createChild()
        self.visit(node.content)
        self.symbols = self.symbols.getParentScope()

    def visit_FlowKeyword(self, node):
        if self.loop == 0:
            self.print_error(node, "flow keyword {} outside loop".format(node.keyword))

    def visit_Print(self, node):
        for a in node.arguments:
            self.visit(a)

    def visit_Return(self, node):
        if node.value is not None:
            self.visit(node.value)

    def visit_String(self, node):
        return Variable("string")

    def visit_Matrix(self, node):
        for e in node.elements:
            self.visit(e)
        size1 = len(node.elements)
        sizes = map(lambda x: len(x.elements), node.elements)
        size2 = min(sizes)
        if all(x == size2 for x in sizes):
            return Variable("matrix", [size1, size2])
        else:
            self.print_error(node, "vectors with different sizes in matrix initialization")
            return None

    def visit_Vector(self, node):
        for e in node.elements:
            self.visit(e)
        return Variable("vector", [len(node.elements)])

    def visit_Reference(self, node, *args, **kwargs):
        container = self.visit(node.container)
        if container.isUndefined():
            return Undefined()

        if len(node.coords) > len(container.size):
            self.print_error(node, "too many dimensions in vector reference")
            return Undefined()

        error = False

        for c in node.coords:
            c_var = self.visit(c)
            if c_var.type != 'int':
                self.print_error(node, "expected int as array coordinate, have {}".format(c_var.type))
                error = True
        if error:
            return Undefined()

        for coord, size in zip(node.coords, container.size):
            if coord.value >= size:
                self.print_error(node, "reference {} out of bounds for size {}".format(coord.value, size))
                error = True
        if error:
            return Undefined()
        if len(container.size) - len(node.coords) == 0:
            return Variable("float")
        else:
            return Variable("vector", [container.size[-1]])

    def visit_FunctionCall(self, node):
        arguments = node.arguments

        for arg in arguments:
            arg_var = self.visit(arg)
            if arg_var.type != 'int':
                self.print_error(node, "expected int as array coordinate, have {}".format(arg_var.type))
                return Undefined()

        if len(arguments) == 1:
            arguments = [arguments[0], arguments[0]]

        bounds = [0, 0]
        for i, arg in enumerate(arguments):
            if isinstance(arg, AST.IntNum):
                bounds[i] = arg.value
            else:
                bounds[i] = float('+inf')
        return Variable("matrix", bounds)

    def visit_While(self, node):
        self.loop += 1
        self.visit(node.body)
        self.loop -= 1

    def visit_For(self, node):
        self.visit(node.range)
        self.loop += 1
        self.symbols = self.symbols.createChild()
        iterator_var = Variable('int', [], node.iterator.name)
        self.symbols.put(iterator_var.name, iterator_var)
        self.visit(node.body)
        self.symbols.getParentScope()
        self.loop -= 1

    def visit_Range(self, node):
        self.visit(node.start)
        self.visit(node.end)

    def visit_Variable(self, node, allow_undefined=False):
        result = self.symbols.get(node.name)
        if result is None:
            if not allow_undefined:
                self.print_error(node, "undefined variable {}".format(node.name))
            result = Undefined(node.name)
        return result

    def visit_If(self, node):
        self.visit(node.condition)
        self.visit(node.body)
        if node.else_body:
            self.visit(node.else_body)

    def visit_BinExpr(self, node):
        var_left = self.visit(node.left)
        var_right = self.visit(node.right)
        op = node.op
        if var_left.type == "matrix" and var_right.type == "matrix" and op == "*":
            if var_left.size[0] != var_right.size[1] and var_left.size[1] != var_right.size[0]:
                self.print_error(node, "matrix dimensions not proper for multiplication: {} and {}".format(var_left.size, var_right.size))
                return Undefined()

        result_type = allowed_operations[op][var_left.type][var_right.type]

        if result_type:
            new_variable = copy(var_left)
            new_variable.type = result_type
            return new_variable
        else:
            self.print_error(node, "cannot {} {} and {}".format(operation_to_string[op], var_left.type, var_right.type))
        return Undefined()

    def visit_ArithmeticOperation(self, node):
        return self.visit_BinExpr(node)

    def visit_Assignment(self, node):

        op = node.op
        overwrite = op == "="

        var_left = self.visit(node.left, overwrite)
        var_right = self.visit(node.right)

        is_slice = isinstance(node.left, AST.Reference)

        if not overwrite and var_left.isUndefined():
            return None
        if var_right.isUndefined():
            return None

        if is_slice:
            if var_left.type == 'vector' and var_right.type != 'vector':
                self.print_error(node, "cannot assign {} to a matrix slice, expected vector".format(var_right.type))
            elif var_left.type == 'vector' and var_right.size != var_left.size[1]:
                self.print_error(node, "vector sized {} does not match matrix dimensions".format(var_right.size))
            elif var_left.type == 'float':
                if var_right.type not in ('int', 'float'):
                    self.print_error(node, 'matrix element must be INT or FLOAT')

        else:
            if overwrite:
                new_variable = Variable(var_right.type, var_right.size, var_left.name)
                self.symbols.put(var_left.name, new_variable)
            else:
                result_type = allowed_operations[op[0]][var_left.type][var_right.type]
                if result_type != "":
                    new_variable = Variable(result_type, var_right.size, var_left.name)
                    self.symbols.put(var_left.name, new_variable)
                else:
                    operation = operation_to_string[op]
                    self.print_error(node, "cannot {} {} to {}".format(operation, var_right.type, var_left.type))

    def visit_IntNum(self, node):
        return Variable("int")

    def visit_FloatNum(self, node):
        return Variable("float")

    def visit_UnaryExpr(self, node):
        operand = self.visit(node.operand)
        if operand.isUndefined():
            self.print_error(node, "undefined variable {}".format(operand.name))

        result_type = allowed_operations[node.operation][operand.type][operand.type]
        if result_type:
            return Variable(result_type, operand.size[::-1])
        else:
            self.print_error(node, "cannot perform {} on {}".format(node.operation, operand.type))
            return Undefined()

    def visit_Comparison(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_Error(self, node):
        pass

    @classmethod
    def result_size(cls, op, var_left, var_right):
        if var_left.type != 'matrix' or var_right.type != 'matrix':
            return var_left.size

        if op == "*":
            return [var_left.size[0], var_right.size[1]]
        elif op == "+":
            return [var_left.size[0] + var_right.size[0], var_left.size[1]]
        else:
            return var_left.size

    def print_error(self, node, error):
        self.encountered_error = True
        print("Error in line {}: {}".format(node.lineno, error))
