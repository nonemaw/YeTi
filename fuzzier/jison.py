import os
import json
from common.meta import Meta


class JsonSyntaxError(Exception):
    pass


class Jison:
    """
    Jison is a simple one-line Json parser merged with a string search feature.
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

    def __init__(self, json_string: str, old_chunk: str = None,
                 new_chunk: dict = None, target_file: str = None, **kwargs):
        self.index = 0
        self.success = True

        # top-level object manipulation:
        # if only old_chunk is assigned, Jison will return the dictionary of this object
        # if only new_chunk is assigned, Jison will append new dictionary to json
        # if both old_chunk and new_chunk are assigned, Jison will delete the old chunk, and append new dictionary
        # if target_file is None, old_chunk and new_chunk will be ignored
        if target_file:
            self.old_chunk = old_chunk  # object name
            self.new_chunk = json.dumps(new_chunk)  # full new dict
            self.target_file = target_file
            self.chunk_location = []
            self.recursion_depth = 0
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'json', f'{Meta.company}.json', 'r')) as F:
                self.json = F.readline()
        else:
            self.json = json_string

        self.length = len(json_string)
        self.ratio_method = None
        if len(kwargs):
            try:
                self.ratio_method = kwargs.get('ratio_method')
                self.pattern = kwargs.get('pattern')
                self.result_length = int(
                    kwargs.get('result_length')) if kwargs.get(
                    'result_length') else 7
                self.result = []
                self.deep = 0
                self.var_val = 0
                self.var_name = ''
                self.group = ''
                self.sub = ''
            except:
                self.ratio_method = None

    def get_object(self) -> dict:
        self.parse()
        if not self.old_chunk:
            return {}

        from ast import literal_eval
        return literal_eval(
            f'{{{self.json[self.chunk_location[0]:self.chunk_location[1]]}}}')

    def replace_object(self):
        self.remove_object(called_by_replace=True)
        self.json = f'{self.json[0:self.chunk_location[0]]}{self.new_chunk[1:-2]}{self.json[self.chunk_location[1]:]}'
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'json', f'{Meta.company}.json', 'w')) as F:
            import json
            json.dump(self.json, F)

    def remove_object(self, called_by_replace: bool = False) -> str:
        self.parse()

        if not called_by_replace:
            left = self.chunk_location[0]
            right = self.chunk_location[1]
            if self.json[self.chunk_location[0] - 1] != '{':
                left = left - 2
            if self.json[self.chunk_location[1] + 1] != '}' and self.json[
                        self.chunk_location[1] + 1] != ']':
                right = right + 2
            self.json = f'{self.json[:left]}{self.json[right:]}'

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'json', f'{Meta.company}.json', 'w')) as F:
                import json
                json.dump(self.json, F)
                return self.json
        else:
            return ''

    def parse(self):
        if self.json:
            if self.ratio_method:
                self.scanner(0)
                return self.result
            return self.scanner(0)
        else:
            raise JsonSyntaxError(f'Json syntax error at index {self.index}')

    def scanner(self, recursion: int = 0):
        """ it decides which kind of data will be parsed
        """
        token = self.check_token()
        if token == self.STRING:
            # '"'
            if self.old_chunk:
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

    def parse_object(self, recursion: int):
        """ a '{'
        """
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
                if self.recursion_depth == recursion and len(
                        self.chunk_location) == 1:
                    self.chunk_location.append(self.index - 2)
                if self.old_chunk:
                    key, location = self.parse_string()
                    if key == self.old_chunk and not self.chunk_location:
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

    def parse_array(self, recursion: int):
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
        if self.old_chunk:
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

        if self.old_chunk:
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


if __name__ == '__main__':
    jison = Jison(
        '{"OBJ1": [{"AMPFDS Services Comment": [{"comment": "Comment"}, {"date": "Date"}]}], "OBJ2": [{"Savings Scenario": [{"modifiedby": "Modified By"}, {"modifiedstamp": "Modified Date"}, {"descp": "Description"}, {"createdby": "Created By"}, {"createdstamp": "Created Date"}]}]}',
        old_chunk='Savings Scenario',
        new_chunk={'OBJ3': ['A', 'B']}
    )
    from pprint import pprint

    pprint(jison.replace_object())
