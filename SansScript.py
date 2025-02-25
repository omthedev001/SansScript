#Made By omthedev
#SansScript
import string
# Constants
with open('devnagiri.txt','r',encoding='utf-8') as f:
    letters = f.read()
LETTERS = letters
print(LETTERS)
LETTER = string.ascii_letters
DIGIT = '0123456789'
DIGITS_SANS = '०१२३४५६७८९'

LETTERS_DIGITS_S = LETTERS + DIGITS_SANS
LETTERS_DIGITS = LETTER + DIGIT

KEYWORD = ['चरः']
# Errors 
class Error:
    def __init__(self,pos_start,pos_end,error,details):
        self.error = error
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.details = details
    def as_string(self):
        result = f'{self.error}: {self.details}'
        result += f' ,अस्मीन सामुकायं दसह: अस्ति | Asmin sanchikayam doshah asti <{self.pos_start.filename}>, पङ्क्ति | pankti {self.pos_start.line + 1}'
        return result
class IllegalCharError(Error):
    def __init__(self,pos_start,pos_end,details):
        super().__init__(pos_start,pos_end,'गलत पत्र! | galat patra',details)
class InvalidSyntaxError(Error):
    def __init__(self,pos_start,pos_end,details=''):
        super().__init__(pos_start,pos_end,'गलत वाक्यसंरचना | galat vakyasanrachana!',details)
class RunTimeError(Error):
    def __init__(self,pos_start,pos_end,details,context):
        super().__init__(pos_start,pos_end,'संचालने दोषः | sanchalane doshah!',details)
        self.context = context
    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error}: {self.details}'
        return result
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context
        while context:
            result = f'फ़ाइलः <{pos.filename}>, पङ्क्तिः {pos.line + 1}, स्थानः {pos.col + 1}, संदेशः {context.display_name}\n | file {pos.filename}, pankti {pos.line + 1}, sthanah {pos.col + 1}, sandeshah {context.display_name} ' + result
            pos = context.parent_entry_pos
            context = context.parent
        return 'संचालने दोषः | sanchalane doshah!\n' + result
# RunTime Result
class RunTimeResult:
    def __init__(self):
        self.value = None
        self.error = None
    def register(self,res):
        if res.error: self.error = res.error
        return res.value
    def success(self,value):
        self.value = value
        return self
    def failure(self,error):
        self.error = error
        return self
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
tt_pow = 'POW'
tt_id = 'IDENTIFIER'
tt_keyword = 'KEYWORD'
tt_eq = 'EQ'
tt_ne = 'NE'
tt_true = 'TRUE'
tt_false = 'FALSE'
class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance(None)
        
    def matches(self,type,value):
        return self.type == type and self.value == value
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
            elif self.current_char in DIGITS_SANS:
                sans_list = list(DIGITS_SANS)
                # print(sans_list)
                self.current_char = str(sans_list.index(self.current_char))
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                # print(self.current_char)
                tokens.append(self.make_identifier())
            elif self.current_char in DIGIT:
                # print(self.current_char)
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
            elif self.current_char == '^':
                tokens.append(Token(tt_pow,pos_start=self.pos))
                self.advance()
            elif self.current_char == '\n':
                tokens.append(Token(tt_eof,pos_start=self.pos))
                self.advance()
            elif self.current_char == '=' :
                tokens.append(Token(tt_eq,pos_start=self.pos))
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
    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()
        # print(self.current_char)
        while self.current_char != None and self.current_char in LETTERS_DIGITS_S + '_' + LETTERS_DIGITS:
            id_str += self.current_char
            # print(id_str + "id_str")
            self.advance()
        token_type = tt_keyword if id_str in KEYWORD else tt_id
        return Token(token_type,id_str,pos_start,self.pos)

# Nodes
class NumberNode:
    def __init__(self,token):
        self.token = token
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
    def __repr__(self):
        return f'{self.token}'
class VarAccessNode:
    def __init__(self,var_name_token):
        self.var_name_token = var_name_token
        self.pos_start = var_name_token.pos_start
        self.pos_end = var_name_token.pos_end

class VarAssignNode:
    def __init__(self,var_name_token,value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
        self.pos_start = self.var_name_token.pos_start
        self.pos_end = self.value_node.pos_end
class BinOpNode:
    def __init__(self,left_node,op_token,right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
        self.pos_start = left_node.pos_start
        self.pos_end = right_node.pos_end
    def __repr__(self):
        return f'({self.left_node},{self.op_token},{self.right_node})'
class UnaryOpNode:
    def __init__(self,op_token,node):
        self.op_token = op_token
        self.node = node
        self.pos_start = op_token.pos_start
        self.pos_end = node.pos_end
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
            return res.failure(InvalidSyntaxError(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षित '+','-','*','/' | Apekshit '+','-','*','/'"))
        return res
    def power(self):
        return self.binary_operation(self.atom,(tt_pow,),self.factor)
    def atom(self):
        res = ParseResult()
        token = self.current_token
        if token.type in (tt_int,tt_float):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(token))
        elif token.type == tt_id:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(token))
        elif token.type == tt_lparen:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_token.type == tt_rparen:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            return res.failure(InvalidSyntaxError(token.pos_start,token.pos_end,"अपेक्षित ')' | Apekshit ')'"))
        return res.failure(InvalidSyntaxError(token.pos_start,token.pos_end,"अपेक्षित 'INT','FLOAT','(' | Apekshit 'INT','FLOAT','('"))
    def factor(self):
        result = ParseResult()
        token = self.current_token
        if token.type in (tt_plus,tt_minus):
            result.register(self.advance())
            factor = result.register(self.factor())
            if result.error: return result
            return result.success(UnaryOpNode(token,factor))
        return self.power()
        
    def term(self):
        return self.binary_operation(self.factor,[tt_mul,tt_div])
    def binary_operation(self,function_a,operation,function_b=None):
        if function_b == None:
            function_b = function_a
        res = ParseResult()
        left = res.register(function_a())
        if res.error: return res
        while self.current_token.type in operation:
            op_token = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(function_b())
            left = BinOpNode(left,op_token,right)
        return res.success(left)
    
    def expr(self):
        res = ParseResult()
        if self.current_token.matches(tt_keyword,'चरः'):
            # print("found keyword")
            res.register_advancement()
            self.advance()
            if self.current_token.type != tt_id:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षित वर्णमाला | Apekshit varnamala"))
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != tt_eq:
                return res.failure(InvalidSyntaxError(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षित '=' | Apekshit '='"))
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success((VarAssignNode(var_name,expr)))
        node = res.register(self.binary_operation(self.term,[tt_plus,tt_minus]))
        if res.error :
            return res.failure(InvalidSyntaxError(self.current_token.pos_start,self.current_token.pos_end,"अपेक्षित 'INT','FLOAT','चरः' | Apekshit 'INT','FLOAT','CHARAH'"))
        return res.success(node)
# Parse result 
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
    def register_advancement(self):
        pass
    def register(self,res):
        if res.error: self.error = res.error
        return res.node
        
    def success(self,node):
        self.node = node
        return self
    def failure(self,error):
        self.error = error
        return self
# Number
class Number:
    def __init__(self,value):
        self.value = value
        self.set_context(None)
    def set_posistion(self,pos_start,pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    def set_context(self,context):
        self.context = context
        return self
    def added_to(self,other):
        if isinstance(other,Number):
            return Number(self.value + other.value).set_context(self.context),None
    def subtracted_by(self,other):
        if isinstance(other,Number):
            return Number(self.value - other.value).set_context(self.context),None
    def multiplied_by(self,other):
        if isinstance(other,Number):
            return Number(self.value * other.value).set_context(self.context),None
    def divided_by(self,other):
        if isinstance(other,Number):
            if other.value == 0:
                return None,RunTimeError(other.pos_start,other.pos_end,"किं भवता शून्येन विभाजनस्य प्रयासः कृतः | Kim bhavata shunyena vibhajanasya prayasah kritah !",self.context)
            return Number(self.value / other.value).set_context(self.context),None
    def powered(self,other):
        if isinstance(other,Number):
            return Number(self.value ** other.value).set_context(self.context),None
    def __repr__(self):
        return str(self.value)
# context 
class Context:
    def __init__(self,display_name,parent=None,parent_entry_pos=None):
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
        value = self.symbols.get(name,None)
        if value == None and self.parent:
            return self.parent.get(name)
        
        return value
    def set(self,name,value):
        self.symbols[name] = value
    def remove(self,name):
        del self.symbols[name]
# Interpreter
class Interpreter:
    def visit(self,node,context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self,method_name)
        return method(node,context)
    def visit_VarAccessNode(self,node,context):
        res = RunTimeResult()
        var_name = node.var_name_token.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(RunTimeError(node.pos_start,node.pos_end,"अभिविन्यासः अस्ति | Abhivinyasah asti",context))
        return res.success(value)
    def visit_VarAssignNode(self,node,context):
        res = RunTimeResult()
        var_name = node.var_name_token.value
        value = res.register(self.visit(node.value_node,context))
        if res.error: return res
        context.symbol_table.set(var_name,value)
        return res.success(value)
    def dont_visit(self,node,context):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    def visit_NumberNode(self,node,context):
        
        return RunTimeResult().success( Number(node.token.value).set_context(context).set_posistion(node.token.pos_start,node.token.pos_end))
    def visit_BinOpNode(self,node,context):
        # print("found binop node")
        result = RunTimeResult()
        left = result.register(self.visit(node.left_node,context))
        if result.error: return left
        right = result.register(self.visit(node.right_node,context))
        if result.error: return right

        if node.op_token.type == tt_plus:
            res,error = left.added_to(right)
        elif node.op_token.type == tt_minus:
            res,error = left.subtracted_by(right)
        elif node.op_token.type == tt_mul:
            res,error = left.multiplied_by(right)
        elif node.op_token.type == tt_div:
            res,error = left.divided_by(right)
        elif node.op_token.type == tt_pow:
            res,error = left.powered(right)
        if error:
            return result.failure(error)
        else:
            return result.success(res.set_posistion(node.left_node.pos_start,node.right_node.pos_end))
    def visit_UnaryOpNode(self,node,context):
        # print("found unaryop node")
        res = RunTimeResult()
        number = res.register(self.visit(node.node,context))
        if res.error: return number
        error = None
        if node.op_token.type == tt_minus:
            number,error = number.multiplied_by(Number(-1))
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_posistion(node.op_token.pos_start,node.node.pos_end))
        # self.visit(node.op_token)
global_symbol_table = SymbolTable()
global_symbol_table.set("लुप्तमूल्य",Number(0))
# RUN
def run(text,fn):
    lexer = Lexer(text,fn)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    
    parser = Parser(tokens)
    tree = parser.parse()
    if tree.error:
        return None, tree.error
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(tree.node,context)
    return result.value, result.error
