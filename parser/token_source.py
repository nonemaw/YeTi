from annoying_char import annoying_guys_cleaner


class TokenType:
    NEWLINE = 0
    BREAK = 1
    CONTINUE = 2
    ELSE = 3
    FOR = 4
    IF = 5
    ELIF = 6
    RETURN = 7
    VOID = 8
    WHILE = 9
    # operators
    PLUS = 10
    MINUS = 11
    MULT = 12
    DIV = 13
    NOT = 14
    NOTEQ = 15
    EQ = 16
    EQEQ = 17
    LT = 18
    LTEQ = 19
    GT = 20
    GTEQ = 21
    ANDAND = 22
    OROR = 23
    # separators
    LCURLY = 24
    RCURLY = 25
    LPAREN = 26
    RPAREN = 27
    LBRACKET = 28
    RBRACKET = 29
    COLON = 30
    SEMICOLON = 31
    COMMA = 32
    # identifiers
    NAME = 33
    # literals
    INTLITERAL = 34
    FLOATLITERAL = 35
    NUMBER = 36
    BOOLEANLITERAL = 37
    STRINGLITERAL = 38
    TEXTLITERAL = 39
    # special tokens...
    ERROR = 40
    EOF = 41
    # other
    ENTITY = 42  # $entity
    PRINT = 43  # =a -> print a
    AND = 44
    OR = 45
    IN = 46
    END = 47
    NOTATION = 48
    SELFPLUS = 49
    SELFMINUS = 50
    BOOLEAN = 51
    INDENT = 52
    MOD = 53

    keywords = [
        '<newline>',
        'break',
        'continue',
        'else',
        'for',
        'if',
        'elif',
        'return',
        'void',
        'while',
        '+',
        '-',
        '*',
        '/',
        'not',
        '!=',
        '=',
        '==',
        '<',
        '<=',
        '>',
        '>=',
        '&&',
        '||',
        '{',
        '}',
        '(',
        ')',
        '[',
        ']',
        ':',
        ';',
        ',',
        '<name>',
        '<int-literal>',
        '<float-literal>',
        '<number-literal>',
        '<boolean-literal>',
        '<string-literal>',
        '<text-literal>',
        '<error>',
        '_EOF',
        '$',
        'print',
        'and',
        'or',
        'in',
        'end',
        '.',
        '+=',
        '-=',
        'boolean',
        '<indent>',
        '%',
    ]


class PositionTracker:
    """
    meta class for tracking position of current token's spelling in file

    a snap shot will be created and stored when creating token
    """

    def __init__(self, line_start: int, line_finish: int, char_start: int,
                 char_finish: int):
        self.line_start = line_start
        self.line_finish = line_finish
        self.char_start = char_start
        self.char_finish = char_finish

    def __str__(self):
        return f'{self.line_start}({self.char_start})...{self.line_finish}({self.char_finish})'

    def snapshot(self, offset=0) -> tuple:
        if offset == -1:
            return (self.line_finish, self.char_finish, self.line_finish,
                    self.char_finish)
        else:
            return (self.line_start, self.char_start, self.line_finish,
                    self.char_finish - offset)


class Token:
    first_reserved = TokenType.NEWLINE
    last_reversed = TokenType.WHILE

    def __init__(self, type: int, spelling: str, position: tuple):
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
        return f'TYPE=[{self.type} {self.spell()}], SPELLING=<{repr(self.spelling)}>, POSITION={self.position[0]}[{self.position[1]}]..{self.position[2]}[{self.position[3]}]'

    def __repr__(self):
        return f'TYPE={self.spell()} SPELLING={repr(self.spelling)}'

    def spell(self) -> str:
        return TokenType.keywords[self.type]

    def print_position(self) -> str:
        return f'{self.position[0]}({self.position[1]})...{self.position[2]}({self.position[3]})'

    def position_snapshot(self) -> tuple:
        return self.position


class SourceFile:
    def __init__(self, source_file: str = None, source_code: str = None):
        self.eof = '_EOF'
        # In Python3.*, for using file pointer seek(), the file MUST be
        # opened as a binary file with mode `b`
        self.source_file = open(source_file, 'rb') if source_file else None
        self.source_code = source_code if source_code else None
        self.index = 0 if source_code else None

        if not self.source_file and not self.source_code:
            raise Exception('No code has been provided')

        # if both file and code is provided, later one will be ignored
        if self.source_file and self.source_code:
            self.source_code = None
            self.index = None

    def next_char(self):
        char = None
        if self.source_file:
            char = self.source_file.read(1)
        elif self.source_code and self.index < len(self.source_code):
            char = self.source_code[self.index].encode()
            self.index += 1

        if not char:
            return self.eof

        if b'\xe2' in char or b'\xc3' in char:

            print(char)

            if len(char) == 1:
                annoying_guy = char
                annoying_guy += self.look_ahead(1, annoying=True)
                annoying_guy += self.look_ahead(2, annoying=True)
                self.move_ahead(2, annoying=True)
                return annoying_guys_cleaner(annoying_guy)
            elif len(char) == 3:
                return annoying_guys_cleaner(char)

        return char.decode('utf-8')

    def look_ahead(self, nth: int, annoying=False):
        # anchor file pointer's original location on function call
        char = None

        if self.source_file:
            seek_offset = -nth
            while nth > 0:
                char = self.source_file.read(1)
                nth -= 1
                if not char:
                    return self.eof
            # rollback the file pointer to the original location
            self.source_file.seek(seek_offset, 1)

        elif self.source_code:
            nth = self.index + nth - 1
            if nth < len(self.source_code):
                char = self.source_code[nth]
            else:
                return self.eof

        if annoying or b'\xe2' in char or b'\xc3' in char:
            return char
        else:
            return char.decode('utf-8')

    def move_ahead(self, nth: int, annoying=False):
        char = None

        if self.source_file:
            while nth > 0:
                char = self.source_file.read(1)
                nth -= 1
                if not char:
                    return self.eof

        elif self.source_code:
            nth = self.index + nth - 1
            if nth < len(self.source_code):
                char = self.source_code[nth]
            else:
                return self.eof

        if not annoying:
            if b'\xe2' in char or b'\xc3' in char:
                if len(char) == 1:
                    annoying_guy = char
                    annoying_guy += self.look_ahead(1, annoying=True)
                    annoying_guy += self.look_ahead(2, annoying=True)
                    self.move_ahead(2, annoying=True)
                    return annoying_guys_cleaner(annoying_guy)
                elif len(char) == 3:
                    return annoying_guys_cleaner(char)
            else:
                return char.decode('utf-8')
