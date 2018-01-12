import os
import re


class JsonSyntaxError(Exception):
    pass


class JsonObjectRemovalFailed(Exception):
    pass


class JsonNotLoaded(Exception):
    pass


class InvalidJson(Exception):
    pass


class Jison:
    """
    Jison is a simple parser for Json manipulation. It parses a Json string
    into a dictionary with syntax check like what Python's builtin method
    `json.loads()` does, but beside this it provides many additional features:

    (the `object` refers any Json key:value pair)
    1. string search under tree structure & hierarchical search
       (requires a string match function as parameter for work)
    2. single Json object acquisition
       (get one Json object returned as dict)
    3. multiple Json object acquisition
       (get all Json objects under any depth with same key value and return
        them as a list of dictionary)
    4. Json object deletion
       (delete any single Json object)
    5. Json object replacement
       (find and replace any single Json object)
    """

    def __init__(self, json_string=None, file_name: str = None):
        self.NONE = 0
        self.OBJ_OPEN = 1
        self.OBJ_CLOSE = 2
        self.ARR_OPEN = 3
        self.ARR_CLOSE = 4
        self.COLON = 5
        self.COMMA = 6
        self.STRING = 7
        self.NUMBER = 8
        self.TRUE = 9
        self.FALSE = 10
        self.NULL = 11

        self.index = 0
        self.success = True

        # object (dict) manipulation:
        # old_chunk: for get_object()/remove_object()/replace_object()
        # new_chunk: for replace_object()
        self.chunk_location = []
        self.obj_name = None

        # object_list is for store multiple object in a list
        self.chunk_location_dict = {}
        self.single_object = False
        self.multi_object = False

        # search_result stores search results
        self.search_result = []
        self.result_length = 8

        # recursion_depth used for object manipulation
        self.recursion_depth = 0

        # deep/ratio_method used for search mechanism
        self.deep = 0
        self.ratio_method = None

        if json_string or file_name:
            self.load_json(json_string, file_name)

    def check_json_string(self, json_content: str) -> str:
        if json_content:
            return re.sub(' *\n *', ' ', json_content).strip()
        else:
            raise InvalidJson('Empty Json string provided')

    def dict_to_json_string(self, json_content: dict) -> str:
        # TODO: get ride of json library, convert dict -> json string
        import json
        return json.dumps(json_content)

    @staticmethod
    def multi_sub(pattern_dict: dict, text: str) -> str:
        # build re for key
        multi_sub = re.compile('|'.join(map(re.escape, pattern_dict)))

        # return pattern_dict's target text based on a matched key
        # e.g. {'a': 'bb'}, if 'a' is matched by re then get and return 'bb'
        def one_xlat(match):
            return pattern_dict.get(match.group(0))

        return multi_sub.sub(one_xlat, text)

    def load_json(self, json_string=None, file_name: str = None):
        """
        if Json string is manually provided then Json in file is ignored

        if filename is provided, changes to Json (deletion/replacement) will be
        written to file (result in form of one-line Json string, a beautified
        Json structure will be overwritten)

        if filename is not provided, changes to Json will be returned as Json
        string
        """
        self.file_name = file_name

        if json_string and isinstance(json_string, str):
            self.json = self.check_json_string(json_string)
        elif json_string and isinstance(json_string, dict):
            self.json = self.dict_to_json_string(json_string)

        elif file_name:
            def convert_file():
                with open(os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        'json', f'{self.file_name}.json'),
                        'r') as F:
                    for line in F:
                        yield line.strip()

            try:
                self.json = ' '.join(convert_file()).strip()

            # file does not exist, raise exception later
            except:
                self.json = ''
        else:
            raise Exception('No Json string has been provided')

        if not self.json:
            raise Exception('Json file is empty')

        self.length = len(self.json)

    def get_object(self, obj_name: str, value_only: bool = False):
        """
        return a matched object key-value pair

        if there were multiple objects with same key, only the first match will
        be returned
        """
        self.obj_name = obj_name
        self.single_object = True
        self.parse(recursion=0)

        if not self.chunk_location:
            return {}

        cache = self.json
        self.load_json(
            f'{{{self.json[self.chunk_location[0]:self.chunk_location[1]]}}}')
        returned_dict = self.parse()

        self.load_json(cache)
        self.chunk_location.clear()

        if returned_dict:
            if value_only:
                return returned_dict.get(obj_name)
            return returned_dict

        return None

    def get_multi_object(self, obj_name, value_only: bool = False):
        """
        return a list of all matched object key-value pairs with same key value
        `obj_name` can be both str or list

        this method will not return a `covered` object, for example: if user is
        requesting object `family` and `children`, and `family` already covers
        `children`, then it will only return the result of `family` object:
        {"family": {"parent": "papa", "children": ["alice", "bob"]}}

        when `obj_name` is in list, it will returns multiple results, e.g.:
        parent, children = get_multi_object(['parent', 'children'])
        """
        self.obj_name = obj_name
        self.multi_object = True
        self.parse(recursion=0)

        if not self.chunk_location_dict and isinstance(obj_name, list):
            return [None for _ in range(len(obj_name))]
        elif not self.chunk_location_dict:
            return None

        cache = self.json
        returned_list = []
        if isinstance(obj_name, str):
            for key in self.chunk_location_dict:
                for chunk in self.chunk_location_dict.get(key):
                    self.load_json(f'{{{cache[chunk[0]:chunk[1]]}}}')
                    result_dict = self.parse()

                    if result_dict:
                        if value_only:
                            returned_list.append(result_dict.get(key))
                        else:
                            returned_list.append(result_dict)

        else:
            for key in obj_name:
                chunks_for_each_string = self.chunk_location_dict.get(key)
                if chunks_for_each_string:
                    returned_list.append([])
                    for chunk in chunks_for_each_string:
                        self.load_json(f'{{{cache[chunk[0]:chunk[1]]}}}')
                        result_dict = self.parse()

                        if result_dict:
                            if value_only:
                                returned_list[-1].append(result_dict.get(key))
                            else:
                                returned_list[-1].append(result_dict)
                else:
                    returned_list.append(None)

        self.load_json(cache)
        self.chunk_location_dict.clear()

        if not returned_list:
            return None
        return returned_list

    def replace_object(self, obj_name: str, new_chunk):
        """
        replace `old_chunk` (object name) with `new_chunk` (dict or Json string),
        and write result to file

        parser will search for object with `obj_name` and replace with new_chunk
        """
        if isinstance(new_chunk, str):
            new_chunk = self.check_json_string(new_chunk)
        elif isinstance(new_chunk, dict):
            new_chunk = self.dict_to_json_string(new_chunk)
        else:
            raise Exception(
                f'Jison.replace_object() only accepts type "str" or "dict", but got "{type(new_chunk)}"')

        if len(new_chunk) > 2:
            self.obj_name = obj_name
            self.parse(recursion=0)

            if self.chunk_location:
                self.json = f'{self.json[0:self.chunk_location[0]]}{new_chunk[1:-1]}{self.json[self.chunk_location[1]:]}'
                self.length = len(self.json)
                self.chunk_location.clear()
                if self.file_name:
                    self.write(skip_check=True)
                    return self
                else:
                    return self

            else:
                # if search failed, do not throw exception
                return None
        else:
            # an empty `new_chunk`: {}
            return None

    def remove_object(self, obj_name: str):
        """
        remove `old_chunk` (object name) from Json string

        it cannot manipulate a Json with only ONE object
        """
        self.obj_name = obj_name
        self.parse(recursion=0)

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
                left -= 2
            # case 3: ...|, "key": value|} ...
            if (self.json[left - 1] == ' ' or self.json[left - 1] == ',') and \
                            self.json[right] == '}':
                left -= 2
            # case 4: ..., {|"key": value, |...
            if self.json[left - 1] == '{' and self.json[right] == ',':
                right += 1
                if self.json[right] == ' ':
                    right += 1

            self.json = f'{self.json[:left]}{self.json[right:]}'
            self.length = len(self.json)
            self.chunk_location.clear()

            if self.file_name:
                self.write(skip_check=True)
                return self
            else:
                return self

        # if search failed, do not throw exception
        else:
            return None

    def search(self, pattern: str, ratio_method, count: int = 8,
               threshold: float = 0.15) -> list:
        """
        ratio_method must return a valid positive float number as ratio ranges
        in (0, 1]
        """
        self.ratio_method = ratio_method
        self.result_length = int(count)
        self.threshold = threshold
        self.deep = 0
        self.is_var_value = True
        self.skipped = False
        self.var_name = ''
        self.group = ''
        self.sub = ''

        # a pattern can be a simple string (for variable search)
        # or a combination of 'parent_pattern:pattern'
        if re.search(':', pattern):
            self.pattern = [p.strip() for p in pattern.split(':') if p]
        else:
            self.pattern = pattern
        self.parse()

        returned_result = self.search_result
        self.search_result = []

        return returned_result

    def write(self, json_string=None, file_name: str = None, skip_check=False):
        if not file_name:
            file_name = self.file_name

        if not skip_check and json_string:

            if isinstance(json_string, str):
                self.json = self.check_json_string(json_string)
            elif isinstance(json_string, dict):
                self.json = self.dict_to_json_string(json_string)
            else:
                raise Exception(
                    f'Jison.write() only accepts type "str" or "dict", but got {type(json_string)}')

            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'json', f'{file_name}.json'),
                      'w') as F:
                F.write(json_string)

        elif skip_check:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'json', f'{file_name}.json'),
                      'w') as F:
                F.write(self.json)

        else:
            # if json_string is not provided and not skip_check then do nothing
            pass

    def parse(self, recursion: int = None) -> dict:
        if not hasattr(self, 'json'):
            raise JsonNotLoaded(
                'Json string is not loaded\nPlease load Json via running Jison.load_json() before any operation')

        if self.json:
            result_dict = self.scanner(recursion)
            # reset data after each parse operation
            self.index = 0
            self.recursion_depth = 0

            if self.obj_name:
                self.obj_name = None
            if self.single_object:
                self.single_object = False
            if self.multi_object:
                self.multi_object = False

            return result_dict

        else:
            raise JsonSyntaxError('No Json string provided')

    def scanner(self, recursion: int = None):
        """
        it decides which kind of data will be parsed

        returned type can be a dict, list, or string
        """
        token = self.check_token()
        if token == self.STRING:
            # '"'
            return self.parse_string()[0]
        if token == self.NUMBER:
            # '0123456789-'
            return self.parse_number()
        if token == self.OBJ_OPEN:
            # '{'
            return self.parse_object(recursion)
        if token == self.ARR_OPEN:
            # '['
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
            return None
        if token == self.NONE:
            pass

        self.success = False
        raise JsonSyntaxError(
            f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')

    def check_token(self) -> int:
        """ check next token but not move index
        """
        return self.go_to_next_token(check_token=True)

    def go_to_next_token(self, check_token: bool = False) -> int:
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

    def parse_object(self, recursion: int = None) -> dict:
        """ a '{'
        """
        if recursion is not None:
            recursion += 1
        if self.ratio_method:
            self.deep += 1

        table = {}
        self.go_to_next_token()

        while True:
            token = self.check_token()

            if token == self.NONE:
                self.success = False
                raise JsonSyntaxError(
                    f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')
            elif token == self.COMMA:
                self.go_to_next_token()
            elif token == self.OBJ_CLOSE:
                if recursion == self.recursion_depth and len(
                        self.chunk_location) == 1:
                    # condition for search object - chunk_location position 1
                    # object ends with `}`
                    self.chunk_location.append(self.index)
                    if self.single_object:
                        # TODO: break operation when single obj search's condition matched
                        pass

                    if self.multi_object:
                        self.chunk_location_dict.get(self.multi_object).append(
                            self.chunk_location)
                        self.chunk_location = []

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
                        # condition for search object - chunk_location position 1
                        # object ends with comma and new key, followed by a the other objects
                        # e.g. {target_obj: values, other_obj: values, ...}

                        if self.json[self.index - 2] != ',':
                            self.chunk_location.append(self.index - 1)
                        else:
                            self.chunk_location.append(self.index - 2)
                        if self.single_object:
                            # TODO: break operation when single obj search's condition matched
                            pass

                        if self.multi_object:
                            self.chunk_location_dict.get(
                                self.multi_object).append(self.chunk_location)
                            self.chunk_location = []

                if recursion is not None and self.obj_name:
                    # condition for search object - chunk_location position 0
                    current_str, location = self.parse_string()
                    matched = False
                    if isinstance(self.obj_name, str):
                        if not self.chunk_location and current_str == self.obj_name:
                            matched = True
                    elif isinstance(self.obj_name, list):
                        if not self.chunk_location and current_str in self.obj_name:
                            matched = True
                    else:
                        raise Exception(
                            'Invalid "obj_name" type, it should be a "str" or "list"')

                    # if current string matched with `obj_name`
                    if matched:
                        self.chunk_location.append(location)
                        self.recursion_depth = recursion
                        if current_str not in self.chunk_location_dict:
                            self.chunk_location_dict[current_str] = []
                        # if flag `multi_object` is True, assign current string to it as a cache
                        if self.multi_object:
                            self.multi_object = current_str

                else:
                    current_str = self.parse_string()[0]

                if not self.success:
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')

                # a ':'
                token = self.go_to_next_token()
                if token != self.COLON:
                    self.success = False
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')

                # a value
                value = self.scanner(recursion)
                if not self.success:
                    self.success = False
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')
                table[current_str] = value

    def parse_array(self, recursion: int = None) -> list:
        """ a '['
        """
        array = []
        self.go_to_next_token()

        while True:
            token = self.check_token()
            if token == self.NONE:
                self.success = False
                raise JsonSyntaxError(
                    f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')
            elif token == self.COMMA:
                self.go_to_next_token()
            elif token == self.ARR_CLOSE:
                self.go_to_next_token()
                break
            else:
                value = self.scanner(recursion)
                if not self.success:
                    raise JsonSyntaxError(
                        f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')
                array.append(value)
        return array

    def parse_string(self) -> tuple:
        # anything begin with `"`
        location_anchor = self.index

        self.ignore_white_space()
        string = ''
        done = False
        self.index += 1  # current index is `"`, +1 to move to string

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
                        # TODO: handling 32 bit unicode, reserved for future development when I have time
                        pass
            else:
                # build string a-zA-Z0-9
                string += char
        if not done:
            self.success = False
            raise JsonSyntaxError(
                f'Json syntax error at index {self.index}, character "{self.json[self.index]}"')

        if self.ratio_method:
            if self.deep == 1:
                # I am the group
                self.group = string
            elif self.deep == 2:
                # I am the subgroup
                self.skipped = False
                if isinstance(self.pattern, str):
                    self.sub = string
                elif isinstance(self.pattern, list) and len(self.pattern) == 2:
                    subgroup_ratio = self.ratio_method(string, self.pattern[0])
                    if subgroup_ratio < 0.33:
                        # `skipped` works on second level of recursion, AKA subgroup
                        # once `skipped` is True, parser will ignore current object
                        # and move to next object on second level of recursion
                        self.skipped = True
                    else:
                        self.sub = string
                elif isinstance(self.pattern, list) and len(self.pattern) == 1:
                    self.pattern = self.pattern[0]
                    self.sub = string
                else:
                    raise Exception('An invalid search pattern')

            elif self.deep == 3 and not self.is_var_value and not self.skipped:
                # I am a variable and a var_name, run ratio_method()
                # a variable representation in Json is `var_value: var_name`
                # the `ratio_method()` will be only applied on `var_name`, as
                # the `var_value` is usually in a short form
                if isinstance(self.pattern, str):
                    current_ratio = self.ratio_method(string, self.pattern)
                elif isinstance(self.pattern, list):
                    current_ratio = self.ratio_method(string, self.pattern[1])
                else:
                    raise Exception('An invalid search pattern')
                self.is_var_value = True

                if current_ratio > self.threshold:
                    if len(self.search_result) == self.result_length:
                        stored_ratio_result = [i[0] for i in
                                               self.search_result]
                        min_ratio = min(stored_ratio_result)
                        if current_ratio >= max(stored_ratio_result):
                            for index, item in enumerate(self.search_result):
                                if item[0] == min_ratio:
                                    self.search_result[index] = [current_ratio,
                                                                 self.group,
                                                                 self.sub,
                                                                 self.var_name,
                                                                 string]
                                    break
                        else:
                            pass
                    else:
                        self.search_result.append(
                            [current_ratio, self.group, self.sub,
                             self.var_name, string])
            elif self.deep == 3 and self.is_var_value and not self.skipped:
                # record var_value
                self.var_name = string
                self.is_var_value = False

        return string, location_anchor

    def parse_number(self) -> float or int:
        self.ignore_white_space()
        pointer = self.index
        is_float = False
        number = 0

        while pointer < self.length:
            if self.json[pointer] not in '0123456789+-.eE':
                break
            else:
                pointer += 1
                if self.json[pointer] in '.eE':
                    is_float = True

        try:
            number = float(self.json[self.index:pointer]) if is_float else int(
                self.json[self.index:pointer])
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
