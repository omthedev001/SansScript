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
# Position 
class Position:
    def __init__(self,index,line,col,filename,filetext):
        self.index = index
        self.line = line
        self.col = col
        self.filename = filename
        self.filetext = filetext
    def advance(self,current_char):
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

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

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
                tokens.append(Token(tt_plus))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(tt_minus))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(tt_mul))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(tt_div))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(tt_lparen))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(tt_rparen))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,"'" + char + "'")
        return tokens,None
    def make_number(self):
        num_str = ''
        dot_count = 0
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
            return Token(tt_int, int(num_str))
        else:
            return Token(tt_float, float(num_str))
# RUN
def run(text,fn):
    lexer = Lexer(text,fn)
    tokens, error = lexer.make_tokens()
    return tokens, error
