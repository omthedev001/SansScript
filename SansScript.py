#Made By omthedev
#SansScript
# Constants
DIGIT = '0123456789'
# Errors 
class Error:
    def __init__(self,pos_start,pos_end,error,details):
        self.error = error
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
    def as_string(self):
        result = f'{self.error}: {self.details}'
        result += f' in File <{self.pos_start.filename}>, line {self.pos_start.line + 1}'
        return result
class IllegalCharError(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start,pos_end,'Illegal Character',details)
class InvalidSyntaxError(Error):
    def __init__(self,pos_start,pos_end,details=''):
        super().__init__(pos_start,pos_end,'Invalid Syntax',details)
# Position 
class Position:
    def __init__(self,index,line,col,filename,filetext):
        self.index = index
        self.line = line
        self.col = col
        self.filename = filename
        self.filetext = filetext
    def advance(self,current_char=None):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.line += 1
            self.col = 0
        return self
    def copy(self):
        return Position(self.index,self.line,self.col,self.filename,self.filetext)
# Token types
tt_int = 'INT'
tt_float = 'FLOAT'
tt_plus = 'PLUS'
tt_minus = 'MINUS'
tt_mul = 'MUL'
tt_div = 'DIV'
tt_lparen = 'LPAREN'
tt_rparen = 'RPAREN'
tt_eof = 'EOF'

class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(None)
        

    def __repr__(self):
        return self.type + (f':{self.value}' if self.value != None else '')
    
# Lexer

class Lexer:
    def __init__(self, text, filename):
        self.text = text
        self.filename = filename
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.advance()
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    def make_tokens(self):
        tokens = []
        while(self.current_char !=None):
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGIT:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(tt_plus,pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(tt_minus,pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(tt_mul,pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(tt_div,pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(tt_lparen,pos_start=self.pos))  
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(tt_rparen,pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,"'" + char + "'")
        tokens.append(Token(tt_eof,pos_start=self.pos))
        return tokens,None
    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char != None and self.current_char in DIGIT + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(tt_int, int(num_str),pos_start,self.pos)
        else:
            return Token(tt_float, float(num_str),pos_start,self.pos)
# Nodes
class NumberNode:
    def __init__(self,token):
        self.token = token
    def __repr__(self):
        return f'{self.token}'
class BinOpNode:
    def __init__(self,left_node,op_token,right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    def __repr__(self):
        return f'({self.left_node},{self.op_token},{self.right_node})'
class UnaryOpNode:
    def __init__(self,op_token,node):
        self.op_token = op_token
        self.node = node
    def __repr__(self):
        return f'({self.op_token},{self.node})'
# Parser
class Parser:  
    def __init__(self,tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != tt_eof:
            return res.failure(InvalidSyntaxError(self.current_token.pos_start,self.current_token.pos_end,"Expected '+','-','*','/'"))
        return res
    def factor(self):
        result = ParseResult()
        token = self.current_token
        if token.type in (tt_plus,tt_minus):
            result.register(self.advance())
            factor = result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOpNode(token,factor))
        elif token.type in (tt_int,tt_float):
            result.register(self.advance())
            return result.success(NumberNode(token))
        elif token.type == tt_lparen:
            result.register(self.advance())
            expr = result.register(self.expr())
            if result.error: return result
            if self.current_token.type == tt_rparen:
                result.register(self.advance())
                return result.success(expr)
            return result.failure(InvalidSyntaxError(token.pos_start,token.pos_end,"Expected ')'"))
        return result.failure(InvalidSyntaxError(token.pos_start,token.pos_end,"Expected int or float"))
    def term(self):
        return self.binary_operation(self.factor,[tt_mul,tt_div])
    def binary_operation(self,function,operation):
        res = ParseResult()
        left = res.register(function())
        if res.error: return res
        while self.current_token.type in operation:
            op_token = self.current_token
            res.register(self.advance())
            right = res.register(function())
            left = BinOpNode(left,op_token,right)
        return res.success(left)
    
    def expr(self):
        return self.binary_operation(self.term,[tt_plus,tt_minus])
# Parse result 
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    def register(self,res):
        if isinstance(res,ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res
    def success(self,node):
        self.node = node
        return self
    def failure(self,error):
        self.error = error
        return self
# RUN
def run(text,fn):
    lexer = Lexer(text,fn)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    
    parser = Parser(tokens)
    tree = parser.parse()
    return tree.node, tree.error
