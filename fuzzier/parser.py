
from common import global_vars


class Json:
    NONE = 0
    CURLY_OPEN = 1
    CURLY_CLOSE = 2
    SQUARED_OPEN = 3
    SQUARED_CLOSE = 4
    COLON = 5
    COMMA = 6
    STRING = 7
    NUMBER = 8
    TRUE = 9
    FALSE = 10
    NULL = 11

    def __init__(self, json_string, search):
        self.index = 0
        self.success = True
        self.json = json_string
        self.length = len(json_string)
        self.search = search

    def parse(self):
        if self.json:
            return self.decider()
        else:
            return None

    def decider(self):
        """ it decides which kind of data will be parsed
        """
        token = self.check_token()
        if token == self.STRING:
            # '"'
            return self.parse_string()
        if token == self.NUMBER:
            # '0123456789-'
            return self.parse_number()
        if token == self.CURLY_OPEN:
            # '{'
            return self.parse_object()
        if token == self.SQUARED_OPEN:
            # '['
            return self.parse_array()
        if token == self.TRUE:
            # 'true'
            self.go_to_next_token()
            return True
        if token == self.FALSE:
            # 'false'
            self.go_to_next_token()
            return False
        if token == self.NULL:
            # 'null'
            self.go_to_next_token()
            return None
        if token == self.NONE:
            pass
        self.success = False
        return None

    def parse_object(self):
        """ a '{'
        """
        table = {}
        done = False
        self.go_to_next_token()

        while not done:
            token = self.check_token()
            if token == self.NONE:
                self.success = False
                return None
            elif token == self.COMMA:
                 self.go_to_next_token()
            elif token == self.CURLY_CLOSE:
                self.go_to_next_token()
                return table
            else:
                # all other token types:
                # a name
                name = self.parse_string()
                if not self.success:
                    return None
                # a ':'
                token = self.go_to_next_token()
                if token != self.COLON:
                    self.success = False
                    return None
                # a value, send to decider to decide type
                value = self.decider()
                if not self.success:
                    self.success = False
                    return None
                table[name] = value
        return table

    def parse_array(self):
        """ a '['
        """
        array = []
        done = False
        self.go_to_next_token()

        while not done:
            token = self.check_token()
            if token == self.NONE:
                self.success = False
                return None
            elif token == self.COMMA:
                 self.go_to_next_token()
            elif token == self.SQUARED_CLOSE:
                self.go_to_next_token()
                break
            else:
                value = self.decider()
                if not self.success:
                    self.success = False
                    return None
                array.append(value)
        return array

    def parse_string(self):
        """ a '"'
        """
        self.ignore_white_space()
        string = ''
        done = False
        self.index += 1  # current index is '"', +1 to move to string

        while not done:
            if self.index == self.length:
                break

            char = self.json[self.index]
            self.index += 1
            if char == '"':
                done = True
                break
            elif char == '\\':
                if self.index == self.length:
                    break

                char = self.json[self.index]
                self.index += 1
                if char == '"':
                    string += '"'
                elif char == '\\':
                    string += '\\'
                elif char == '/':
                    string += '/'
                elif char == 'b':
                    string += '\b'
                elif char == 'f':
                    string += '\f'
                elif char == 'n':
                    string += '\n'
                elif char == 'r':
                    string += '\r'
                elif char == 't':
                    string += '\t'
                elif char == 'u':
                    remaining_length = self.length - self.index
                    if remaining_length >= 4:
                        # 32 bit unicode, reserved for future
                        a = 1
            else:
                # build string a-zA-Z0-9
                string += char
        if not done:
            self.success = False
            return None
        self.search(string, global_vars.pattern)
        return string

    def parse_number(self):
        self.ignore_white_space()
        pointer = self.index
        number = 0
        while pointer < self.length:
            if self.json[pointer] not in '0123456789+-.eE':
                break
            else:
                pointer += 1

        try:
            number = int(self.json[self.index:pointer])
        except:
            self.success = False
        else:
            self.success = True
        finally:
            self.index = pointer
            return number

    def check_token(self):
        """ check next token but not move index
        """
        return self.go_to_next_token(check_token=True)

    def go_to_next_token(self, check_token=False):
        self.ignore_white_space()
        index = self.index

        if index == self.length:
            return self.NONE

        c = self.json[index]
        # move index to next position
        index += 1
        if not check_token:
            self.index = index
        if c == '{':
            return self.CURLY_OPEN
        elif c == '}':
            return self.CURLY_CLOSE
        elif c == '[':
            return self.SQUARED_OPEN
        elif c == ']':
            return self.SQUARED_CLOSE
        elif c == ',':
            return self.COMMA
        elif c == '"':
            return self.STRING
        elif c == '0' or c == '1' or c == '2' or c == '3' or c == '4'\
                      or c == '5' or c == '6' or c == '7' or c == '8'\
                      or c == '9' or c == '-':
            return self.NUMBER
        elif c == ':':
            return self.COLON
        # if nothing returned, move back index to keep checking
        index -= 1
        if not check_token:
            self.index = index

        remaining_length = self.length - index
        if remaining_length >= 5:
            # 'false' case
            if self.json[index] == 'f' and self.json[index + 1] == 'a'\
                                       and self.json[index + 2] == 'l'\
                                       and self.json[index + 3] == 's'\
                                       and self.json[index + 4] == 'e':
                index += 5
                if not check_token:
                    self.index = index
                return self.FALSE
        if remaining_length >= 4:
            # 'true' case
            if self.json[index] == 't' and self.json[index + 1] == 'r'\
                                       and self.json[index + 2] == 'u'\
                                       and self.json[index + 3] == 'e':
                index += 4
                if not check_token:
                    self.index = index
                return self.TRUE
        if remaining_length >= 4:
            # 'null' case
            if self.json[index] == 'n' and self.json[index + 1] == 'u'\
                                       and self.json[index + 2] == 'l'\
                                       and self.json[index + 3] == 'l':
                index += 4
                if not check_token:
                    self.index = index
                return self.NULL
        return self.NONE

    def ignore_white_space(self):
        while self.json[self.index] == ' ' or self.json[self.index] == '\t'\
                                           or self.json[self.index] == '\n':
            self.index += 1
