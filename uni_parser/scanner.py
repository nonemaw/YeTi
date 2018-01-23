import re
from uni_parser.base_class import ScannerBase
from uni_parser.token_source import *
from uni_parser.ebnf.errors import TokenTypeError


class Scanner(ScannerBase):
    escape_char = ['b', 'f', 'n', 'r', 't', "'", '"', '\\']
    id_string_begin = re.compile(r'[a-zA-Z_\u4e00-\u9fa5\$]{1}')
    id_string_rest = re.compile(r'[a-zA-Z0-9_\u4e00-\u9fa5\$]+')
    digit = re.compile(r'[0-9]+')

    def __init__(self,
                 source_file: SourceFile,
                 comment_tag: str = '#',
                 template_tag: str = None,
                 var_define: str = None,
                 end_tag: list = None):
        """
        template_tag: tag for template code section, e.g.: template_tag='<::>'
        """
        super().__init__(source_file, comment_tag)
        self.tracker = PositionTracker(1, 1, 1, 1)
        self.debug = False

        self.prev_char = ''
        self.prev_token_type = None
        self.current_char = self.source_file.next_char()
        self.current_spelling = ''

        self.text = ''
        self.code_flag = False
        self.if_for_flag = False
        self.print_flag = False
        self.text_line_flag = False

        # for detect tag closure
        # TODO: temporary solution
        self.tag_stack = []

        self.var_define = var_define
        self.end_tag = end_tag
        if template_tag:
            self.template_tag = template_tag[:int(len(template_tag) / 2)]
            self.template_close = template_tag[int(len(template_tag) / 2):]
        else:
            self.template_tag = None
            self.template_close = None
            self.code_flag = True

    def accept(self, count: int = None, word: str = None, l_cap: bool = False):
        """
        consume current character and add it to token spelling

        remember previous character, and move file pointer to next char &
        update position
        """
        times = 0
        if count and count > 0 and not word:
            times = count
        elif word and not count:
            times = len(word)
        else:
            self.current_spelling += self.current_char.lower() \
                if l_cap else self.current_char
            self.prev_char = self.current_char
            self.current_char = self.source_file.next_char()
            self.tracker.char_finish += 1

        if times:
            while times > 0:
                self.current_spelling += self.current_char.lower() \
                    if l_cap else self.current_char
                self.prev_char = self.current_char
                self.current_char = self.source_file.next_char()
                self.tracker.char_finish += 1
                times -= 1

    def look_ahead(self, nth: int):
        return self.source_file.look_ahead(nth)

    def move_ahead(self, nth: int):
        self.prev_char = self.current_char
        self.current_char = self.source_file.move_ahead(nth)

    def enable_debug(self):
        self.debug = True

    def disable_debug(self):
        self.debug = False

    def get_token_type(self, indent=4):
        """
        continue scan input from one character until get & return a token
        """
        # newline, only process when template is not activated
        if not self.template_tag:
            if self.current_char == '\r' or self.current_char == '\n':
                # consume \r or \n
                self.accept()
                if self.current_char == '\n' and self.prev_char == '\r':
                    # consume \n if former char is \r
                    self.accept()
                self.tracker.char_start, self.tracker.char_finish = 1, 1
                self.tracker.line_finish += 1
                self.tracker.line_start = self.tracker.line_finish
                return TokenType.NEWLINE

        # indent space in a new line
        # if self.current_char == ' ':
        #     counter = indent
        #     while counter > 0:
        #         self.accept()
        #         counter -= 1
        #     if self.prev_char == ' ':
        #         return TokenType.INDENT
        #     else:
        #         raise Exception('Indent expected')
        #
        if self.current_char == '%':
            self.accept()
            return TokenType.MOD
        elif self.current_char == '{':
            self.accept()
            return TokenType.LCURLY
        elif self.current_char == '}':
            self.accept()
            return TokenType.RCURLY
        elif self.current_char == '(':
            self.accept()
            return TokenType.LPAREN
        elif self.current_char == ')':
            self.accept()
            return TokenType.RPAREN
        elif self.current_char == '[':
            self.accept()
            return TokenType.LBRACKET
        elif self.current_char == ']':
            self.accept()
            return TokenType.RBRACKET
        elif self.current_char == ':':
            self.accept()
            return TokenType.COLON
        elif self.current_char == ';':
            self.accept()
            return TokenType.SEMICOLON
        elif self.current_char == ',':
            self.accept()
            return TokenType.COMMA
        elif self.current_char == '+':
            if self.look_ahead(1) == '=':
                self.accept(2)
                return TokenType.SELFPLUS
            self.accept()
            return TokenType.PLUS
        elif self.current_char == '-':
            if self.prev_char == ':' and self.digit.findall(
                    self.look_ahead(1)):
                self.accept()
                while self.digit.findall(self.current_char):
                    self.accept()
                return TokenType.NUMBER
            if self.look_ahead(1) == '=':
                self.accept(2)
                return TokenType.SELFMINUS
            self.accept()
            return TokenType.MINUS
        elif self.current_char == '*':
            self.accept()
            return TokenType.MULT
        elif self.current_char == '/':
            self.accept()
            return TokenType.DIV
        elif self.current_char == '!':
            if self.look_ahead(1) == '=':
                self.accept(2)
                return TokenType.NOTEQ
        elif self.current_char == '=':
            if self.prev_char == self.template_tag:
                token = TokenType.PRINT
            else:
                token = TokenType.EQ
            self.accept()
            if self.current_char == '=':
                self.accept()
                return TokenType.EQEQ
            return token
        elif self.current_char == '<':
            self.accept()
            if self.current_char == '=':
                self.accept()
                return TokenType.LTEQ
            return TokenType.LT
        elif self.current_char == '>':
            self.accept()
            if self.current_char == '=':
                self.accept()
                return TokenType.GTEQ
            return TokenType.GT
        elif self.current_char == '&':
            if self.look_ahead(1) == '&':
                self.accept(2)
                return TokenType.ANDAND
            return TokenType.ERROR
        elif self.current_char == '|':
            if self.look_ahead(1) == '|':
                self.accept(2)
                return TokenType.OROR
            return TokenType.ERROR
        elif self.current_char == '$' and self.template_tag:
            self.accept()
            if self.current_char.lower() == 'c' \
                    and self.look_ahead(1).lower() == 'l' \
                    and self.look_ahead(2).lower() == 'i' \
                    and self.look_ahead(3).lower() == 'e' \
                    and self.look_ahead(4).lower() == 'n' \
                    and self.look_ahead(5).lower() == 't' \
                    and not self.id_string_rest.findall(self.look_ahead(6)):
                self.accept(word='client')
                return TokenType.NAME
            elif self.current_char.lower() == 'p' \
                    and self.look_ahead(1).lower() == 'a' \
                    and self.look_ahead(2).lower() == 'r' \
                    and self.look_ahead(3).lower() == 't' \
                    and self.look_ahead(4).lower() == 'n' \
                    and self.look_ahead(5).lower() == 'e' \
                    and self.look_ahead(6).lower() == 'r' \
                    and not self.id_string_rest.findall(self.look_ahead(7)):
                self.accept(word='partner')
                return TokenType.NAME
            elif self.current_char.lower() == 's' \
                    and self.look_ahead(1).lower() == 'u' \
                    and self.look_ahead(2).lower() == 'p' \
                    and self.look_ahead(3).lower() == 'e' \
                    and self.look_ahead(4).lower() == 'r' \
                    and self.look_ahead(5).lower() == 'f' \
                    and self.look_ahead(6).lower() == 'u' \
                    and self.look_ahead(7).lower() == 'n' \
                    and self.look_ahead(8).lower() == 'd' \
                    and not self.id_string_rest.findall(self.look_ahead(9)):
                self.accept(word='superfund')
                return TokenType.NAME
            elif self.current_char.lower().lower() == 't' \
                    and self.look_ahead(1).lower() == 'r' \
                    and self.look_ahead(2).lower() == 'u' \
                    and self.look_ahead(3).lower() == 's' \
                    and self.look_ahead(4).lower() == 't' \
                    and not self.id_string_rest.findall(self.look_ahead(5)):
                self.accept(word='trust')
                return TokenType.NAME
            elif self.current_char.lower() == 'c' \
                    and self.look_ahead(1).lower() == 'o' \
                    and self.look_ahead(2).lower() == 'm' \
                    and self.look_ahead(3).lower() == 'p' \
                    and self.look_ahead(4).lower() == 'a' \
                    and self.look_ahead(5).lower() == 'n' \
                    and self.look_ahead(6).lower() == 'y' \
                    and not self.id_string_rest.findall(self.look_ahead(7)):
                self.accept(word='company')
                return TokenType.NAME
            elif self.current_char.lower() == 'p' \
                    and self.look_ahead(1).lower() == 'a' \
                    and self.look_ahead(2).lower() == 'r' \
                    and self.look_ahead(3).lower() == 't' \
                    and self.look_ahead(4).lower() == 'n' \
                    and self.look_ahead(5).lower() == 'e' \
                    and self.look_ahead(6).lower() == 'r' \
                    and self.look_ahead(7).lower() == 's' \
                    and self.look_ahead(8).lower() == 'h' \
                    and self.look_ahead(9).lower() == 'i' \
                    and self.look_ahead(10).lower() == 'p' \
                    and not self.id_string_rest.findall(self.look_ahead(11)):
                self.accept(word='partnership')
                return TokenType.NAME
            elif self.current_char.lower() == 'd' \
                    and self.look_ahead(1).lower() == 'o' \
                    and self.look_ahead(2).lower() == 'c' \
                    and self.look_ahead(3).lower() == 'n' \
                    and self.look_ahead(4).lower() == 'o' \
                    and self.look_ahead(5).lower() == 't' \
                    and self.look_ahead(6).lower() == 'e' \
                    and not self.id_string_rest.findall(self.look_ahead(7)):
                self.accept(word='docnote')
                return TokenType.NAME
            elif self.current_char.lower() == 'u' \
                    and self.look_ahead(1).lower() == 'd' \
                    and self.look_ahead(2).lower() == 'a' \
                    and not self.id_string_rest.findall(self.look_ahead(3)):
                self.accept(word='uda')
                return TokenType.NAME
            else:
                raise TokenTypeError(
                    f"""\n    Syntax Error while scanning, around line {str(self.tracker)}, near spelling < {repr(self.current_char)} >""")

        elif self.current_char.lower() == 'a':
            if self.look_ahead(1).lower() == 'n' \
                    and self.look_ahead(2).lower() == 'd' \
                    and not self.id_string_rest.findall(self.look_ahead(3)):
                self.accept(3, l_cap=True)
                return TokenType.AND
        elif self.current_char.lower() == 'o':
            if self.look_ahead(1).lower() == 'r' \
                    and not self.id_string_rest.findall(self.look_ahead(2)):
                self.accept(2, l_cap=True)
                return TokenType.OR
        elif self.current_char.lower() == 'n':
            if self.look_ahead(1).lower() == 'o' \
                    and self.look_ahead(2) == 't' \
                    and not self.id_string_rest.findall(self.look_ahead(3)):
                self.accept(3, l_cap=True)
                return TokenType.NOT
        elif self.current_char.lower() == 'i':
            if self.look_ahead(1).lower() == 'n' \
                    and not self.id_string_rest.findall(self.look_ahead(2)):
                self.accept(2, l_cap=True)
                return TokenType.IN

        # special end if/loop tag, usually come with template, for example:
        #
        # <:if xxx:><:end:> or {{if xxx}}{{endif}}
        elif self.current_char.lower() == 'e':
            if self.end_tag and self.look_ahead(1).lower() == 'n' \
                    and self.look_ahead(2).lower() == 'd':
                for end_tag in self.end_tag:
                    length = len(end_tag)

                    # 'end' case
                    if not end_tag[3:] and (not self.id_string_rest.findall(
                            self.look_ahead(length)) or self.look_ahead(
                            length) == '_EOF'):
                        self.accept(3, l_cap=True)
                        return TokenType.END

                    # 'endif' or else case
                    elif end_tag[3:]:
                        for i in range(3, length):
                            if self.look_ahead(i).lower() != end_tag[i]:
                                break
                        else:
                            if not self.id_string_rest.findall(
                                    self.look_ahead(length)):
                                self.accept(length, l_cap=True)
                                if end_tag[3:].lower() == 'if':
                                    return TokenType.ENDIF
                                elif end_tag[3:].lower() == 'for':
                                    return TokenType.ENDFOR
                                elif end_tag[3:].lower() == 'while':
                                    return TokenType.ENDWHILE

        # special `def` case, for example:
        # if template language use `var` to define variables, skipped it and
        # move the file pointer to variable name directly:
        #
        # e.g. {{var a = 1}}, and I will only got token 'a', '=' and '1'
        elif self.var_define \
                and self.current_char.lower() == self.var_define[0]:
            length = len(self.var_define)
            for i in range(1, length):
                if self.look_ahead(i).lower() != self.var_define[i]:
                    break
            else:
                if not self.id_string_rest.findall(self.look_ahead(length)):
                    self.move_ahead(length)
                    self.tracker.char_finish += length
                    self.tracker.char_start += length + 1
                    self.skip_space_comments()

        elif self.digit.findall(self.current_char):
            self.accept()
            while self.digit.findall(self.current_char) \
                    and self.current_char != self.source_file.eof:
                self.accept()
            if self.current_char != '.':
                return TokenType.NUMBER

        # literals, string
        if self.current_char == '"' or self.current_char == "'":
            quotation = self.current_char
            self.accept()  # eat '"'
            while self.current_char != quotation:
                if self.current_char == '\n' \
                        or self.current_char == '\r' \
                        or self.current_char == self.source_file.eof:
                    # ERROR: unterminated string
                    return TokenType.STRINGLITERAL
                elif self.current_char == '\\':
                    # an escape: 'A\t' will be read as 'A', '\\', 't'
                    # jump over escape, make current_char as the actually char
                    self.current_char = self.source_file.next_char()
                    self.current_char = self.make_escape(self.current_char)
                self.accept()
            self.accept()  # eat '"'  # eat '"'
            return TokenType.STRINGLITERAL

        # NAME
        if self.id_string_begin.findall(self.current_char):
            self.accept()
            while self.id_string_rest.findall(self.current_char) \
                    and self.current_char != self.source_file.eof:
                self.accept()
            if self.current_spelling == 'True' \
                    or self.current_spelling == 'False':
                return TokenType.BOOLEANLITERAL
            return TokenType.NAME

        # decimal dot
        if self.current_char == '.':
            # a number follows '.' - float number
            if self.digit.findall(self.look_ahead(1)):
                self.accept()  # eat '.'
                while self.digit.findall(self.current_char) \
                        and self.current_char != self.source_file.eof:
                    self.accept()

                if self.current_char != 'e' and self.current_char != 'E':
                    pass
                else:
                    # exponentials, 12.12e+22 12.12e-22 etc.
                    if self.look_ahead(1) == '+' or self.look_ahead(1) == '-' \
                            and self.digit.findall(self.look_ahead(2)):
                        self.accept(2)  # eat 'e', eat '+/-'
                        while self.digit.findall(self.current_char) \
                                and self.current_char != self.source_file.eof:
                            self.accept()
                    # exponentials, 12.12e12
                    elif self.digit.findall(self.look_ahead(1)):
                        self.accept()  # eat 'e'
                        while self.digit.findall(self.current_char) \
                                and self.current_char != self.source_file.eof:
                            self.accept()
                return TokenType.FLOATLITERAL

            # a dot notation between string and NAME, e.g. "a".join([xx])
            elif self.id_string_begin.findall(self.look_ahead(1)) \
                    and (self.id_string_rest.findall(self.prev_char)
                         or self.prev_char in ['"', "'"]):
                self.accept()
                return TokenType.NOTATION
            else:
                self.accept()
                return TokenType.ERROR

        if self.current_char == self.source_file.eof:
            self.current_spelling += self.source_file.eof
            return TokenType.EOF

        print(self.current_char)

        raise TokenTypeError(
            f"""\n    Unknown token while scanning, around line {str(self.tracker)}, near spelling < {repr(self.current_char)} >""")

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
        jump over spaces and comment
        """
        while self.current_char == ' ' or self.current_char == '	':
            if self.current_char == '	':
                self.tracker.char_finish += 3
            else:
                self.tracker.char_finish += 1
            self.move_ahead(1)

        # jump over comments
        if self.current_char == self.comment_tag:
            if self.template_tag:
                # jump template's comments, loop stops when current char &
                # next char matches template tag
                while True:
                    if (self.current_char == self.template_close[
                        0] and self.look_ahead(1) == self.template_close[
                        1]) or self.current_char == self.source_file.eof:
                        break
                    else:
                        self.move_ahead(1)
                        self.tracker.char_finish += 1
            else:
                # jump over comments on non template code
                if self.current_char == self.comment_tag:
                    while True:
                        self.move_ahead(1)
                        self.tracker.char_finish += 1
                        if self.current_char == '\n' \
                                or self.current_char == '\r' \
                                or self.current_char == self.source_file.eof:
                            break

    def get_token(self):
        """
        return a token instance on each time it being called
        (token = scanner_instance.get_token())
        until it reaches to EOF of input file
        """
        while self.current_char != self.source_file.eof:

            # case 1: in template code section or normal code file
            if self.code_flag:
                self.skip_space_comments()

                # sub case 1: template code case
                if self.template_tag:
                    if self.text_line_flag:
                        self.text_line_flag = False
                        return self.build_token(TokenType.NEWLINE, '\n',
                                                offset=-1)

                    if self.current_char == self.template_close[0]\
                            and self.look_ahead(1) == self.template_close[1]:
                        if self.if_for_flag or self.print_flag:
                            if self.if_for_flag:
                                self.if_for_flag = False
                                return self.build_token(TokenType.COLON, ':',
                                                        offset=-1)
                            elif self.print_flag:
                                self.print_flag = False
                                return self.build_token(TokenType.RPAREN, ')',
                                                        offset=-1)
                        else:
                            # check close tag, code close, skip template tag
                            self.move_ahead(2)
                            self.tracker.char_finish += 2
                            self.tracker.char_start = self.tracker.char_finish
                            self.code_flag = False
                            if self.current_char == '\n':
                                self.move_ahead(1)
                                self.tracker.line_finish += 1
                                self.tracker.char_finish = 1
                            return self.build_token(TokenType.NEWLINE)
                    else:
                        # still in code, processing code
                        if self.prev_token_type == TokenType.PRINT:
                            self.prev_token_type = TokenType.LPAREN
                            return self.build_token(TokenType.LPAREN, '(',
                                                    offset=-1)
                        else:
                            self.current_spelling = ''
                            self.tracker.char_start = self.tracker.char_finish
                            return self.build_token(self.get_token_type())

                # sub case 2: normal code case, e.g. Python
                else:
                    if self.current_char == self.source_file.eof:
                        break
                    self.current_spelling = ''
                    self.tracker.char_start = self.tracker.char_finish
                    return self.build_token(self.get_token_type())

            # case 2: in text literals, append char to text
            if not self.code_flag \
                    and self.current_char != self.source_file.eof:
                # if meets template tag, build text token when not null then
                # set code flag to True
                if self.current_char == self.template_tag[
                    0] and self.look_ahead(1) == self.template_tag[1]:
                    token = None
                    if self.text:
                        if self.text[-1] == '\n':
                            self.text_line_flag = True
                        token = self.build_token(TokenType.TEXTLITERAL,
                                                 self.text)
                        self.text = ''
                    self.tracker.line_start = self.tracker.line_finish
                    self.move_ahead(2)
                    self.tracker.char_finish += 2
                    self.code_flag = True
                    self.prev_char = self.template_tag
                    if token:
                        return token
                else:
                    if self.current_char:
                        self.text += self.current_char
                    if self.current_char == '\n':
                        # new line, increase line number, reset finish position
                        self.tracker.line_finish += 1
                        self.tracker.char_finish = 0
                    # annoying tab
                    if self.current_char == '	':
                        self.tracker.char_finish += 3
                    else:
                        self.tracker.char_finish += 1
                    self.move_ahead(1)

            # case 3: reaching eof, try to create text Token, then followed
            # by an EOF token (optional)
            if self.current_char == self.source_file.eof:
                # if text is not null then create text token
                if self.text and self.text != self.source_file.eof:
                    self.tracker.char_finish -= 1
                    token = self.build_token(TokenType.TEXTLITERAL, self.text)
                    self.tracker.char_finish += 1
                    self.tracker.line_start = self.tracker.line_finish
                    return token
                else:
                    break

    def build_token(self, token_type: int = None, text: str = None,
                    offset: int = None):
        """
        build and return a token based on token type and a possible text
        """
        if token_type is not None:
            # `offset=1`: as char_finish is right behind current token's end
            # location hence a minus is needed
            if offset == -1:
                token = Token(token_type, text,
                              self.tracker.snapshot(offset=-1))
            # normal tokens
            elif not text:
                # a newline token
                if token_type == TokenType.NEWLINE:
                    token = Token(token_type, '\n', self.tracker.snapshot())
                # not a newline token but spelling is a newline text
                elif self.current_spelling == '\'\n\'' \
                        or self.current_spelling == '\"\n\"':
                    token = Token(token_type, r"'\n'",
                                  self.tracker.snapshot(offset=1))
                # a print token
                elif token_type == TokenType.PRINT:
                    token = Token(token_type, 'print',
                                  self.tracker.snapshot(offset=-1))
                # all other cases
                else:
                    token = Token(token_type, self.current_spelling,
                                  self.tracker.snapshot(offset=1))

            # text token for template or eof token
            else:
                token = Token(token_type, text, self.tracker.snapshot())

            if self.template_tag \
                    and (self.prev_token_type == TokenType.NEWLINE
                         or self.prev_token_type == TokenType.TEXTLITERAL
                         or self.prev_token_type is None) and token.type in [
                TokenType.FOR, TokenType.IF,
                TokenType.ELIF, TokenType.ELSE,
                TokenType.WHILE]:
                self.if_for_flag = True
            if self.template_tag and token.type == TokenType.PRINT:
                self.print_flag = True

            # record previous token's type
            self.prev_token_type = token.type

            return token

    def get_eof_token(self):
        # create eof token
        self.tracker.line_start = self.tracker.line_finish
        self.tracker.char_start = self.tracker.char_finish
        return self.build_token(TokenType.EOF, self.source_file.eof)


if __name__ == '__main__':
    import os
    this_path = os.path.dirname(os.path.realpath(__file__))
    scanner = Scanner(SourceFile(source_file='', source_code="""<:for partnership in $partnership:>"""),
                      template_tag='<::>', var_define='def', end_tag=['end'])

    while scanner.current_char != scanner.source_file.eof:
        token = scanner.get_token()
        print(token)

    print(scanner.current_char)
