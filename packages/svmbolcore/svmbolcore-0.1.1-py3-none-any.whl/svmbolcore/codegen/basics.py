import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.symbol import *

def is_sub (expr):
    if isinstance(expr, Mul) and expr.operands[0].is_negone():
        return True

def is_div (expr):
    if isinstance(expr, Pow) and expr.operands[1].is_negone():
        return True

def str_flat(expr):
    if expr.is_leaf():
        return str(expr)
    elif isinstance(expr, Add):
        result = ''
        for i, op in enumerate(expr.operands):
            if is_sub(op):
                result += str_flat(op) # - op. no + sign
            elif is_div(op):
                result += ' + 1' # will become + 1 / base
                result += str_flat(op)
            elif i == 0:
                result += str_flat(op) # no + sign in the first
            else:
                result += ' + ' #normal case
                result += str_flat(op)
        return result

    elif isinstance(expr, Mul):
        result = ''

        def helper(op):
            tempstr = str_flat(op)
            if isinstance(op, Add):
                tempstr = '(' + tempstr + ')'
            return tempstr

        for i, op in enumerate(expr.operands):
            if i == 0:
                if is_sub(expr):
                    result += ' - '
                elif is_div(op):
                    result += ' 1'
                    result += helper(op)
                else:
                    result += helper(op)
            elif i == 1:
                if is_sub(expr):
                    if is_div(op):
                        result += ' 1'
                    result += helper(op)
                else:
                    result += ' * '
                    result += helper(op)
            elif is_div (op):
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
            result += ' / '
            result += base_str
        else:
            result += base_str
            result += ' ** '
            result += exponent_str
        return result



