#!/usr/bin/env python2

import scanner
import ply.yacc as yacc

import AST

tokens = scanner.tokens
literals = scanner.literals


precedence = (
    ('nonassoc', 'IF'),
    ('nonassoc', 'ELSE'),
    ('right', '=', 'ADDASSIGN', 'SUBASSIGN', 'MULASSIGN', 'DIVASSIGN'),
    ('nonassoc', '<', '>', 'EQUAL', 'NOTEQUAL', 'LE', 'GE'),
    ('left', '+', '-'),
    ('left', 'DOTADD', 'DOTSUB'),
    ('left', '*', '/'),
    ('left', 'DOTMUL', 'DOTDIV'),
    ('right', 'UMINUS'),
    ('right', '\''),
)


def p_error(p):
    p.lexer.encountered_error = True
    if p:
        print("Syntax error at line {0}, column {1}: LexToken({2}, '{3}')"
              .format(p.lineno, scanner.find_column(p.lexer.lexdata, p),
                      p.type, p.value))
    else:
        print("Unexpected end of input")


# Starting point

def p_instructions(p):
    """instructions : instruction
                    | instruction instructions"""
    if len(p) == 2:
        p[0] = AST.Instructions(p.lineno(1), [p[1]])
    else:
        p[0] = p[2]
        p[0].nodes = [p[1]] + p[0].nodes


def p_instruction(p):
    """instruction : block
                   | conditional
                   | loop
                   | statement ';'
                   | error ';'"""
    p[0] = p[1]


# Block

def p_block(p):
    """block : '{' instructions '}'
             | '{' error '}'"""
    p[0] = AST.Block(p.lineno(1), p[2])


# Conditionals

def p_conditional(p):
    """conditional : IF '(' expression ')' instruction %prec IF
                   | IF '(' expression ')' instruction ELSE instruction"""
    if len(p) == 6:
        else_body = None
    else:
        else_body = p[7]
    p[0] = AST.If(p.lineno(1), p[3], p[5], else_body)


# Loops

def p_loop(p):
    """loop : while
            | for"""
    p[0] = p[1]


def p_while(p):
    """while : WHILE '(' expression ')' instruction"""
    p[0] = AST.While(p.lineno(1), p[3], p[5])


def p_for(p):
    """for : FOR ID '=' numeric_expression ':' numeric_expression instruction"""
    p[0] = AST.For(p.lineno(1), AST.Variable(p.lineno(1), p[2]), p[4], p[6], p[7])


# Statements

def p_statement(p):
    """statement : assignment
                 | flow_keyword
                 | return
                 | print"""
    p[0] = p[1]


def p_flow_keyword(p):
    """flow_keyword : BREAK
                    | CONTINUE"""
    p[0] = AST.FlowKeyword(p.lineno(1), p[1])


def p_return(p):
    """return : RETURN expression
              | RETURN """
    if len(p) == 2:
        p[0] = AST.Return(p.lineno(1))
    else:
        p[0] = AST.Return(p.lineno(1), p[2])


def p_print(p):
    """print : PRINT print_body"""
    p[0] = AST.Print(p.lineno(1), p[2])


def p_print_body(p):
    """print_body : expression ',' print_body
                  | expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_string(p):
    """string : STRING"""
    p[0] = AST.String(p.lineno(1), p[1][1:-1])


# Assignment

def p_assignment_var(p):
    """assignment_var : var
                      | array_range"""
    p[0] = p[1]


def p_assignment(p):
    """assignment : assignment_var assignment_operand expression
                  | assignment_var '=' string"""
    p[0] = AST.Assignment(p.lineno(1), p[2], p[1], p[3])


def p_assignment_operand(p):
    """assignment_operand : '='
                          | ADDASSIGN
                          | SUBASSIGN
                          | MULASSIGN
                          | DIVASSIGN"""
    p[0] = p[1]


# Variables, numbers and array range

def p_var(p):
    """var : ID
           | var '[' vector_body ']'"""
    if len(p) == 2:
        p[0] = AST.Variable(p.lineno(1), p[1])
    else:
        p[0] = AST.Reference(p.lineno(1), p[1], p[3])


def p_number(p):
    """number : INTNUM
              | FLOATNUM
              | var"""
    if isinstance(p[1], int):
        p[0] = AST.IntNum(p.lineno(1), p[1])
    elif isinstance(p[1], float):
        p[0] = AST.FloatNum(p.lineno(1), p[1])
    else:
        p[0] = p[1]


def p_array_range(p):
    """array_range : var '[' numeric_expression ',' numeric_expression ']'"""
    p[0] = AST.Reference(p.lineno(1), p[1], [p[3], p[5]])


# Expressions

def p_expression(p):
    """expression : numeric_expression
                  | comparison_expression"""
    p[0] = p[1]


# Numeric operations

def p_numeric_expression(p):
    """numeric_expression : number
                          | matrix
                          | vector
                          | string
                          | unary_operation
                          | function
                          | '(' numeric_expression ')'"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


# Binary numeric operations

def p_binary_numeric_expression(p):
    """numeric_expression : numeric_expression '+' numeric_expression
                          | numeric_expression '-' numeric_expression
                          | numeric_expression '*' numeric_expression
                          | numeric_expression '/' numeric_expression
                          | numeric_expression DOTADD numeric_expression
                          | numeric_expression DOTSUB numeric_expression
                          | numeric_expression DOTMUL numeric_expression
                          | numeric_expression DOTDIV numeric_expression"""
    p[0] = AST.ArithmeticOperation(p.lineno(1), p[2], p[1], p[3])


# Matrices

def p_vector(p):
    """vector : '[' vector_body ']'
              | '[' ']'"""
    if len(p) == 3:
        p[0] = AST.Vector(p.lineno(1), [])
    else:
        p[0] = AST.Vector(p.lineno(1), p[2])


def p_vector_body(p):
    """vector_body : numeric_expression
                   | vector_body ',' numeric_expression"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_matrix(p):
    """matrix : '[' matrix_body ']'"""
    p[0] = AST.Matrix(p.lineno(1), p[2])


def p_matrix_body(p):
    """matrix_body : vector_body
                   | matrix_body ';' vector_body"""
    if len(p) == 2:
        p[0] = [AST.Vector(p.lineno(1), p[1])]
    else:
        p[0] = p[1]
        p[0] += [AST.Vector(p.lineno(1), p[3])]


# Unary operations

def p_unary_operation(p):
    """unary_operation : negation
                       | transposition"""
    p[0] = p[1]


def p_negation(p):
    """negation : '-' numeric_expression %prec UMINUS"""
    p[0] = AST.UnaryExpr(p.lineno(1), "NEGATE", p[2])


def p_transposition(p):
    r"""transposition : numeric_expression '\''"""
    p[0] = AST.UnaryExpr(p.lineno(1), "TRANSPOSE", p[1])


# Special functions

def p_function(p):
    """function : function_name '(' vector_body ')'
                | function_name '(' error ')'"""
    p[0] = AST.FunctionCall(p.lineno(1), p[1], p[3])


def p_function_name(p):
    """function_name : EYE
                     | ZEROS
                     | ONES"""
    p[0] = p[1]


# Comparison expressions

def p_comparison_expression(p):
    """comparison_expression : numeric_expression '<' numeric_expression
                              | numeric_expression '>' numeric_expression
                              | numeric_expression EQUAL numeric_expression
                              | numeric_expression NOTEQUAL numeric_expression
                              | numeric_expression LE numeric_expression
                              | numeric_expression GE numeric_expression
                              | '(' comparison_expression ')'"""
    if p[1] == '(':
        p[0] = p[2]
    else:
        p[0] = AST.Comparison(p.lineno(1), p[2], p[1], p[3])


parser = yacc.yacc()
