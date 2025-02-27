from strings_with_arrows import *

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = 'EOF'
DIGITS_S = '०१२३४५६७८९'
DIGITS = '0123456789'
# Error
class Error:
    def __init__(self,pos_start,pos_end,err_name,details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = err_name
        self.details = details
    def as_string(self):
        result =  f"{self.error_name}:{self.details}"
        result += f'\nसंचिका <{self.pos_start.file_name}> , पंक्ति {self.pos_start.line+1} |\nsanchikaa <{self.pos_start.file_name}>, pankti {self.pos_start.line+1} '
        result += '\n\n' + string_with_arrows(self.pos_start.file_text,self.pos_start,self.pos_end)
        return result
class Illegal_Character_Error(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start,pos_end,'अवैध चरित्र | avaidh charitra', details)
class Invalid_Syntax_Error(Error):
    def __init__(self,pos_start,pos_end,details = ''):
        super().__init__(pos_start,pos_end,'अवैध वाक्यविन्यासः | avaidh vakyavinyasyah', details)
class RTError(Error):
    def __init__(self,pos_start,pos_end,details = ''):
        super().__init__(pos_start,pos_end,'रनटाइम् त्रुटिः | runtime trutih', details)
# Position
class Position:
    def __init__(self,index,line,column,file_name,file_text):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text
    def advance(self,current_char = None):
        self.index +=1
        self.column +=1

        if current_char == '\n':
            self.line += 1
            self.column = 0
        return self
    def copy(self):
        return Position(self.index,self.line,self.column,self.file_name,self.file_text)

# Token 
class Token:
    def __init__(self, type, value=None, pos_start = None,pos_end = None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()
    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"
# Lexer
class Lexer:
    def __init__(self,file_name,text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1,0,-1,file_name,text)
        self.current_char = None
        self.advance()
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None
    def make_tokens(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()  # Skip whitespace 
            elif self.current_char in DIGITS + DIGITS_S:
                
                tokens.append(self.make_number())  
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS,pos_start = self.pos))  
                self.advance()  
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS,pos_start = self.pos)) 
                self.advance()  
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL,pos_start = self.pos))  
                self.advance()  
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV,pos_start = self.pos)) 
                self.advance() 
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN,pos_start = self.pos))  
                self.advance()  
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN,pos_start = self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                character = self.current_char
                self.advance()
                return [], Illegal_Character_Error(pos_start,self.pos,("'" + character + "'"))  # Handle invalid characters
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None  # Return tokens and no error
    def make_number(self):
        # print("Make Number was called")
        n_str = ''
        dot = 0
        pos_start =  self.pos.copy()
        while self.current_char != None and (self.current_char in DIGITS + '.' + DIGITS_S):
            # print(self.current_char)
            # print(n_str)
            if self.current_char in DIGITS_S:
                dl = list(DIGITS_S)
                n = str(dl.index(self.current_char))
                print(n)
                n_str += n
            elif self.current_char in DIGITS:
                n_str += self.current_char
            elif self.current_char == '.':
                if dot == 1:break
                dot +=1
                n_str += '.'
            self.advance()

        if dot == 0:
            return Token(TT_INT,int(n_str),pos_start,self.pos)
        else:
            return Token(TT_FLOAT,float(n_str),pos_start,self.pos)
# Number 
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end
    def __repr__(self):
        return f'{self.tok}'
class BinaryOpNode:
    def __init__(self,left_node,op_tok,right_node):
        self.left_node = left_node
        self.right_node = right_node
        self.op_tok = op_tok

        self.pos_start =  self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    def __repr__(self):
        return f'({self.left_node},{self.op_tok},{self.right_node})'
class UnaryOpNode:
    def __init__(self,op_tok,node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start =  self.op_tok.pos_start
        self.pos_end  = node.pos_end
    def __repr__(self):
        return f'({self.op_tok},{self.node})'
# Parse Result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    def register(self,res):
        if isinstance(res,ParseResult):
            if res.error:
                self.error =  res.error
            return res.node
        return res
    def success(self,node):
        self.node  = node
        return self
    def failure(self,error):
        self.error = error
        return self
# Parser 
class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.advance()
    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,'अपेक्षितं * , + , - or / | apekchhit * , + , - or /'))
        return res
    def advance(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]
        return self.current_token
    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (TT_PLUS,TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error : return res
            return res.success(UnaryOpNode(tok,factor))
        elif tok.type in (TT_INT,TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        elif tok.type ==  TT_LPAREN:
            res.register(self.advance())
            expr =  res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षितं ')' | apekchhit ')'"))
        return res.failure(Invalid_Syntax_Error(tok.pos_start,tok.pos_end,'अपेक्षितं INT अथवा FLOAT | apekchhit INT athva FLOAT'))
    def term(self):
        return self.bin_op(self.factor,(TT_MUL,TT_DIV))
    def expr(self):
        return self.bin_op(self.term,(TT_MINUS,TT_PLUS))    
    def bin_op(self,func,ops):
        res  = ParseResult()
        left = res.register(func())
        if res.error:return res
        # self.advance()
        while self.current_token.type in ops:
            op_tok = self.current_token
            res.register(self.advance())
            right = res.register(func())
            if res.error : return res 
            left = BinaryOpNode(left,op_tok,right)
        return res.success(left)
# Runtime Result
class RTresult:
    def __init__(self):
        self.value  =  None
        self.error = None
    def register(self,res):
        if res.error:
            self.error =  res.error
        return res.value
# Values
class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()
    def set_pos(self,pos_start = None,pos_end = None):
        self.pos_start =  pos_start
        self.pos_end = pos_end
        return self
    def added_to(self,other):
        if isinstance(other,Number):
            return Number(self.value + other.value)
    def subtracted_from(self,other):
        if isinstance(other,Number):
            return Number(self.value - other.value)
    def multiplied_by(self,other):
        if isinstance(other,Number):
            return Number(self.value * other.value)
    def divided_by(self,other):
        if isinstance(other,Number):
            return Number(self.value / other.value)
    def __repr__(self):
        return str(self.value)
    
# Interpreter
class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method =  getattr(self, method_name, self.no_visit_method)
        return method(node)
    def no_visit_method(self,node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    def visit_NumberNode(self,node):
        return Number(node.tok.value).set_pos(node.pos_start,node.pos_end)
    def visit_BinaryOpNode(self,node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_tok.type == TT_PLUS:
            result = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result = left.subtracted_from(right)
        elif node.op_tok.type == TT_MUL:
            result = left.multiplied_by(right)
        elif node.op_tok.type == TT_DIV:
            result = left.divided_by(right)
        
        return result.set_pos(node.pos_start,node.pos_end)

    def visit_UnaryOpNode(self,node):
        number =  self.visit(node.node)
        if node.op_tok.type ==  TT_MINUS:
            number =  number.multiplied_by(Number(-1)).set_pos(node.pos_start,node.pos_end)
        return number

    
# Run
def Run(text,file_name):
    lexer = Lexer(file_name,text)
    tokens,error =  lexer.make_tokens()
    if error : return None,error
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error : 
        return None,ast.error
    interpreter = Interpreter( )
    result = interpreter.visit(ast.node)
    return result,None
