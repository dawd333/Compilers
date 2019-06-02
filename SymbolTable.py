#!/usr/bin/env python2


class Variable(object):
    def __init__(self, type, size=[], name=""):
        self.type = type
        self.size = size
        self.name = name

    def __str__(self):
        return '(Variable {}: {}, {})'.format(self.name, self.type, self.size)

    def __repr__(self):
        return str(self)

    def isUndefined(self):
        return self.type == "undefined"


class SymbolTable(object):

    def __init__(self, parent = None): # parent scope and symbol table name
        self.parent = parent
        self.symbols = dict()
        pass

    def put(self, name, symbol): # put variable symbol or fundef under <name> entry
        self.symbols[name] = symbol

    def get(self, name): # return symbol of given name or None is the symbol is not known
        local = self.symbols.get(name)
        if local is None and self.hasParent():
            return self.parent.get(name)
        return local

    def getParentScope(self):
        return self.parent

    def hasParent(self):
        return self.parent is not None

    def createChild(self):
        return SymbolTable(self)