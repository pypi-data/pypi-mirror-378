import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.symbol import *

def is_sub (expr):
    if (isinstance(expr, Mul)
        and isinstance(expr.operands[0], Number)
        and expr.operands[0].value < 0):
            return True
    return False

def is_div (expr):
    if isinstance(expr, Pow) and expr.operands[1].is_negone():
        return True
    return False

'''
complete logic pseudocode
all parenthesis are helper functions that add parenthesis if 

is_sub: -1 * exprs
is_div  exprs ** -1

handle SUB and DIV at the um at the LOCAL level

alright lets handle the div_1_prefix now
need prefix when
1: it is a stand alone term (no mul) either it is a pow by itself or part of add
dont need prefix when it is: not the first op in mul

ADD
basic add case:
3 + a + b
-3 - a + b
3 + a ** -1 + b -> 3 + /a + b

code:
if 0 or is_sub (op)
    result += helper(op)
else:
    result += '+'
    result += helper(op)

MUL
mul cases:
3 * a * b
-3 * a ** -1 * b
code:
if 0 or is_div (op)
    result += helper (op)
else:
    result += '*'
    result += helper(op)

POW:
pow cases:
3 ** a
a ** -1
code:
if is_div(self):
    result += '/'
    result += helper(base)
else:
    result += helper(base)
    result += '**'
    result += heler (exponent)
''' 

def str_flat(expr, div_need_1_prefix = True):
    if expr.is_leaf():
        return str(expr)
    elif isinstance(expr, Add):
        result = ''
        for i, op in enumerate(expr.operands):
            if i == 0 or is_sub(op):
                result += str_flat(op) # the first term or - op. no + sign
            else: #normal case or div case. does not handle + 1 / for now
                result += ' + '
                result += str_flat(op)
        return result

    elif isinstance(expr, Mul):
        result = ''
        def helper(op, div_need_1_prefix = True):
            tempstr = str_flat(op, div_need_1_prefix)
            if isinstance(op, Add):
                tempstr = '(' + tempstr + ')'
            return tempstr

        if is_sub(expr):
            result += ' - '
            pos_expr = expr * -1
            pos_str = helper(pos_expr)
            result += pos_str
        else:
            for i, op in enumerate(expr.operands):
                if is_div(op):
                    if i == 0:
                        result += helper (op)
                    else:
                        result += helper (op, False)
                elif i == 0:
                    result += helper(op)
                else:
                    result += ' * '
                    result += helper(op)
        return result

    elif isinstance(expr, Pow):

        result = ''
        def helper(op):
            tempstr = str_flat(op)
            if isinstance(op, Add) or isinstance(op, Mul):
                tempstr = '(' + tempstr + ')'
            return tempstr

        base_str = helper(expr.base)
        exponent_str = helper(expr.exponent)

        if is_div(expr):
            if div_need_1_prefix:
                result += ' 1 / '
            else:
                result += ' / '
            result += base_str
        else:
            result += base_str
            result += ' ** '
            result += exponent_str
        return result
