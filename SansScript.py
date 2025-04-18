from strings_with_arrows import *
import string
import os
import math
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING_S = "STRING_S"
TT_STRING_D = "STRING_D"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF"
TT_POW = "POW"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQ = "EQ"
TT_NE = "NE"
TT_GT = "GT"
TT_LT = "LT"
TT_GTE = "GTE"
TT_LTE = "LTE"
TT_EE = "EE"
TT_LSQUARE = "LSQUARE"
TT_RSQUARE = "RSQUARE"
TT_COMMA = "COMMA"
TT_NEWLINE = "NEWLINE"
KEYWORDS = [
    "charaH",
    "charah",
    "tathA",
    "tatha",
    "vA",
    "va",
    "nahi",
    "yadi",
    ":",
    "anyadi",
    "uta",
    "kRRite",
    "krrite",
    "ityasmai",
    "charaNa",
    "charana",
    "yAvad",
    "yavad",
    "niyoga",
    "sopanah",
    "sopAnaH",
    "aMta",
    "anta",
    "amta",
    "anuvartanam",
    "pratyAvartanam",
    "pratyavartanam",
    "virAmaH",
    "viramah"
]

DIGITS_S = "०१२३४५६७८९"
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


# Error
class Error:
    def __init__(self, pos_start, pos_end, err_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = err_name
        self.details = details

    def as_string(self):
        result = f"{self.error_name}:{self.details}"
        result += f"\nसंचिका <{self.pos_start.file_name}> , पंक्ति {self.pos_start.line+1} |\nsanchikaa <{self.pos_start.file_name}>, pankti {self.pos_start.line+1} "
        result += "\n\n" + string_with_arrows(
            self.pos_start.file_text, self.pos_start, self.pos_end
        )
        return result


class Illegal_Character_Error(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "अवैध चरित्र | avaidh charitra", details)


class Invalid_Syntax_Error(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(
            pos_start, pos_end, "अवैध वाक्यविन्यासः | avaidh vakyavinyasyah", details
        )


class Expected_Char_Error(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(
            pos_start, pos_end, "अवैध वाक्यविन्यासः | avaidh vakyavinyasyah", details
        )


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "रनटाइम् त्रुटिः | runtime trutih", details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f"{self.error_name}:{self.details}"
        result += "\n\n" + string_with_arrows(
            self.pos_start.file_text, self.pos_start, self.pos_end
        )
        return result

    def generate_traceback(self):
        result = ""
        ctx = self.context
        pos = self.pos_start
        while ctx:
            result = f"      संचिका <{self.pos_start.file_name}> , पंक्ति {self.pos_start.line+1} |\n      sanchikaa <{self.pos_start.file_name}>, pankti {self.pos_start.line+1}\n "
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return (
            "अनुसन्धानं कुर्वन्तु, अद्यतनतमं आह्वानं अन्तिमम् | anusandhanam kurvantu , adyatanatamah aahvanah antimah :-\n"
            + result
        )


# Position
class Position:
    def __init__(self, index, line, column, file_name, file_text):
        self.index = index
        self.line = line
        self.column = column
        self.file_name = file_name
        self.file_text = file_text

    def advance(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == "\n":
            self.line += 1
            self.column = 0
        return self

    def copy(self):
        return Position(
            self.index, self.line, self.column, self.file_name, self.file_text
        )


# Token
class Token:
    def __init__(self, type, value=None, pos_start=None, pos_end=None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value_a, value_b=None):
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
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0, -1, file_name, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = (
            self.text[self.pos.index] if self.pos.index < len(self.text) else None
        )

    def make_tokens(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in " \t":
                self.advance()  # Skip whitespace
            elif self.current_char in "#":
                self.skip_comment()
            elif self.current_char in ";\n":
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char in DIGITS + DIGITS_S:
                tokens.append(self.make_number())
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "!":
                tok, error = self.make_not_equals()
                if error:
                    return [], None
                tokens.append(tok)
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ":":
                tokens.append(Token(TT_KEYWORD, ":", pos_start=self.pos))
                self.advance()
            elif self.current_char == "[":
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == "]":
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == "'":
                tokens.append(self.make_string())

            elif self.current_char == '"':
                tokens.append(self.make_string())

            else:
                pos_start = self.pos.copy()
                character = self.current_char
                self.advance()
                return [], Illegal_Character_Error(
                    pos_start, self.pos, ("'" + character + "'")
                )  # Handle invalid characters
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None  # Return tokens and no error
    def skip_comment(self):
        self.advance()
        while self.current_char != "\n":
            self.advance()
        self.advance()
    def make_string(self):
        string_ = ""
        pos_start = self.pos.copy()
        str_type = self.current_char
        escape_character = False
        escape_characters = {
            "n": "\n",
            "t": "\t",
        }
        self.advance()
        if str_type == "'":
            while self.current_char != None and (
                self.current_char != "'" or escape_character
            ):
                if escape_character:
                    string_ += escape_characters.get(
                        self.current_char, self.current_char
                    )
                else:
                    if self.current_char == "\\":
                        escape_character = True
                    else:
                        string_ += self.current_char
                self.advance()
                escape_character = False
            self.advance()
            return Token(TT_STRING_S, string_, pos_start, self.pos)
        elif str_type == '"':
            while self.current_char != None and (
                self.current_char != '"' or escape_character
            ):
                if escape_character:
                    string_ += escape_characters.get(
                        self.current_char, self.current_char
                    )
                else:
                    if self.current_char == "\\":
                        escape_character = True
                    else:
                        string_ += self.current_char

                self.advance()
                escape_character = False
            self.advance()
            return Token(TT_STRING_D, string_, pos_start, self.pos)

    def make_number(self):
        # print("Make Number was called")
        n_str = ""
        dot = 0
        pos_start = self.pos.copy()
        while self.current_char != None and (
            self.current_char in DIGITS + "." + DIGITS_S
        ):
            # print(self.current_char)
            # print(n_str)
            if self.current_char in DIGITS_S:
                dl = list(DIGITS_S)
                n = str(dl.index(self.current_char))
                n_str += n
            elif self.current_char in DIGITS:
                n_str += self.current_char
            elif self.current_char == ".":
                if dot == 1:
                    break
                dot += 1
                n_str += "."
            self.advance()

        if dot == 0:
            return Token(TT_INT, int(n_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(n_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()
        # print(self.current_char)
        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == "=":
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, Expected_Char_Error(
            pos_start, self.pos, " '=' अनन्तरम्‌ '!' | '=' anantaram '!'"
        )

    def make_equals(self):
        pos_start = self.pos.copy()
        tok_type = TT_EQ
        self.advance()
        if self.current_char == "=":
            self.advance()
            tok_type = TT_EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        pos_start = self.pos.copy()
        tok_type = TT_GT
        self.advance()
        if self.current_char == "=":
            self.advance()
            tok_type = TT_GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        pos_start = self.pos.copy()
        tok_type = TT_LT
        self.advance()
        if self.current_char == "=":
            self.advance()
            tok_type = TT_LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


# Number
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class BinaryOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.right_node = right_node
        self.op_tok = op_tok

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f"({self.left_node},{self.op_tok},{self.right_node})"


class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op_tok},{self.node})"


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end


class ifNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class ForNode:
    def __init__(
        self,
        var_name_tok,
        start_value_node,
        end_value_node,
        step_value_node,
        body_node,
        should_return_null,
    ):
        self.var_name_tok = var_name_tok
        self.start_value_node = start_value_node
        self.end_value_node = end_value_node
        self.step_value_node = step_value_node
        self.body_node = body_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end
        self.should_return_null = should_return_null


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end
        self.should_return_null = should_return_null


class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_tok, body_node, should_auto_return):

        self.var_name_tok = var_name_tok
        self.arg_name_tok = arg_name_tok
        self.body_node = body_node
        self.should_auto_return = should_auto_return
        if var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(arg_name_tok) > 0:
            self.pos_start = self.arg_name_tok[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.pos_start = self.node_to_call.pos_start
        if len(arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end


# Parse Result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = -1
        self.advance()

    def parse(self):
        res = self.statements()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "अपेक्षितं * , + , - or / | apekchhit * , + , - or /",
                )
            )
        return res

    def statements(self):
        res = ParseResult()
        statements = []

        pos_start = self.current_token.pos_start.copy()

        while self.current_token.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_token.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = res.try_register(self.statement())
            if not statement:

                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(
            ListNode(statements, pos_start, self.current_token.pos_end.copy())
        )

    def statement(self):
        res = ParseResult()
        pos_start = self.current_token.pos_start.copy()
        if self.current_token.matches(
            TT_KEYWORD, "pratyAvartanam"
        ) or self.current_token.matches(TT_KEYWORD, "pratyavartanam"):

            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                return self.reverse(res.to_reverse_count)
            return res.success(
                ReturnNode(expr, pos_start, self.current_token.pos_end.copy())
            )

        if self.current_token.matches(
            TT_KEYWORD, "virAmaH"
        ) or self.current_token.matches(TT_KEYWORD, "viramah"):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_token.pos_end.copy()))
        if self.current_token.matches(TT_KEYWORD, "anuvartanam"):
            res.register_advancement()
            self.advance()
            return res.success(
                ContinueNode(pos_start, self.current_token.pos_end.copy())
            )

        expr = res.register(self.expr())
        if res.error:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "अपेक्षितं वाक्यम् | apekchhitam vakhyam",
                )
            )
        return res.success(expr)

    def advance(self):
        self.tok_index += 1
        self.update_current_tok()
        return self.current_token

    def reverse(self, amount=1):
        self.tok_index -= amount
        self.update_current_tok()
        return self.current_token

    def update_current_tok(self):
        if self.tok_index >= 0 and self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.check_if_cases("yadi"))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(ifNode(cases, else_case))

    def check_if_cases(self, case):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_token.matches(TT_KEYWORD, case):
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    f"Expected '{case}'",
                )
            )

        res.register_advancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(TT_KEYWORD, ":"):
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Expected ':'",
                )
            )

        res.register_advancement()
        self.advance()

        # CORRECTED: Get the actual expression node
        if self.current_token.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            statements = res.register(self.statements())
            if res.error:
                return res
            cases.append((condition, statements, True))

            if self.current_token.matches(TT_KEYWORD, "aMta"):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.check_if_BCCASE())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            # FIX: Register the expression and get the node
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))  # Store the node, not ParseResult

            all_cases = res.register(self.check_if_BCCASE())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def check_if_elif(self):
        return self.check_if_cases("anyadi")

    def check_if_else(self):
        res = ParseResult()
        else_case = None

        if self.current_token.matches(TT_KEYWORD, "uta"):
            res.register_advancement()
            self.advance()

            if self.current_token.type != TT_KEYWORD:  # Missing colon check
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Expected ':' after 'uta'",
                    )
                )

            res.register_advancement()
            self.advance()

            if self.current_token.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error:
                    return res
                else_case = (statements, True)

                if not self.current_token.matches(TT_KEYWORD, "anta"):
                    return res.failure(
                        Invalid_Syntax_Error(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "Expected 'anta'",
                        )
                    )
                res.register_advancement()
                self.advance()
            else:
                expr = res.register(self.statement())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def check_if_BCCASE(self):
        res = ParseResult()
        cases = []
        else_case = None

        # Handle anyadi (elif) cases
        while self.current_token.matches(TT_KEYWORD, "anyadi"):
            cases_res = res.register(self.check_if_cases("anyadi"))
            if res.error:
                return res
            cases.extend(cases_res[0])

        # Handle uta (else) case
        if self.current_token.matches(TT_KEYWORD, "uta"):
            else_res = res.register(self.check_if_else())
            if res.error:
                return res
            else_case = else_res

        return res.success((cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, "krrite"):
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit 'krrite'",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_token.type != TT_IDENTIFIER:
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit 'Identifier'",
                )
            )
        var_name = self.current_token
        res.register_advancement()
        self.advance()
        if self.current_token.type != TT_EQ:
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit '='",
                )
            )
        res.register_advancement()
        self.advance()
        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_token.matches(TT_KEYWORD, "ityasmai"):
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit 'ityasmai'",
                )
            )
        res.register_advancement()
        self.advance()
        end_value = res.register(self.expr())
        if res.error:
            return res
        if self.current_token.matches(TT_KEYWORD, "charana"):
            res.register_advancement()
            self.advance()
            step_value = res.register(self.expr())
            if res.error:
                return res
        else:
            step_value = None
        if not self.current_token.matches(TT_KEYWORD, ":"):
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit ':'",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_token.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())

            if res.error:
                return res

            if not self.current_token.matches(TT_KEYWORD, "aMta"):

                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं 'anta' | apekchhit 'anta'",
                    )
                )
            res.register_advancement()
            self.advance()

            return res.success(
                ForNode(var_name, start_value, end_value, step_value, body, True)
            )

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(
            ForNode(var_name, start_value, end_value, step_value, body, False)
        )

    def while_expr(self):
        res = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, "sopanah"):

            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit 'sopanah'",
                )
            )
        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res
        if not self.current_token.matches(TT_KEYWORD, ":"):
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit ':'",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_token.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_token.matches(TT_KEYWORD, "aMta"):
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं 'anta' | apekchhit 'anta'",
                    )
                )
            res.register_advancement()
            self.advance()
            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res
        return res.success(WhileNode(condition, body, False))

    def func_def(self):
        res = ParseResult()
        arg_name_tok = []
        if not self.current_token.matches(TT_KEYWORD, "niyoga"):
            return res.failure(
                Expected_Char_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "apekchhit 'niyoga'",
                )
            )

        res.register_advancement()
        self.advance()
        if self.current_token.type == TT_IDENTIFIER:
            var_name_tok = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != TT_LPAREN:
                return res.failure(
                    Expected_Char_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "apekchhit '('",
                    )
                )
            res.register_advancement()
            self.advance()
        else:
            var_name_tok = None
            if self.current_token.type != TT_LPAREN:
                return res.failure(
                    Expected_Char_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "apekchhit 'identifier' , '('",
                    )
                )
            res.register_advancement()
            self.advance()
            arg_name_tok = []
        if self.current_token.type == TT_IDENTIFIER:
            arg_name_tok.append(self.current_token)
            res.register_advancement()
            self.advance()
            while self.current_token.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_token.type != TT_IDENTIFIER:
                    return res.failure(
                        Expected_Char_Error(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "apekchhit 'identifier'",
                        )
                    )
                arg_name_tok.append(self.current_token)
                res.register_advancement()
                self.advance()
            if self.current_token.type != TT_RPAREN:
                return res.failure(
                    Expected_Char_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "apekchhit ',' or ')'",
                    )
                )
        else:
            if self.current_token.type != TT_RPAREN:
                return res.failure(
                    Expected_Char_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "apekchhit 'identifier' , ')'",
                    )
                )

        res.register_advancement()
        self.advance()
        if self.current_token.matches(TT_KEYWORD, ":"):
            res.register_advancement()
            self.advance()
            if self.current_token.type != TT_NEWLINE:
                body = res.register(self.expr())
                if res.error:
                    return res
                return res.success(FuncDefNode(var_name_tok, arg_name_tok, body, True))
            if self.current_token.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                body = res.register(self.statements())
                if res.error:
                    return res
                while self.current_token.type == TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                if not (
                    self.current_token.matches(TT_KEYWORD, "anta")
                    or self.current_token.matches(TT_KEYWORD, "aMta")
                ):
                    return res.failure(
                        Invalid_Syntax_Error(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "अपेक्षितं 'anta' | apekchhit 'anta'",
                        )
                    )
                res.register_advancement()
                self.advance()
                return res.success(FuncDefNode(var_name_tok, arg_name_tok, body, False))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res
        if self.current_token.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []
            if self.current_token.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        Invalid_Syntax_Error(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit INT,FLOAT,+,-,parichayakah athva (",
                        )
                    )

                while self.current_token.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res
                if self.current_token.type != TT_RPAREN:
                    return res.failure(
                        Expected_Char_Error(
                            self.current_token.pos_start,
                            self.current_token.pos_end,
                            "apekchhit ',' or ')'",
                        )
                    )
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def list_expr(self):
        res = ParseResult()
        list_element_nodes = []
        pos_start = self.current_token.pos_start

        if self.current_token.type != TT_LSQUARE:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "अपेक्षितं '[' | apekchhit '['",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_token.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            list_element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ] | apekchhit INT,FLOAT,+,-,parichayakah athva (",
                    )
                )
            while self.current_token.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                list_element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res
            if self.current_token.type != TT_RSQUARE:
                return res.failure(
                    Expected_Char_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "apekchhit ',' or ')'",
                    )
                )
            res.register_advancement()
            self.advance()
        return res.success(
            ListNode(list_element_nodes, pos_start, self.current_token.pos_end.copy())
        )

    def atom(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))
        if tok.type in (TT_STRING_S, TT_STRING_D):
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_token.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं ')' | apekchhit ')'",
                    )
                )
        elif tok.matches(TT_KEYWORD, "yadi"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)
        elif tok.matches(TT_KEYWORD, "kRRite") or tok.matches(TT_KEYWORD, "krrite"):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "Invalid for-loop syntax",
                    )
                )
            return res.success(for_expr)
        elif tok.matches(TT_KEYWORD, "sopAnaH") or tok.matches(TT_KEYWORD, "sopanah"):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)
        elif tok.matches(TT_KEYWORD, "niyoga"):
            func_expr = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_expr)
        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        return res.failure(
            Invalid_Syntax_Error(
                tok.pos_start,
                tok.pos_end,
                "अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit INT,FLOAT,+,-,parichayakah athva (",
            )
        )

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_token
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()
        if self.current_token.matches(TT_KEYWORD, "nahi"):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))
        node = res.register(
            self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE))
        )
        if res.error:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit INT,FLOAT,+,-,nahi parichayakah athva (",
                )
            )
        return res.success(node)

    def expr(self):
        res = ParseResult()
        if self.current_token.matches(
            TT_KEYWORD, "charaH"
        ) or self.current_token.matches(TT_KEYWORD, "charah"):
            res.register_advancement()
            self.advance()
            if self.current_token.type != TT_IDENTIFIER:
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं परिचयकः | apekchhit parichayakah",
                    )
                )
            var_name = self.current_token
            res.register_advancement()
            self.advance()
            if self.current_token.type != TT_EQ:
                return res.failure(
                    Invalid_Syntax_Error(
                        self.current_token.pos_start,
                        self.current_token.pos_end,
                        "अपेक्षितं '=' | apekchhit '=",
                    )
                )
            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))
        node = res.register(
            self.bin_op(
                self.comp_expr,
                (
                    (TT_KEYWORD, "tathA"),
                    (TT_KEYWORD, "tatha"),
                    (TT_KEYWORD, "vA"),
                    (TT_KEYWORD, "va"),
                ),
            )
        )
        if res.error:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "अपेक्षितं INT,FLOAT,+,-,परिचयकः अथवा ( | apekchhit charah ,INT,FLOAT,+,-,nahi,parichayakah athva (",
                )
            )
        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        res = ParseResult()
        if func_b == None:
            func_b = func_a
        left = res.register(func_a())

        if res.error:
            return res.failure(
                Invalid_Syntax_Error(
                    self.current_token.pos_start,
                    self.current_token.pos_end,
                    "Invalid binary operation",
                )
            )
        # self.advance()
        while (
            self.current_token.type in ops
            or (self.current_token.type, self.current_token.value) in ops
        ):
            op_tok = self.current_token
            res.register_advancement()
            self.advance()
            right = res.register(func_b())

            if res.error:
                return res
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)


# Runtime Result
class RTresult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):

        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        self.reset()
        self.value = value
        return self

    def succes_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        self.reset()
        self.error = error
        return self

    def should_return(self):
        return (
            self.error
            or self.func_return_value
            or self.loop_should_continue
            or self.loop_should_break
        )


# Values
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subtracted_from(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def divided_by(self, other):
        return None, self.illegal_operation(other)

    def to_power(self, other):
        return None, self.illegal_operation(other)

    def get_comp_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comp_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comp_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comp_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comp_gte(self, other):
        return None, self.illegal_operation(other)

    def get_comp_lte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def is_true(self):
        return False

    def execute(self, args):
        return RTresult().failure(self.illegal_operation())

    def copy(self):
        raise Exception("No copy method defined")

    def illegal_operation(self, other=None):
        if not other:
            other = self
            return RTError(
                self.pos_start, self.pos_end, "अवैध क्रिया | avaidh kriya", self.context
            )


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def added_to(self, other):
        newlist = self.copy()
        newlist.elements.append(other)
        return newlist, None

    def subtracted_from(self, other):
        if isinstance(other, Number):
            newlist = self.copy()
            try:
                newlist.elements.pop(other.value)
                return newlist, None
            except:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "अवैध स्थानम् | avaidh sthanam",
                    self.context,
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            newlist = self.copy()
            newlist.elements.append(other)
            return newlist, None
        elif isinstance(other, List):
            list_1 = self.copy()
            list_2 = other.copy()
            length_1 = len(list_1.elements)
            length_2 = len(list_2.elements)
            newlist = []
            max_len = max(length_1, length_2)
            print(max_len)


            list_1.elements += [Number(0)] * (max_len - length_1)
            list_2.elements += [Number(0)] * (max_len - length_2)
            for i in range(max_len):
                elem1 = list_1.elements[i]
                elem2 = list_2.elements[i]
                product, error = elem1.multiplied_by(elem2)
                if error:
                    return None, error
                newlist.append(product)
            return List(newlist), None
                
        else:
            return None, Value.illegal_operation(self, other)

    def divided_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "अवैध स्थानम् | avaidh sthanam",
                    self.context,
                )
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elements])}]'


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subtracted_from(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def to_power(self, other):
        if isinstance(other, Number):
            return Number(self.value**other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start,
                    other.pos_end,
                    "शून्येन विभागः | shunyen vibhagah",
                    self.context,
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_eq(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value == other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_ne(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value != other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_gte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value >= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comp_lte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value <= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value and other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value or other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(int(1 if self.value == 0 else 0)).set_context(self.context), None

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_pi = Number(math.pi)


class String(Value):
    def __init__(self, value, type):
        super().__init__()
        self.value = value
        self.type = type

    def added_to(self, other):
        if isinstance(other, String):
            return (
                String(self.value + str(other.value), TT_STRING_D).set_context(
                    self.context
                ),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def multiplied_by(self, other):
        if isinstance(other, Number):
            return (
                String(self.value * other.value, TT_STRING_D).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value, TT_STRING_D)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        if self.value == "":
            return "''"
        elif self.type == TT_STRING_S:
            return f"'{self.value}'"
        elif self.type == TT_STRING_D:
            return f'"{self.value}"'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<अज्ञातम्>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTresult()
        if len(args) > len(arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(arg_names)} अधिक प्राप्ताः | {len(args) - len(arg_names)} adhik praptaah",
                    self.context,
                )
            )
        if len(args) < len(arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(arg_names) - len(args)} अभावाः | {len(arg_names) - len(args)} abhavah",
                    self.context,
                )
            )
        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTresult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RTresult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res
        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res

        ret_value = (
            (value if self.should_auto_return else None)
            or res.func_return_value
            or Number.null
        )
        return res.success(ret_value)

    def copy(self):
        copy = Function(
            self.name, self.body_node, self.arg_names, self.should_auto_return
        )
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"


class BuiltinFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTresult()
        exec_ctx = self.generate_new_context()
        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)
        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        return_value = res.register(method(exec_ctx))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit_method(self, args, exec_ctx):
        raise Exception(f"No execute_{self.name} method defined")

    def copy(self):
        copy = BuiltinFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RTresult().success(Number.null)

    execute_print.arg_names = ["value"]

    def execute_print_rt(self, exec_ctx):
        return RTresult().success(
            String(str(exec_ctx.symbol_table.get("value")), TT_STRING_D)
        )

    execute_print_rt.arg_names = ["value"]

    def execute_input(self, exec_ctx):
        text = input()
        return RTresult().success(String(text, TT_STRING_D))

    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        text = input()
        while True:
            try:
                number = int(text)
                break
            except ValueError:
                return RTresult().failure(
                    RTError(
                        self.pos_start,
                        self.pos_end,
                        "अवैध अंकः | avaidh ankah",
                        self.context,
                    )
                )
        return RTresult().success(Number(number))

    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system("cls" if os.name == "nt" else "clear")
        return RTresult().success(Number.null)

    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTresult().success(Number(int(is_number)))

    execute_is_number.arg_names = ["value"]

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTresult().success(Number(int(is_string)))

    execute_is_string.arg_names = ["value"]

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return RTresult().success(Number(int(is_list)))

    execute_is_list.arg_names = ["value"]

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTresult().success(Number(int(is_function)))

    execute_is_function.arg_names = ["value"]

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")
        if not isinstance(list_, List):
            return RTresult().failure(
                RTError(
                    self.pos_start, self.pos_end, "अवैध सूची | avaidh suchi", self.context
                )
            )
        list_.elements.append(value)
        return RTresult().success(Number.null)

    execute_append.arg_names = ["list", "value"]

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")
        if not isinstance(list_, List):
            return RTresult().failure(
                RTError(
                    self.pos_start, self.pos_end, "अवैध सूची | avaidh suchi", self.context
                )
            )
        if not isinstance(index, Number):
            return RTresult().failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "अवैध स्थानम् | avaidh sthanam",
                    self.context,
                )
            )
        try:
            element = list_.elements.pop(index.value)
        except:
            return RTresult().failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "अवैध स्थानम् | avaidh sthanam",
                    self.context,
                )
            )
        return RTresult().success(element)

    execute_pop.arg_names = ["list", "index"]

    def execute_extend(self, exec_ctx):
        list1 = exec_ctx.symbol_table.get("list1")
        list2 = exec_ctx.symbol_table.get("list2")
        if not isinstance(list1, List) or not isinstance(list2, List):
            return RTresult().failure(
                RTError(
                    self.pos_start, self.pos_end, "अवैध सूची | avaidh suchi", self.context
                )
            )
        list1.elements.extend(list2.elements)
        return RTresult().success(Number.null)

    execute_extend.arg_names = ["list1", "list2"]
    def execute_run(self,exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        if not isinstance(list_, List):
            return RTresult().failure(
                RTError(self.pos_start, self.pos_end, "अवैध सूची | avaidh suchi", self.context)
            )
        return RTresult().success(Number(len(list_.elements)))
    execute_run.arg_names = ["list"]
    def execute_run(self,exec_ctx):
        fn = exec_ctx.symbol_table.get("fn")
        if not isinstance(fn, String):
            return RTresult().failure(
                RTError(self.pos_start, self.pos_end, "अवैध स्थानम् | avaidh sthanam", self.context)
            )
        fn = fn.value
        try:
            with open(fn, "r",encoding= 'utf8') as f:
                script = f.read()
        except Exception as e:
            return RTresult().failure(
                RTError(self.pos_start, self.pos_end, f"अवैध फ़ाइलः {e}", self.context)
            )
        _ , error = Run(script,fn)
        if error:
            return RTresult().failure(
                RTError(self.pos_start, self.pos_end, f"अवैध फ़ाइलः {error}", self.context)
            )
        return RTresult().success(Number.null)
    execute_run.arg_names = ["fn"]


BuiltinFunction.print = BuiltinFunction("print")
BuiltinFunction.print_rt = BuiltinFunction("print_rt")
BuiltinFunction.input = BuiltinFunction("input")
BuiltinFunction.input_int = BuiltinFunction("input_int")
BuiltinFunction.clear = BuiltinFunction("clear")
BuiltinFunction.is_number = BuiltinFunction("is_number")
BuiltinFunction.is_string = BuiltinFunction("is_string")
BuiltinFunction.is_list = BuiltinFunction("is_list")
BuiltinFunction.is_function = BuiltinFunction("is_function")
BuiltinFunction.append = BuiltinFunction("append")
BuiltinFunction.pop = BuiltinFunction("pop")
BuiltinFunction.extend = BuiltinFunction("extend")
BuiltinFunction.len = BuiltinFunction("len")
BuiltinFunction.run = BuiltinFunction("run")

# Context
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


# Symbol Table
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


# Interpreter
class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_ifNode(self, node, context):
        res = RTresult()
        i = 0
        for condition, expr, should_return_null in node.cases:
            i += 1

            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(Number.null if should_return_null else expr_value)
        if node.else_case:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(Number.null if should_return_null else else_value)
        return res.success(Number.null)

    def visit_ForNode(self, node, context):
        res = RTresult()
        elements = []
        start_value = res.register(self.visit(node.start_value_node, context))
        if res.should_return():
            return res
        end_value = res.register(self.visit(node.end_value_node, context))
        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.should_return():
                return res
        else:
            step_value = Number(1)
        i = start_value.value
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value
        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value
            value = res.register(self.visit(node.body_node, context))
            if (
                res.should_return()
                and res.loop_should_continue == False
                and res.loop_should_break == False
            ):
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(
            Number.null
            if node.should_return_null
            else List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_WhileNode(self, node, context):
        res = RTresult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res
            if not condition.is_true():
                break
            value = res.register(self.visit(node.body_node, context))
            if (
                res.should_return()
                and res.loop_should_continue == False
                and res.loop_should_break == False
            ):
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)
        return res.success(
            Number.null
            if node.should_return_null
            else List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context):
        res = RTresult()
        elements = []
        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return():
                return res
        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        res = RTresult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(
                RTError(
                    node.pos_start,
                    node.pos_end,
                    f"'{var_name}' न विवक्षितम् | {var_name} na vivakshitam",
                    context,
                )
            )
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTresult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_NumberNode(self, node, context):
        return RTresult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RTresult().success(
            String(node.tok.value, node.tok.type)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_BinaryOpNode(self, node, context):
        res = RTresult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return():
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
            return res

        result, error = None, None
        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subtracted_from(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multiplied_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.to_power(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comp_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comp_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comp_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comp_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comp_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comp_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, "tatha", "tathA"):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, "va", "vA"):
            result, error = left.ored_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTresult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res
        error = None
        if node.op_tok.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, "nahi"):
            number, error = number.notted()
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_FuncDefNode(self, node, context):
        res = RTresult()
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_names.value for arg_names in node.arg_name_tok]
        func_value = (
            Function(func_name, body_node, arg_names, node.should_auto_return)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTresult()

        args = []
        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)
        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res
        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        return_value = (
            return_value.copy()
            .set_pos(node.pos_start, node.pos_end)
            .set_context(context)
        )
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTresult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = Number.null
        return res.succes_return(value)

    def visit_ContinueNode(self, node, context):
        return RTresult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTresult().success_break()


global_symbol_table = SymbolTable()
global_symbol_table.set("shUnya", Number.null)
global_symbol_table.set("satya", Number.true)
global_symbol_table.set("asatya", Number.false)
global_symbol_table.set("pi", Number.math_pi)
global_symbol_table.set("mudrayati", BuiltinFunction.print)
global_symbol_table.set("mudrayati_punaH", BuiltinFunction.print_rt)
global_symbol_table.set("praveshaH", BuiltinFunction.input)
global_symbol_table.set("aMka_praveshaH", BuiltinFunction.input_int)
global_symbol_table.set("shuddha", BuiltinFunction.clear)
global_symbol_table.set("shuddha", BuiltinFunction.clear)
global_symbol_table.set("aMkaH_vA", BuiltinFunction.is_number)
global_symbol_table.set("sUtram_vA", BuiltinFunction.is_string)
global_symbol_table.set("sUchiH_vA", BuiltinFunction.is_list)
global_symbol_table.set("kAryaH_vA", BuiltinFunction.is_function)
global_symbol_table.set("saMyojayati", BuiltinFunction.append)
global_symbol_table.set("apanayati", BuiltinFunction.pop)
global_symbol_table.set("prasArayati", BuiltinFunction.extend)
global_symbol_table.set("parimANam", BuiltinFunction.len)
global_symbol_table.set("dhAvayati", BuiltinFunction.run)
global_symbol_table.set("shunya", Number.null)
global_symbol_table.set("satya", Number.true)
global_symbol_table.set("asatya", Number.false)
global_symbol_table.set("pi", Number.math_pi)
global_symbol_table.set("mudrayati", BuiltinFunction.print)
global_symbol_table.set("mudrayati_punah", BuiltinFunction.print_rt)
global_symbol_table.set("praveshah", BuiltinFunction.input)
global_symbol_table.set("anka_praveshah", BuiltinFunction.input_int)
global_symbol_table.set("shuddha", BuiltinFunction.clear)
global_symbol_table.set("shuddha", BuiltinFunction.clear)
global_symbol_table.set("ankah_va", BuiltinFunction.is_number)
global_symbol_table.set("sutram_va", BuiltinFunction.is_string)
global_symbol_table.set("suchih_va", BuiltinFunction.is_list)
global_symbol_table.set("karyah_va", BuiltinFunction.is_function)
global_symbol_table.set("samyojayati", BuiltinFunction.append)
global_symbol_table.set("apanayati", BuiltinFunction.pop)
global_symbol_table.set("prasarayati", BuiltinFunction.extend)
global_symbol_table.set("parimanam", BuiltinFunction.len)
global_symbol_table.set("dhavayati", BuiltinFunction.run)


# Run
def Run(text, file_name):
    converted_text = str(transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS))
    lexer = Lexer(file_name, converted_text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error
    interpreter = Interpreter()
    context = Context("<कार्यक्रम> | <karyakram>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error
