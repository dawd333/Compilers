#!/usr/bin/env python2

import sys
import ply.yacc as yacc
import Mparser
from TreePrinter import TreePrinter
from TypeChecker import TypeChecker
from Interpreter import Interpreter
from Exceptions import ReturnValueException

if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "examples/example1.m"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = Mparser.parser
    text = file.read()
    lexer = Mparser.scanner.lexer
    lexer.encountered_error = False
    ast = parser.parse(text, lexer=lexer, tracking=True)
    if not lexer.encountered_error and ast is not None:
        ast.printTree()
        typeChecker = TypeChecker()
        typeChecker.visit(ast)

        if not typeChecker.encountered_error:
            try:
                ast.accept(Interpreter())
            except ReturnValueException as e:
                print("RETURNED {}".format(e.value))
