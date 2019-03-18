import ply.lex as lex

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'eye': 'EYE',
    'zeros': 'ZEROS',
    'ones': 'ONES',
    'return': 'RETURN',
    'print': 'PRINT'
}

tokens = ['DOTADD', 'DOTSUB', 'DOTMUL', 'DOTDIV', 'ADDASSIGN', 'SUBASSIGN', 'MULASSIGN', 'DIVASSIGN', 'GE', 'LE',
          'NOTEQUAL', 'EQUAL', 'ID', 'INTNUM', 'FLOATNUM', 'STRING'] + list(reserved.values())

t_DOTADD = r'\.\+'
t_DOTSUB = r'\.-'
t_DOTMUL = r'\.\*'
t_DOTDIV = r'\./'
t_ADDASSIGN = r'\+='
t_SUBASSIGN = r'-='
t_MULASSIGN = r'\*='
t_DIVASSIGN = r'/='
t_GE = r'>='
t_LE = r'<='
t_NOTEQUAL = r'!='
t_EQUAL = r'=='


def t_ID(t):
    r'[_a-zA-Z]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_FLOATNUM(t):
    r'\d*\.\d+([Ee][+-]?\d+)?|\d+\.([Ee][+-]?\d+)?'
    t.value = float(t.value)
    return t


def t_INTNUM(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'".*?"'
    t.value = str(t.value)
    return t


t_ignore = ' \t'
t_ignore_comment = r'\#.*'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def find_column(text, token):
    line_start = text.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def t_error(t):
    print("Illegal character %s" % t.value[0] + " at line %s" % t.lineno)
    t.lexer.skip(1)


literals = "+-*/=<>()[]{}:',;"

lexer = lex.lex()

