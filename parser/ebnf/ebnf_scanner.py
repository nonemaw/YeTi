import re
from parser.token_source import PositionTracker, SourceFile
from parser.ebnf.errors import TokenTypeError


class TokenType:
    NEWLINE = 0
    STAR = 1
    PLUS = 2
    ALT = 3
    EXCEP = 4
    LREP = 5
    RREP = 6
    LGR = 7
    RGR = 8
    LOP = 9
    ROP = 10
    DEF = 11
    NAME = 12
    STRING = 13
    EOF = 14
    ERROR = 15
    NUMBER = 16

    keywords = [
        '<NEWLINE>',
        '<STAR>',
        '<PLUS>',
        '<ALT>',
        '<EXCEP>',
        '<LREP>',
        '<RREP>',
        '<LGR>',
        '<RGP>',
        '<LOP>',
        '<ROP>',
        '<DEF>',
        '<NAME>',
        '<STRING>',
        '_EOF',
        '<ERROR>',
        '<NUMBER>'
    ]


class Token:
    first_reserved = TokenType.NEWLINE
    last_reversed = TokenType.DEF

    def __init__(self, type: int, spelling: str, position: tuple):
        """
        position: (line_start, spelling_start, line_end, spelling_end)
        """
        if type == TokenType.NAME:
            current_type = self.first_reserved
            while True:
                if TokenType.keywords[current_type] == spelling:
                    self.type = current_type
                    break
                elif current_type == self.last_reversed:
                    self.type = TokenType.NAME
                    break
                else:
                    current_type += 1
        else:
            self.type = type

        self.spelling = spelling
        self.position = position

    def __str__(self):
        return f'TYPE=[{self.type} {self.name(self.type)}], SPELLING=<{repr(self.spelling)}>, POSITION={self.position[0]}[{self.position[1]}]..{self.position[2]}[{self.position[3]}]'

    def __repr__(self):
        return f'TYPE={self.name(self.type)} SPELLING={repr(self.spelling)}'

    def name(self, type: int) -> str:
        if type is None:
            raise TokenTypeError(
                f'Unknown token in source code at position line {self.position[0]}[{self.position[1]}]')
        return TokenType.keywords[type]

    def position_snapshot(self) -> tuple:
        return self.position


class EBNFScanner:
    escape_char = ['b', 'f', 'n', 'r', 't', "'", '"', '\\']
    id_string_begin = re.compile(r'[a-zA-Z_\u4e00-\u9fa5]{1}')
    id_string_rest = re.compile(r'[a-zA-Z0-9_\u4e00-\u9fa5]+')
    digit = re.compile(r'[0-9]+')

    def __init__(self, source_file: SourceFile, comment_tag='#'):
        self.source_file = source_file
        self.tracker = PositionTracker(1, 1, 1, 1)
        self.option_lock = None

        self.prev_char = ''
        self.current_char = self.source_file.next_char()
        self.current_spelling = ''

        self.text = ''
        self.comment_tag = comment_tag

    def accept(self, count: int = None):
        """
        consume current character and add it to token spelling

        remember previous character, and move file pointer to next char & update position
        """
        if count:
            while count > 0:
                self.current_spelling += self.current_char
                self.prev_char = self.current_char
                self.current_char = self.source_file.next_char()
                self.tracker.char_finish += 1
                count -= 1
        else:
            self.current_spelling += self.current_char
            self.prev_char = self.current_char
            self.current_char = self.source_file.next_char()
            self.tracker.char_finish += 1

    def look_ahead(self, nth: int):
        return self.source_file.look_ahead(nth)

    def move_ahead(self, nth: int):
        self.prev_char = self.current_char
        self.current_char = self.source_file.move_ahead(nth)

    def get_token_type(self):
        """
        continue scan input from one character until get & return a token
        """
        if self.option_lock:
            # translate option `[ expr ]` into `( expr ){0, 1}`
            if self.current_char == '_OPTION':
                self.current_char = '{'
                self.current_spelling = '{'
                return TokenType.LREP
            elif self.current_char == '{':
                self.current_char = '0'
                self.current_spelling = '0'
                return TokenType.NUMBER
            elif self.current_char == '0':
                self.current_char = '1'
                self.current_spelling = '1'
                return TokenType.NUMBER
            elif self.current_char == '1':
                self.current_char = '}'
                self.current_spelling = '}'
                return TokenType.RREP
            elif self.current_char == '}':
                self.current_char = self.option_lock
                self.option_lock = None
                self.skip_space_comments()

        if self.current_char == '*':
            self.accept()
            return TokenType.STAR
        elif self.current_char == '+':
            self.accept()
            return TokenType.PLUS
        elif self.current_char == '|':
            self.accept()
            return TokenType.ALT
        elif self.current_char == '-':
            self.accept()
            return TokenType.EXCEP
        elif self.current_char == '{':
            self.accept()
            return TokenType.LREP
        elif self.current_char == '}':
            self.accept()
            return TokenType.RREP
        elif self.current_char == '(' or self.current_char == '[':
            self.current_char = '('
            self.accept()
            return TokenType.LGR
        elif self.current_char == ')' or self.current_char == ']':
            if self.current_char == ']':
                self.current_char = ')'
                self.accept()
                # work as current char's cache
                self.option_lock = self.current_char
                self.current_char = '_OPTION'
            else:
                self.accept()
            return TokenType.RGR
        elif self.current_char == ':' and self.look_ahead(
                1) == ':' and self.look_ahead(2) == '=':
            self.accept(3)
            return TokenType.DEF

        # newline
        elif self.current_char == '\r' or self.current_char == '\n':
            # consume \r or \n
            self.accept()
            if self.current_char == '\n' and self.prev_char == '\r':
                # move over \n if former char is \r
                self.move_ahead(1)
            self.tracker.char_start, self.tracker.char_finish = 1, 1
            self.tracker.line_finish += 1
            self.tracker.line_start = self.tracker.line_finish
            return TokenType.NEWLINE

        # number
        elif self.digit.findall(self.current_char):
            self.accept()
            while self.digit.findall(
                    self.current_char) and self.current_char != self.source_file.eof:
                self.accept()
            return TokenType.NUMBER

        # literals, string
        elif self.current_char == '"' or self.current_char == "'":
            quotation = self.current_char
            self.accept()  # eat '"'
            while self.current_char != quotation:
                if self.current_char == '\n' or self.current_char == '\r' or self.current_char == self.source_file.eof:
                    # ERROR: unterminated string
                    return TokenType.STRING
                elif self.current_char == '\\':
                    # an escape: 'A\t' will be read as 'A', '\\', 't'
                    # jump over escape, make current_char as the actually char
                    self.current_char = self.source_file.next_char()
                    self.current_char = self.make_escape(self.current_char)
                self.accept()
            self.accept()  # eat '"'
            return TokenType.STRING

        # NAME
        elif self.current_char != self.source_file.eof and self.id_string_begin.findall(
                self.current_char):
            self.accept()
            while self.current_char != self.source_file.eof and self.id_string_rest.findall(
                    self.current_char):
                self.accept()
            return TokenType.NAME

        # unknown token case, it will raise exception
        else:
            self.accept()
            return None

    def make_escape(self, char: str):
        self.tracker.char_finish += 1
        if char == 'b':
            return '\b'
        elif char == 'r':
            return '\r'
        elif char == 'n':
            return '\n'
        elif char == 't':
            return '\t'
        elif char == 'f':
            return '\f'
        elif char == '\'':
            return '\''
        elif char == '"':
            return '\"'
        elif char == '\\':
            return '\\\\'
        else:
            return '\\' + char

    def skip_space_comments(self):
        """
        jump over spaces, comma and comment
        """
        while self.current_char == ' ' or self.current_char == '	' or self.current_char == ',':
            if self.current_char == '	':
                self.tracker.char_finish += 3
            else:
                self.tracker.char_finish += 1
            self.move_ahead(1)

        # jump over comments
        if self.current_char == self.comment_tag:
            while True:
                self.move_ahead(1)
                self.tracker.char_finish += 1
                if self.current_char == '\n' or self.current_char == '\r' or self.current_char == self.source_file.eof:
                    break

    def get_token(self) -> Token:
        """
        return a token instance on each time it being called (token = scanner_instance.get_token())
        until it reaches to EOF of input file
        """
        while self.current_char != self.source_file.eof:
            self.skip_space_comments()
            if self.current_char == self.source_file.eof:
                break
            self.current_spelling = ''
            self.tracker.char_start = self.tracker.char_finish
            return self.build_token(self.get_token_type())

    def build_token(self, token_type: int = None, text: str = None) -> Token:
        """
        build and return a token based on token type and a possible text
        """
        if token_type is not None:
            if not text:
                # normal tokens
                # `offset=1`: as char_finish is right behind current token's end location hence a minus is needed
                if token_type == TokenType.NEWLINE:
                    token = Token(token_type, '\n', self.tracker.snapshot())
                elif self.current_spelling == '\'\n\'' or self.current_spelling == '\"\n\"':
                    token = Token(token_type, r"'\n'",
                                  self.tracker.snapshot(offset=1))
                else:
                    token = Token(token_type, self.current_spelling,
                                  self.tracker.snapshot(offset=1))
            else:
                # eof token, reserved
                token = Token(token_type, text, self.tracker.snapshot())
            return token


"""
RUN THIS FOR DEBUG ONLY:
PUT `grammar.txt` WITH THIS FILE UNDER SAME DIRECTORY FOR TEST
"""
if __name__ == '__main__':
    import os

    this_path = os.path.dirname(os.path.realpath(__file__))
    scanner = EBNFScanner(SourceFile(os.path.join(this_path, 'grammar.ebnf')))

    while scanner.current_char != scanner.source_file.eof:
        token = scanner.get_token()
        print(token)
