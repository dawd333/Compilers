#!/usr/bin/env python2

import AST
import Interpreter


class Memory:

    def __init__(self):
        self.variables = dict()

    def __str__(self):
        return repr(self.variables)

    def __repr__(self):
        return str(self)

    def has_key(self, node):  # variable name
        if isinstance(node, AST.Variable):
            return self.variables.get(node.name) is not None
        elif isinstance(node, Interpreter.ConcreteReference):
            return self.variables.get(node.container.name) is not None
        else:
            raise TypeError("{} is not a memory reference".format(node.__class__))

    def get(self, node):  # gets from memory current value of variable <name>
        if isinstance(node, AST.Variable):
            return self.variables.get(node.name)
        elif isinstance(node, Interpreter.ConcreteReference):
            value = self.get(node.container)
            for coord in node.coords:
                value = value[coord]
                if value is None:
                    break
            return value
        else:
            raise TypeError("{} is not a memory reference".format(node.__class__))

    def put(self, node, value):  # puts into memory current value of variable <name>
        if isinstance(node, AST.Variable):
            self.variables[node.name] = value
        elif isinstance(node, Interpreter.ConcreteReference):
            container = self.variables[node.container.name]
            for coord in node.coords[:-1]:
                container = container[coord]
            container[node.coords[-1]] = value
        else:
            raise TypeError("{} is not a memory reference".format(node.__class__))


class MemoryStack:

    def __init__(self, memory=None):  # initialize memory stack with memory <memory>
        self.stack = [Memory()]

    def __str__(self):
        s = "STACK [\n"
        for elem in self.stack:
            s += str(elem) + "\n"
        return s + "]"

    def __repr__(self):
        return str(self)

    def get(self, node):  # gets from memory stack current value of variable <name>
        result = None
        for elem in self.stack[::-1]:
            if elem.has_key(node):
                result = elem.get(node)
                break
        if result is None:
            if isinstance(node, AST.Variable):
                raise KeyError("Variable '{}' does not exist on stack".format(node.name))
            elif isinstance(node, Interpreter.ConcreteReference):
                raise KeyError("Variable '{}' does not exist on stack".format(node.container))
        return result

    def insert(self, node, value):  # inserts into memory stack variable <name> with value <value>
        self.stack[-1].put(node, value)

    def set(self, node, value):  # sets variable <name> to value <value>
        for elem in self.stack[::-1]:
            if elem.has_key(node):
                elem.put(node, value)
                break
        else:
            self.insert(node, value)

    def push(self, memory=None):  # pushes memory <memory> onto the stack
        if memory is None:
            memory = Memory()
        self.stack.append(memory)

    def pop(self):  # pops the top memory from the stack
        return self.stack.pop()

