from parser.annoying_char import annoying_guys_cleaner


class TokenType:
    NEWLINE     = 0
    BREAK       = 1
    CONTINUE    = 2
    ELSE        = 3
    FOR         = 4
    IF          = 5
    ELIF        = 6
    RETURN      = 7
    VOID        = 8
    WHILE       = 9
    # operators
    PLUS        = 10
    MINUS       = 11
    MULT        = 12
    DIV         = 13
    NOT         = 14
    NOTEQ       = 15
    EQ          = 16
    EQEQ        = 17
    LT          = 18
    LTEQ        = 19
    GT          = 20
    GTEQ        = 21
    ANDAND      = 22
    OROR        = 23
    # separators
    LCURLY      = 24
    RCURLY      = 25
    LPAREN      = 26
    RPAREN      = 27
    LBRACKET    = 28
    RBRACKET    = 29
    COLON       = 30
    SEMICOLON   = 31
    COMMA       = 32
    # identifiers
    NAME        = 33
    # literals
    INTLITERAL     = 34
    FLOATLITERAL   = 35
    NUMBER         = 36
    BOOLEANLITERAL = 37
    STRINGLITERAL  = 38
    TEXTLITERAL    = 39
    # special tokens...
    ERROR       = 40
    EOF         = 41
    # other
    ENTITY      = 42 # $entity
    PRINT       = 43 # =a -> print a
    AND         = 44
    OR          = 45
    IN          = 46
    END         = 47
    NOTATION    = 48
    SELFPLUS    = 49
    SELFMINUS   = 50
    BOOLEAN     = 51
    INDENT      = 52
    MOD         = 53


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
    def __init__(self, line_start:int, line_finish:int, char_start:int, char_finish:int):
        self.line_start = line_start
        self.line_finish = line_finish
        self.char_start = char_start
        self.char_finish = char_finish

    def __str__(self):
        return f'{self.line_start}({self.char_start})...{self.line_finish}({self.char_finish})'

    def snapshot(self, offset=0) -> tuple:
        if offset == -1:
            return (self.line_finish, self.char_finish, self.line_finish, self.char_finish)
        else:
            return (self.line_start, self.char_start, self.line_finish, self.char_finish - offset)


class Token:
    first_reserved = TokenType.NEWLINE
    last_reversed = TokenType.WHILE

    def __init__(self, type:int, spelling:str, position:tuple):
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
    def __init__(self, file_name:str):
        self.eof = '_EOF'
        # In Python3.*, for using file pointer seek(), the file MUST be
        # opened as a binary file with mode `b`
        self.reader = open(file_name, 'rb')

    def next_char(self):
        char = self.reader.read(1)
        if char == b'\xe2' or char == b'\xc3':
            annoying_guy = char
            annoying_guy += self.look_ahead(1, annoying=True)
            annoying_guy += self.look_ahead(2, annoying=True)
            self.move_ahead(2, annoying=True)
            char = annoying_guys_cleaner(annoying_guy)
            return char
        if not char:
            return self.eof
        return char.decode('utf-8')

    def look_ahead(self, nth:int, annoying=False):
        # anchor file pointer's original location on function call
        seek_offset = 0 - nth
        char = ''
        while nth > 0:
            char = self.reader.read(1)
            nth -= 1
            if not char:
                return self.eof
        # rollback the file pointer to the original location
        self.reader.seek(seek_offset, 1)
        if annoying or char == b'\xe2' or char == b'\xc3':
            return char
        else:
            return char.decode('utf-8')

    def move_ahead(self, nth:int, annoying=False):
        char = ''
        while nth > 0:
            char = self.reader.read(1)
            nth -= 1
            if not char:
                char = self.eof
                return char

        if not annoying:
            if char == b'\xe2' or char == b'\xc3':
                annoying_guy = char
                annoying_guy += self.look_ahead(1, annoying=True)
                annoying_guy += self.look_ahead(2, annoying=True)
                self.move_ahead(2, annoying=True)
                char = annoying_guys_cleaner(annoying_guy)
                return char
            else:
                return char.decode('utf-8')
