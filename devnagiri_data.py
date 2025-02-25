# Load Devanagiri letters from a text file
with open('devnagiri.txt', 'r', encoding='utf-8') as file:
    DEVANAGIRI_LETTERS = file.read().split()

# Predefined Devanagiri digits and keywords
DEVANAGIRI_DIGITS = '०१२३४५६७८९'
DEVANAGIRI_KEYWORDS = {
    'मुद्रण': 'PRINT'
}

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
tt_id = 'IDENTIFIER'
tt_keyword = 'KEYWORD'
tt_eq = 'EQ'

# Token class
class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def __repr__(self):
        return f'{self.type}:{self.value}' if self.value else f'{self.type}'

# Position class
class Position:
    def __init__(self, index, line, col, filename, filetext):
        self.index = index
        self.line = line
        self.col = col
        self.filename = filename
        self.filetext = filetext

    def advance(self, current_char=None):
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.line += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.filename, self.filetext)

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
        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DEVANAGIRI_DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in DEVANAGIRI_LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char == '+':
                tokens.append(Token(tt_plus, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(Token(tt_eq, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(tt_lparen, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(tt_rparen, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, f"'{char}'")
        tokens.append(Token(tt_eof, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        pos_start = self.pos.copy()
        while self.current_char is not None and self.current_char in DEVANAGIRI_DIGITS:
            num_str += self.current_char
            self.advance()
        return Token(tt_int, int(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()
        while self.current_char is not None and self.current_char in DEVANAGIRI_LETTERS:
            id_str += self.current_char
            self.advance()
        token_type = tt_keyword if id_str in DEVANAGIRI_KEYWORDS else tt_id
        return Token(token_type, id_str, pos_start, self.pos)

# ParseResult class
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        res = ParseResult()
        if self.current_token.type == tt_keyword and self.current_token.value == 'मुद्रण':
            return self.print_statement()
        return res.failure(InvalidSyntaxError(
            self.current_token.pos_start, self.current_token.pos_end,
            "अपेक्षित 'मुद्रण' | Apekshit 'मुद्रण'"
        ))

    def print_statement(self):
        res = ParseResult()
        res.register(self.advance())  # Skip 'मुद्रण'
        if self.current_token.type != tt_lparen:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "अपेक्षित '(' | Apekshit '('"
            ))
        res.register(self.advance())  # Skip '('
        expr = res.register(self.expr())
        if res.error: return res
        if self.current_token.type != tt_rparen:
            return res.failure(InvalidSyntaxError(
                self.current_token.pos_start, self.current_token.pos_end,
                "अपेक्षित ')' | Apekshit ')'"
            ))
        res.register(self.advance())  # Skip ')'
        return res.success(PrintNode(expr))

# Interpreter
class Interpreter:
    def __init__(self):
        self.symbol_table = {}

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_PrintNode(self, node, context):
        value = self.visit(node.expr_node, context)
        print(value.value)
        return value

# Nodes
class PrintNode:
    def __init__(self, expr_node):
        self.expr_node = expr_node
        self.pos_start = expr_node.pos_start
        self.pos_end = expr_node.pos_end

# Error handling
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f'{self.error_name}: {self.details}'

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'गलत पत्र | Galat Patra', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'गलत वाक्यसंरचना | Galat Vakya Sanrachana', details)

# Run function
def run(text, filename):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    interpreter = Interpreter()
    result = interpreter.visit(ast.node, None)
    return result.value, result.error

# Example usage
if __name__ == '__main__':
    code = """
    अ = १२
    ख = १३
    मुद्रण(अ + ख)
    """
    result, error = run(code, '<stdin>')
    if error:
        print(error.as_string())