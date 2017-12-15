import os
from ast import literal_eval


class JsonSyntaxError(Exception):
    pass


class JsonObjectRemovalFailed(Exception):
    pass


class Jison:
    """
    Jison is a simple parser for one-line Json string for Json manipulation:

    1. string search under a maintained tree structure
    2. Json object acquisition
    3. Json object deletion
    4. Json object replacement
    """
    NONE = 0
    OBJ_OPEN = 1
    OBJ_CLOSE = 2
    ARR_OPEN = 3
    ARR_CLOSE = 4
    COLON = 5
    COMMA = 6
    STRING = 7
    NUMBER = 8
    TRUE = 9
    FALSE = 10
    NULL = 11

    def __init__(self, json_string: str = None, company: str = None, **kwargs):
        self.index = 0
        self.success = True
        self.company = company

        # object (dict) manipulation:
        # old_chunk: for get_object()/remove_object()/replace_object()
        # new_chunk: for replace_object()
        self.chunk_location = []
        self.recursion_depth = 0

        # if json_string is manually provided then file will be ignored. If
        # further operations such as remove or replace have been done, the file
        # will be overwritten with the provided json_string + operation results
        if json_string:
            try:
                literal_eval(json_string)
                self.json = json_string.strip()
            except:
                raise JsonSyntaxError('Jison got an invalid Json string')
        elif company:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'json', f'{self.company}.json'), 'r') as F:
                self.json = F.readline().strip()
        else:
            raise Exception('No Json string has been provided')
        self.length = len(self.json)

        self.ratio_method = None

    def get_object(self, obj_name: str) -> dict:
        self.obj_name = obj_name
        self.parse(recursion=0)
        self.index = 0
        if not self.obj_name:
            return {}

        returned_dict = literal_eval(
            f'{{{self.json[self.chunk_location[0]:self.chunk_location[1]]}}}')
        self.chunk_location.clear()
        self.recursion_depth = 0

        return returned_dict

    def replace_object(self, obj_name: str, new_chunk):
        """
        replace `old_chunk` (object name) with `new_chunk` (dict or Json string),
        and write result to file
        """
        if isinstance(new_chunk, str):
            try:
                literal_eval(new_chunk)
            except:
                raise JsonSyntaxError(
                    '"new_chunk" is not a valid Json string')
        elif isinstance(new_chunk, dict):
            import json
            new_chunk = json.dumps(new_chunk)
        else:
            raise Exception(
                f'Jison.replace_object() only accepts type "str" or "dict", but got {type(new_chunk)}')

        # TODO: support a list of obj_name's replacement rather than only one
        # TODO: obj_name = ['a', 'b', 'c']
        # TODO: new_chunk = [chunk1, chunk2, chunk3]
        if len(new_chunk) > 2:
            self.obj_name = obj_name
            self.parse(recursion=0)
            self.index = 0

            if self.chunk_location:
                self.json = f'{self.json[0:self.chunk_location[0]]}{new_chunk[1:-1]}{self.json[self.chunk_location[1]:]}'
                self.length = self.json
                self.chunk_location.clear()
                self.recursion_depth = 0
                if self.company:
                    with open(os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            'json', f'{self.company}.json'), 'w') as F:
                        F.write(self.json)
                else:
                    return self.json
            else:
                # if the chunk_location is empty do not throw exception
                pass

        else:
            # an empty `new_chunk`: {}
            pass


    def remove_object(self, obj_name: str):
        """
        remove `old_chunk` (object name) from Json string

        if this method is `called_by_replace`: return nothing, keep modified Json
        in memory and waiting for further process in `replace_object()`

        if this method is not `called_by_replace`: write changes to file
        """
        self.obj_name = obj_name
        self.parse(recursion=0)
        self.index = 0

        if self.chunk_location:
            left = self.chunk_location[0]
            right = self.chunk_location[1]

            # case 1: ...|, {"key": value}| ...
            if self.json[left - 1] == '{' and self.json[right] == '}':
                if self.length == right + 1:
                    raise JsonObjectRemovalFailed(
                        f'Cannot remove the ONLY object "{obj_name}" in Json')
                else:
                    left -= 3
                    right += 1
            # case 2: ...|, "key": value|, ...
            if (self.json[left - 1] == ' ' or self.json[left - 1] == ',') and (
                            self.json[right] == ' ' or self.json[
                        right] == ','):
                print('case2')
                left -= 2
            # case 3: ...|, "key": value|} ...
            if (self.json[left - 1] == ' ' or self.json[left - 1] == ',') and \
                            self.json[right] == '}':
                print('case3')
                left -= 2
            # case 4: ..., {|"key": value, |...
            if self.json[left - 1] == '{' and self.json[right] == ',':
                print('case4')
                right += 1
                if self.json[right] == ' ':
                    right += 1

            self.json = f'{self.json[:left]}{self.json[right:]}'
            self.length = len(self.json)
            self.recursion_depth = 0
            self.chunk_location.clear()
            if self.company:
                with open(os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'json', f'{self.company}.json'), 'w') as F:
                    F.write(self.json)
            else:
                return self.json

        else:
            raise JsonObjectRemovalFailed(
                f'The Json object "{obj_name}" does not exist')

    def search(self, pattern: str, ratio_method, count: int = 8) -> list:
        self.ratio_method = ratio_method
        self.pattern = pattern
        self.result_length = int(count)
        self.result = []
        self.deep = 0
        self.var_val = 0
        self.var_name = ''
        self.group = ''
        self.sub = ''

        self.parse()
        self.index = 0
        return self.result

    def json_to_file(self, json_string):
        if isinstance(json_string, str):
            try:
                literal_eval(json_string)
            except:
                raise JsonSyntaxError(
                    'Jison.json_to_file() got an invalid Json string')
            self.json = json_string
        elif isinstance(json_string, dict):
            import json
            self.json = json.dumps(json_string)
        else:
            raise Exception(
                f'Jison.json_to_file() only accepts type "str" or "dict", but got {type(json_string)}')

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'json', f'{self.company}.json'), 'w') as F:
            F.write(json_string)

    def parse(self, recursion: int = None):
        if self.json:
            return self.scanner(recursion)
        else:
            raise JsonSyntaxError('No Json string provided')

    def scanner(self, recursion: int = None):
        """ it decides which kind of data will be parsed
        """
        token = self.check_token()
        if token == self.STRING:
            # '"'
            if hasattr(self, 'obj_name') and self.obj_name:
                return self.parse_string()[0]
            return self.parse_string()
        if token == self.NUMBER:
            # '0123456789-'
            return self.parse_number()
        if token == self.OBJ_OPEN:
            # '{'
            if self.ratio_method:
                self.deep += 1
            return self.parse_object(recursion)
        if token == self.ARR_OPEN:
            # '['
            if self.ratio_method:
                self.deep += 1
            return self.parse_array(recursion)
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
            raise JsonSyntaxError(f'Json syntax error at index {self.index}')
        if token == self.NONE:
            pass
        self.success = False
        raise JsonSyntaxError(f'Json syntax error at index {self.index}')

    def check_token(self):
        """ check next token but not move index
        """
        return self.go_to_next_token(check_token=True)

    def go_to_next_token(self, check_token: bool = False):
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
            return self.OBJ_OPEN
        elif c == '}':
            return self.OBJ_CLOSE
        elif c == '[':
            return self.ARR_OPEN
        elif c == ']':
            return self.ARR_CLOSE
        elif c == ',':
            return self.COMMA
        elif c == '"':
            return self.STRING
        elif c == '0' or c == '1' or c == '2' or c == '3' or c == '4' \
                or c == '5' or c == '6' or c == '7' or c == '8' \
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
            if self.json[index] == 'f' and self.json[index + 1] == 'a' \
                    and self.json[index + 2] == 'l' \
                    and self.json[index + 3] == 's' \
                    and self.json[index + 4] == 'e':
                index += 5
                if not check_token:
                    self.index = index
                return self.FALSE
        if remaining_length >= 4:
            # 'true' case
            if self.json[index] == 't' and self.json[index + 1] == 'r' \
                    and self.json[index + 2] == 'u' \
                    and self.json[index + 3] == 'e':
                index += 4
                if not check_token:
                    self.index = index
                return self.TRUE
        if remaining_length >= 4:
            # 'null' case
            if self.json[index] == 'n' and self.json[index + 1] == 'u' \
                    and self.json[index + 2] == 'l' \
                    and self.json[index + 3] == 'l':
                index += 4
                if not check_token:
                    self.index = index
                return self.NULL
        return self.NONE

    def parse_object(self, recursion: int = None):
        """ a '{'
        """
        if recursion is not None:
            recursion += 1
        table = {}
        self.go_to_next_token()

        while True:
            token = self.check_token()

            if token == self.NONE:
                self.success = False
                raise JsonSyntaxError(
                    f'Json syntax error at index {self.index}')
            elif token == self.COMMA:
                self.go_to_next_token()
            elif token == self.OBJ_CLOSE:
                if recursion == self.recursion_depth and len(
                        self.chunk_location) == 1:
                    self.chunk_location.append(self.index)

                if self.ratio_method:
                    self.deep -= 1
                self.go_to_next_token()
                return table
            else:
                # not comma, not close, it can be all the following token types:
                # a key
                if recursion is not None:
                    if self.recursion_depth == recursion and len(
                            self.chunk_location) == 1:
                        self.chunk_location.append(self.index - 2)

                if recursion is not None and hasattr(self,
                                                     'obj_name') and self.obj_name:
                    key, location = self.parse_string()
                    if key == self.obj_name and not self.chunk_location:
                        self.chunk_location.append(location)
                        self.recursion_depth = recursion
                else:
                    key = self.parse_string()

                if not self.success:
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}')

                # a ':'
                token = self.go_to_next_token()
                if token != self.COLON:
                    self.success = False
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}')

                # a value
                value = self.scanner(recursion)
                if not self.success:
                    self.success = False
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}')
                table[key] = value

    def parse_array(self, recursion: int = None):
        """ a '['
        """
        array = []
        self.go_to_next_token()

        while True:
            token = self.check_token()
            if token == self.NONE:
                self.success = False
                raise JsonSyntaxError(
                    f'Json syntax error at index {self.index}')
            elif token == self.COMMA:
                self.go_to_next_token()
            elif token == self.ARR_CLOSE:
                if self.ratio_method:
                    self.deep -= 1
                self.go_to_next_token()
                break
            else:
                value = self.scanner(recursion)
                if not self.success:
                    self.success = False
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}')
                array.append(value)
        return array

    def parse_string(self):
        """ a '"'
        """
        if hasattr(self, 'obj_name') and self.obj_name:
            anchor = self.index

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
                        # handling 32 bit unicode, reserved for future development when I have time
                        a = 1
            else:
                # build string a-zA-Z0-9
                string += char
        if not done:
            self.success = False
            raise JsonSyntaxError(f'Json syntax error at index {self.index}')
        if self.ratio_method:
            if self.deep == 1:
                # I am the group
                self.group = string
            elif self.deep == 3:
                # I am the subgroup
                self.sub = string
            elif self.deep == 5 and self.var_val:
                # I am a variable
                current_ratio = self.ratio_method(string, self.pattern)
                self.var_val = 0
                if current_ratio > 0.15:
                    if len(self.result) == self.result_length:
                        stored_ratio_result = [i[0] for i in self.result]
                        min_ratio = min(stored_ratio_result)
                        if current_ratio >= max(stored_ratio_result):
                            for index, item in enumerate(self.result):
                                if item[0] == min_ratio:
                                    self.result[index] = [current_ratio,
                                                          self.group, self.sub,
                                                          self.var_name,
                                                          string]
                                    break
                        else:
                            pass
                    else:
                        self.result.append(
                            [current_ratio, self.group, self.sub,
                             self.var_name,
                             string])
            elif self.deep == 5 and not self.var_val:
                self.var_name = string
                self.var_val = 1

        if hasattr(self, 'obj_name') and self.obj_name:
            return string, anchor

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

    def ignore_white_space(self):
        while self.json[self.index] == ' ' or self.json[self.index] == '\t' \
                or self.json[self.index] == '\n':
            self.index += 1
