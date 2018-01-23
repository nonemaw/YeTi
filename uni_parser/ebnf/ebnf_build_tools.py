from uni_parser.ebnf.ebnf_scanner import TokenType


class BuildTracker:
    """
    tracker used for building productions
    """
    def __init__(self, grammar_dict: dict):
        self.grammars = grammar_dict  # record all available grammar object
        self.on_track = []  # record all tracked grammar's name

    def __iter__(self):
        return iter(self.grammars)

    def __getitem__(self, item):
        return self.grammars.__getitem__(item)

    def __delitem__(self, item):
        self.grammars.__delitem__(item)

    def __setitem__(self, item, value):
        self.grammars.__setitem__(item, value)

    def list_grammars(self):
        return ' '.join([self.grammars.get(name) for name in self.grammars])

    def list_on_track(self):
        return ' '.join([name for name in self.on_track])


class Lexer:
    def __init__(self, scanner):
        """
        lexer will get one token from scanner each time, scanner read code from
        an input file like a Python file or an EBNF grammar file
        """
        self.scanner = scanner
        self.current_token = self.scanner.get_token()
        self.skip_redundant_newline()
        self.history = [self.current_token]
        self.h_index = 0
        self.anchor_stack = []

        # for error message / raise exception only, indicate error range
        self.last_token = self.current_token

        # for detect left recursion: ((current token's position), grammar name)
        self.lr_mark = ()

    def skip_redundant_newline(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.current_token = self.scanner.get_token()

    def forward(self):
        self.h_index += 1
        try:
            self.current_token = self.history[self.h_index]
        except:
            # index out of range, get token from file instead
            self.current_token = self.scanner.get_token()
            self.history.append(self.current_token)

    def current_position(self) -> tuple:
        try:
            position = self.current_token.position_snapshot()
        except:
            position = (0, 0, 0, 0)
        return position

    def print_history(self):
        return [str(item) for item in self.history]

    def backward(self):
        # rollback to a specific index to anchored history
        if self.current_token is None:
            pass
        else:
            if self.current_token.position[0] > self.last_token.position[2]:
                self.last_token = self.current_token
            elif self.current_token.position[0] == self.last_token.position[
                2] and self.current_token.position[1] > \
                       self.last_token.position[3]:
                self.last_token = self.current_token
        self.h_index = self.anchor_stack.pop()
        self.current_token = self.history[self.h_index]

    def anchor(self):
        # set current recursion's anchor stack
        self.anchor_stack.append(self.h_index)

    def release_anchor(self):
        # release last recursion's anchor
        self.anchor_stack.pop()
