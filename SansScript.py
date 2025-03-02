from strings_with_arrows import *
import string
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = 'EOF'
TT_POW = 'POW'
TT_IDENTIFIER = 'IDENTIFIER'
TT_KEYWORD = 'KEYWORD'
TT_EQ = 'EQ'
TT_NE = 'NE'
TT_GT = 'GT'
TT_LT = 'LT'
TT_GTE = 'GTE'
TT_LTE = 'LTE'
TT_EE = 'EE'
KEYWORDS = ['charaH','charah','tathA','tatha','vA','va','nahi']

DIGITS_S = '०१२३४५६७८९'
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
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
class Expected_Char_Error(Error):
    def __init__(self,pos_start,pos_end,details = ''):
        super().__init__(pos_start,pos_end,'अवैध वाक्यविन्यासः | avaidh vakyavinyasyah', details)        
class RTError(Error):
    def __init__(self,pos_start,pos_end,details,context):
        super().__init__(pos_start,pos_end,'रनटाइम् त्रुटिः | runtime trutih', details)
        self.context =  context
    def as_string(self):
        result = self.generate_traceback()
        result +=  f"{self.error_name}:{self.details}"
        result += '\n\n' + string_with_arrows(self.pos_start.file_text,self.pos_start,self.pos_end)
        return result
    def generate_traceback(self):
        result = ''
        ctx = self.context
        pos = self.pos_start
        while ctx:
            result = f'      संचिका <{self.pos_start.file_name}> , पंक्ति {self.pos_start.line+1} |\n      sanchikaa <{self.pos_start.file_name}>, pankti {self.pos_start.line+1}\n '
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'अनुसन्धानं कुर्वन्तु, अद्यतनतमं आह्वानं अन्तिमम् | anusandhanam kurvantu , adyatanatamah aahvanah antimah :-\n' + result
    

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
    def matches(self,type_,value_a,value_b = None):
        if value_b:
            return self.type == type_ and self.value == value_a or value_b
        else:            
            return self.type == type_ and self.value == value_a
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
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
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
            elif self.current_char == '^':
                tokens.append(Token(TT_POW,pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals())
            elif self.current_char == '!':
                tok,error = self.make_not_equals()
                if error:
                    return [],None
                tokens.append(tok)
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())

            else:
                pos_start = self.pos.copy()
                character = self.current_char
                self.advance()
                return [], Illegal_Character_Error(pos_start,self.pos,("'" + character + "'"))  # Handle invalid characters
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        print(tokens)
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
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()
        
        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type,id_str,pos_start,self.pos)
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == '=':
            self.advance()
            return Token(TT_NE,pos_start=pos_start,pos_end=self.pos), None
        self.advance()
        return None,Expected_Char_Error(pos_start,self.pos," '=' अनन्तरम्‌ '!' | '=' anantaram '!'") 
    def make_equals(self):
        pos_start = self.pos.copy()
        tok_type = TT_EQ
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
        return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
    def make_greater_than(self):
        pos_start = self.pos.copy()
        tok_type = TT_GT
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
        return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
    def make_less_than(self):
        pos_start = self.pos.copy()
        tok_type = TT_LT
        self.advance()
        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
        return Token(tok_type,pos_start=pos_start,pos_end=self.pos)
        

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
class VarAccessNode:
    def __init__(self,var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end
class VarAssignNode:
    def __init__(self,var_name_tok,value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end


# Parse Result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
    def register_advancement(self):
        self.advance_count +=1
    def register(self,res):
        self.advance_count += res.advance_count
        if res.error:
            self.error =  res.error
        return res.node
        
    def success(self,node):
        self.node  = node
        return self
    def failure(self,error):
        # print(self.advance_count)
        if not self.error or self.advance_count ==0 :
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
    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (TT_INT,TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type ==  TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr =  res.register(self.expr())
            if res.error: return res
            if self.current_token.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षितं ')' | apekchhit ')'"))
        return res.failure(Invalid_Syntax_Error(tok.pos_start,tok.pos_end,'अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit INT,FLOAT,+,-,parichayakah athva ('))
    def power(self):
        return self.bin_op(self.atom,(TT_POW, ), self.factor)
    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (TT_PLUS,TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error : return res
            return res.success(UnaryOpNode(tok,factor))
        
        return self.power()
    def term(self):
        return self.bin_op(self.factor,(TT_MUL,TT_DIV))
    def arith_expr(self):
        return self.bin_op(self.term,(TT_PLUS,TT_MINUS))
    def comp_expr(self):
        res = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'nahi'):
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr)
            if res.error:
                return res
            return res.success(UnaryOpNode(self.current_token,node))
        node = res.register(self.bin_op(self.arith_expr,(TT_EE,TT_NE,TT_LT,TT_GT,TT_LTE,TT_GTE)))
        if res.error:
            return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit INT,FLOAT,+,-,nahi parichayakah athva ("))
        return res.success(node)
    def expr(self):
        res  = ParseResult()
        if self.current_token.matches(TT_KEYWORD,'charaH') or self.current_token.matches(TT_KEYWORD,'charah'):
            res.register_advancement()
            self.advance()
            print(self.current_token)
            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,'अपेक्षितं परिचयकः | apekchhit parichayakah'))
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            print(self.current_token)
            if self.current_token.type != TT_EQ:
                return res.failure(Invalid_Syntax_Error(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षितं '=' | apekchhit '=")) 
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error: 
                return res  
            return res.success(VarAssignNode(var_name,expr))                     
        node =  res.register(self.bin_op(self.comp_expr,((TT_KEYWORD,'tathA'),(TT_KEYWORD,'tatha'),(TT_KEYWORD,'vA'),(TT_KEYWORD,'va'))))
        if res.error:
            return res.failure(Invalid_Syntax_Error(self.current_token.pos_start, self.current_token.pos_end,'अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit charah ,INT,FLOAT,+,-,nahi,parichayakah athva ('))
        return res.success(node) 
    def bin_op(self,func_a,ops,func_b=None):
        res  = ParseResult()
        if func_b == None:
            func_b = func_a
        left = res.register(func_a())
        if res.error:return res
        # self.advance()
        while self.current_token.type in ops or (self.current_token.type,self.current_token.value) in ops:
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
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
    def success(self,value):
        self.value = value
        return self
    def failure(self,error):
        self.error = error
        return self
    
# Values
class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()
        self.set_context()
    def set_pos(self,pos_start = None,pos_end = None):
        self.pos_start =  pos_start
        self.pos_end = pos_end
        return self
    def set_context(self,context = None):
        self.context = context
        return self
    def added_to(self,other):
        if isinstance(other,Number):
            return Number(self.value + other.value).set_context(self.context),None
    def subtracted_from(self,other):
        if isinstance(other,Number):
            return Number(self.value - other.value).set_context(self.context),None
    def multiplied_by(self,other):
        if isinstance(other,Number):
            return Number(self.value * other.value).set_context(self.context),None
    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start,self.pos_end)
        copy.set_context(self.context)
        return copy
    def to_power(self,other):
        if isinstance(other,Number):
            return Number(self.value ** other.value).set_context(self.context),None
    def divided_by(self,other):
        if isinstance(other,Number):
            if other.value == 0:
                return None,RTError(
                    other.pos_start,other.pos_end,
                    'शून्येन विभागः | shunyen vibhagah',
                    self.context
                )
            return Number(self.value / other.value).set_context(self.context),None
    def get_comp_eq(self,other):
        if isinstance(other,Number):
            return Number(int(self.value == other.value)).set_context(self.context),None
    def get_comp_ne(self,other):
        if isinstance(other,Number):
            return Number(int(self.value != other.value)).set_context(self.context),None
    def get_comp_lt(self,other):
        if isinstance(other,Number):
            return Number(int(self.value < other.value)).set_context(self.context),None
    def get_comp_gt(self,other):
        if isinstance(other,Number):
            return Number(int(self.value > other.value)).set_context(self.context),None
    def get_comp_gte(self,other):
        if isinstance(other,Number):
            return Number(int(self.value >= other.value)).set_context(self.context),None
    def get_comp_lte(self,other):
        if isinstance(other,Number):
            return Number(int(self.value <= other.value)).set_context(self.context),None
    def anded_by(self,other):
        if isinstance(other,Number):
            return Number(int(self.value and other.value)).set_context(self.context),None
    def ored_by(self,other):
        if isinstance(other,Number):
            return Number(int(self.value or other.value)).set_context(self.context),None
    def notted(self):
        return Number(int(1 if self.value == 0 else 0)).set_context(self.context),None
    def __repr__(self):
        return str(self.value)
# Context 
class Context:
    def __init__(self,display_name,parent = None,parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None
# Symbol Table
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None
    def get(self,name):
        value =  self.symbols.get(name,None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value
    def set(self,name,value):
        self.symbols[name] = value
    def remove(self,name):
        del self.symbols[name]

# Interpreter
class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method =  getattr(self, method_name, self.no_visit_method)
        return method(node,context)
    
    def no_visit_method(self,node,context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    def visit_VarAccessNode(self,node,context):
        res = RTresult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(node.pos_start, node.pos_end,f"'{var_name}' न विवक्षितम् | {var_name} na vivakshitam",context))
        value = value.copy().set_pos(node.pos_start,node.pos_end)
        return res.success(value)
    def visit_VarAssignNode(self,node,context):
        res = RTresult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node,context))
        if res.error :
            return res
        context.symbol_table.set(var_name,value)
        return res.success(value)
    
        
    
    def visit_NumberNode(self,node,context):
        return RTresult().success(Number(node.tok.value).set_context(context).set_pos(node.pos_start,node.pos_end))
    
    def visit_BinaryOpNode(self,node,context):
        res = RTresult()
        left = res.register(self.visit(node.left_node,context))
        if res.error:return res
        right = res.register(self.visit(node.right_node,context))
        if res.error:return res

        result,error = None,None
        if node.op_tok.type == TT_PLUS:
            result,error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result,error = left.subtracted_from(right)
        elif node.op_tok.type == TT_MUL:
            result,error = left.multiplied_by(right)
        elif node.op_tok.type == TT_DIV:
            result,error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result,error = left.to_power(right)
        elif node.op_tok.type == TT_EE:
            result,error = left.get_comp_eq(right)
        elif node.op_tok.type == TT_NE:
            result,error = left.get_comp_ne(right)
        elif node.op_tok.type == TT_LT:
            result,error = left.get_comp_lt(right)
        elif node.op_tok.type == TT_GT:
            result,error = left.get_comp_gt(right)
        elif node.op_tok.type == TT_LTE:
            result,error = left.get_comp_lte(right)
        elif node.op_tok.type == TT_GTE:
            result,error = left.get_comp_gte(right)
        elif node.op_tok.matches(TT_KEYWORD,'tatha','tathA'):
            result,error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD,'va','vA'):
            result,error = left.ored_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start,node.pos_end))

    def visit_UnaryOpNode(self,node,context):
        res = RTresult()
        number =  res.register(self.visit(node.node,context))
        if res.error:
            return res
        error = None
        if node.op_tok.type ==  TT_MINUS:
            number,error =  number.multiplied_by(Number(-1))
        elif node.op_tok.matches(TT_IDENTIFIER,'nahi'):
            number,error = number.notted()
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start,node.pos_end))
global_symbol_table = SymbolTable()
global_symbol_table.set("null",Number(0))
    
# Run
def Run(text,file_name):
    print(text)
    converted_text = str(transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS))
    print(converted_text)
    lexer = Lexer(file_name,converted_text)
    tokens,error =  lexer.make_tokens()
    if error : return None,error
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error : 
        return None,ast.error
    interpreter = Interpreter()
    context = Context('<कार्यक्रम> | <karyakram>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node,context)
    return result.value,result.error
