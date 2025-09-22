import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.symbol import *
from core.solve import Eq

# no sin cos tan log for now.
# all multiplications MUST be explicit use a * b to mean multiplication ab will be treated as one variable named ab


'''
prescedence ordering
1: binary +-
2: * /
3: unary +-
4: 
'''
# use Token for operators. Variables and Numbers get directly converted to exprs
class Token():
    def __init__(self,token_str:str, stack_level:int, unary = False):
        # +, -, *, /, **, var, num
        self.token_str = token_str
        self.unary = unary
        self.left_associative = True
        self.prescedence = 0

        if (unary == True or token_str in ('**')):
            self.left_associative = False

        if (unary == False and token_str in ('+','-')):
            self.prescedence += 1
        elif (token_str in ('*', '/')):
            self.prescedence += 2
        elif (token_str in ('**')):
            self.prescedence += 3
        elif unary == True:
            self.prescedence += 4
        self.prescedence += stack_level * 5

    # the idea is you would only consume operands with higher prescedence than yourself due to the conversation from high -> low prescedence. or it's a leaf with no prescedence.
    def to_expr(self, operands: list[Expr]):
        for op in operands:
            assert isinstance(op, Expr)
        if self.unary == True:
            assert(len(operands)) == 1
        else:
            assert(len(operands)) == 2

        if self.token_str == '+':
            return Add(*operands)
        elif self.token_str == '-' and self.unary == True:
            return Mul(-1, operands[0])
        elif self.token_str == '-' and self.unary == False:
            return Add(operands[0], Mul(-1,operands[1]))
        elif self.token_str == '*':
            return Mul(*operands)
        elif self.token_str == '/':
            return Mul(operands[0], Pow(operands[1],-1))
        elif self.token_str == '**':
            return Pow(operands[0], operands[1])

def _parse_exprstr_to_tokenlist(expr_str : str):
    token_list = []
    #for unary op classifying
    last_token_is_operator = True
    #for parenthesis
    stack_level = 0
    i = 0
    while i < len(expr_str):
        char = expr_str[i]
        if char == ' ' or char == ',':
            pass
        elif char == '(':
            stack_level += 1
        elif char == ')':
            stack_level -= 1
        elif char.isdigit() or char == '.':
            start = i
            while i < len(expr_str) and (expr_str[i].isdigit() or expr_str[i] == '.'):
                i += 1
            number_str = expr_str[start:i]
            token_list.append(Number(float(number_str)))
            i -= 1
            last_token_is_operator = False
        elif char.isalpha():
            start = i
            while i < len(expr_str) and (expr_str[i].isalpha() or expr_str[i] == '_'):
                i += 1
            variable_str = expr_str[start:i]
            token_list.append(Variable(variable_str))
            i -= 1
            last_token_is_operator = False
        elif char in ('+', '-'):
            if last_token_is_operator:
                token_list.append(Token(char, stack_level,True))
            else:
                token_list.append(Token(char, stack_level,False))
            last_token_is_operator = True
        elif char == '/':
            token_list.append(Token(char, stack_level))
            last_token_is_operator = True
        elif char == '*':
            # handle the ** case
            if i + 1 < len(expr_str) and expr_str[i + 1] == '*':
                token_list.append(Token('**', stack_level))
                i += 1  # Skip the next '*'
            else:
                token_list.append(Token('*', stack_level))
            last_token_is_operator = True           
        else:
            raise ValueError('string not supported cannot parse')
        i += 1
    return token_list

def _create_AST_from_tokenlist(token_list):
    prescedence_ordering = set()
    for token in token_list:
        if isinstance(token, Token):
            prescedence_ordering.add(token.prescedence)
    sorted_ordering = sorted(prescedence_ordering, reverse = True)
    for cur_prescedence in sorted_ordering:
        i = 0
        while i < len(token_list):
            cur_token = token_list[i]
            if (isinstance(cur_token, Token) and
                cur_token.prescedence == cur_prescedence and
                cur_token.left_associative == True):
                # no unary ops should be left associtive.
                assert(cur_token.unary == False)
                cur_expr = cur_token.to_expr([token_list[i-1], token_list[i+1]])
                token_list[i-1 : i+2] = [cur_expr]
                i -= 1
            i += 1

        i = len(token_list) - 1
        while i >= 0:
            cur_token = token_list[i]
            if (isinstance(cur_token, Token) and
                cur_token.prescedence == cur_prescedence and
                cur_token.left_associative == False):

                if cur_token.unary == True:
                    cur_expr = cur_token.to_expr([token_list[i+1]])
                    token_list[i : i+2] = [cur_expr]
                elif cur_token.unary == False:
                    cur_expr = cur_token.to_expr([token_list[i-1],token_list[i+1]])
                    token_list[i-1 : i+2] = [cur_expr]
                    i -= 1
            i -= 1
    assert (len(token_list) == 1)
    assert (isinstance(token_list[0], Expr))
    return token_list[0]

# handles = to create Eq here
def parse_expr(expr_str: str):
    for i, char in enumerate(expr_str):
        if char == '=':
            left_part = expr_str[:i]
            right_part = expr_str[i+1:]
            left_expr = parse_expr(left_part)
            right_expr = parse_expr(right_part)
            return Eq(left_expr, right_expr)
    
    token_list = _parse_exprstr_to_tokenlist(expr_str)
    expr = _create_AST_from_tokenlist(token_list)
    return expr


