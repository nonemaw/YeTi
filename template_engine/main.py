import re
import ast
from uni_parser.reserved_names import ReservedNames


class XPLANSyntaxError(Exception):
    pass


class StmtError(Exception):
    pass


class ExprError(Exception):
    pass


class CodeBuilder:
    """
    basic code tools
    """
    INDENT_STEP = 4
    def __init__(self, indent: int = 0):
        self.code = []
        self.indent_level = indent

    def __str__(self):
        return ''.join(str(c) for c in self.code)

    def add_line(self, line: str):
        self.code.extend([' ' * self.indent_level, line, '\n'])

    def indent(self):
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def get_globals(self) -> dict:
        """
        magic method `exec()` for getting global names example:

        code = '''
        SEVENTEEN = 17

        def test():
            return 3
        '''
        global_namespace = {}
        exec(code, global_namespace)

        after the execution:
        global_namespace.get('SEVENTEEN')  # is 17
        global_namespace.get('test')       # is <function test>
        """

        # make sure the final indent is 0
        assert self.indent_level == 0

        code = str(self)
        global_namespace = {}

        print(code)

        exec(code, global_namespace)
        return global_namespace


class ContextManager:
    pass


class XPLAN:
    """
    template function:

    """
    def __init__(self, template_text: str, *func_contexts, template_tag: list,
                 print_tag: str = None, instance_tag: str = None,
                 imported: str = None, var_define: str = None,
                 iter_to_list: bool = False):
        self.template_text = template_text
        self.config(*func_contexts, template_tag=template_tag,
                    print_tag=print_tag, instance_tag=instance_tag,
                    imported=imported, var_define=var_define,
                    iter_to_list=iter_to_list)

    def load_template(self, template_text: str):
        self.template_text = template_text

    def config(self, *func_contexts, template_tag: list,
               print_tag: str = None, instance_tag: str = None,
               imported: str = None, var_define: str = None,
               iter_to_list: bool = False):
        self.context = {}
        self.all_vars = set()
        self.loop_vars = set()
        self.print_tag = print_tag
        self.instance_tag = instance_tag
        self.imported = imported
        self.var_define = var_define
        self.iter_to_list = iter_to_list

        self.module_name = None

        for c in func_contexts:
            self.context.update(c)
        try:
            self.template_tag = [t[:int(len(t) / 2)] for t in template_tag]
            self.template_close = [t[int(len(t) / 2):] for t in template_tag]
        except:
            raise Exception('Invalid template tag')

        if not self.imported or not self.instance_tag:
            self.instance_tag = None
            self.imported = None

        if self.imported:
            try:
                self.module_name = self.imported.split(' as ')[1].strip()
            except IndexError:
                self.instance_tag = None
                self.imported = None

    def syntax_error(self, msg, token):
        raise XPLANSyntaxError(f'{msg}: {repr(token)}')

    def record_var_name(self, name, vars_set: set):
        """
        put a var_name into the target var_set
        """
        if isinstance(name, str):
            if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
                self.syntax_error('Invalid name', name)
            vars_set.add(name)
        elif isinstance(name, list):
            for n in name:
                n = re.sub(',', '', n)
                if n:
                    if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", n):
                        self.syntax_error('Invalid name', n)
                    vars_set.add(n)

    def handle_dot(self, instance, *dots):
        for dot in dots:
            # try to handle method
            # e.g. my_method('abc', 'egf') ->
            #      args: ['abc', 'egf'], dot: my_method
            try:
                matched = re.search(r'^([a-zA-Z_]+)\((.+)\)$', dot)
                args = matched.group(2)
                dot = matched.group(1)
            except AttributeError:
                args = None
                dot = re.sub('\(\)$', '', dot)

            args = [arg.strip() for arg in args.split(',')] if args else []

            try:
                instance = getattr(instance, dot)
            except AttributeError:
                instance = instance[dot]

            if callable(instance):
                instance = instance(*args) if args else instance()

        if instance is None:
            return ''
        return instance

    def flush_output(self, code: CodeBuilder, buffered: list):
        """
        a closure for buffering strings: store string and append/extend to
        current code, then empty buffer
        """
        if len(buffered) == 1:
            code.add_line(f'append_result({buffered[0]})')
        elif len(buffered) > 1:
            code.add_line(f'extend_result([{", ".join(buffered)}])')
        del buffered[:]

    def split_template_text(self):
        template_string = '|'.join(f'{tag1}.*?{tag2}' for tag1, tag2 in zip(self.template_tag, self.template_close))
        re_string = f'(?s)({template_string})'
        tokens = re.split(re_string, self.template_text)

        last_token = None
        for index, token in enumerate(tokens):
            # clean up newline in tokens right after variable definition
            # and statements (such as if and for)
            if last_token is None:
                token_content = re.search('<:(.*):>', token)
                last_token = token_content.group(1).strip() if token_content else ''
                continue

            if token.startswith('\n'):
                # var define case, e.g.
                # <:let a = 1:>
                if last_token.startswith(self.var_define):
                    tokens[index] = token[1:]

                # statement case
                if last_token.startswith('if') or last_token.startswith('for'):
                    tokens[index] = token[1:]

            token_content = re.search('<:(.*):>', token)
            last_token = token_content.group(1).strip() if token_content else ''

        return tokens

    def handle_print(self, stmt: str) -> str:
        if not stmt.startswith(self.print_tag):
            return ''

    def handle_var_value(self, value: str):
        re_keyword = '|'.join(f'\\b{word}\\b' for word in ReservedNames.names)
        re_keyword = '|'.join([re_keyword, '|'.join(s for s in ReservedNames.operation_symbols)])

        # if key word contains statements (like generator) in value, e.g.
        #
        # "[x for x in range(10)]"
        # "[x for x in var_name]"
        # "2 + 4"
        # "'abc' + 'efg'"
        if re.search(re_keyword, value):
            try:
                return eval(value)
            except NameError:
                return value

        # normal value, can be a simple int, str, list, or dict in str format
        else:
            return ast.literal_eval(value)

    def handle_iter_to_list(self, stmt: str):
        """
        convert map, reduce, filter to list, for a compatibility with
        Python2.*'s operation, e.g. filter(func, iter)[0]

        e.g.

        map(func, filter(lambda x: str(x) in '0123456789', [1,2,3,4,5,99]))
        to
        list(map(func, list(filter(lambda x: str(x) in '0123456789', [1,2,3,4,5,99]))))
        """
        search = re.search(r"[^a-zA-Z]*(map|reduce|filter)[^a-zA-Z]", stmt)
        if search:
            start = search.start(1)
            end = search.end(1)
            func = search.group(1)

            # find the position of closed brackets
            temp = stmt[end:]
            stack = 0
            str_stack = []
            closed_position = 0
            for index, c in enumerate(temp):
                if (c == '(' or c == '{' or c == '[') and not str_stack:
                    stack += 1

                if (c == ')' or c == '}' or c == ']') and not str_stack:
                    stack -= 1

                if c == "'" or c == '"':
                    if str_stack and str_stack[-1] == c:
                        str_stack.pop()
                    else:
                        str_stack.append(c)

                if not stack:
                    closed_position = index + 1 + end
                    break

            return f'{stmt[:start]}list({func}{self.handle_iter_to_list(stmt[end:closed_position])}){self.handle_iter_to_list(stmt[closed_position:])}'
        else:
            return stmt

    def handle_stmt(self, stmt: str, test_stmt: bool = False,
                    code: CodeBuilder = None):
        """
        processing simple one-line statement: pipeline or dot operation

        a stmt is the string between two template tags, e.g.:

        let my_name = 'huang'
        =my_name|upper
        user.username
        =$client.name
        """
        # can access imported instance, use instance_tag to call instance
        # replace all instance_tag with instance name
        if self.instance_tag and self.module_name:
            stmt = re.sub('\$([a-zA-Z_]+)', f'{self.module_name}.\\1', stmt)

        if test_stmt:
            if stmt.startswith('end') or stmt.startswith('if') or stmt.startswith('for') and not stmt.startswith('let'):
                raise StmtError('Stmt contains keyword, switch to Expr')

            # if print_tag is provided
            if self.print_tag:
                # if the stmt has no print_tag
                if not stmt.startswith(self.print_tag):
                    # add variable to context if it's a var definition
                    if self.var_define and stmt.startswith(self.var_define):
                        if code:
                            code.add_line(re.sub(self.var_define, '', stmt).strip())
                            return '_VAR_DEF'
                        else:
                            return '_VAR_DEF'

                    # return empty string if the syntax has no print_tag
                    else:
                        return ''

                # if the syntax has print_tag, handle it
                else:
                    stmt = re.sub(self.print_tag, '', stmt).strip()

            # if no print_tag is provided, treat every stmt as "printed"
            else:
                if self.var_define and stmt.startswith(self.var_define):
                    if code:
                        code.add_line(re.sub(self.var_define, '', stmt).strip())
                        return '_VAR_DEF'
                    else:
                        return '_VAR_DEF'
                else:
                    stmt = stmt

        if '|' in stmt:
            pipes = stmt.split('|')
            code = self.handle_stmt(pipes[0])
            for pipe_func in pipes[1:]:
                # put the piped function into var list
                self.record_var_name(pipe_func, self.all_vars)
                code = f'{pipe_func}({code})'

        # elif '.' in stmt:
        #     # when doing `x.y` meas either `x.y` or `x['y']`
        #     #
        #     # therefore, for example, doing `x.y.z`, we just throw `x`, `y` and
        #     # `z` to method `handle_dot()` as `handle_dot(x, y, z)` and try which
        #     # way will work
        #     outsider = re.search('^([a-zA-Z_]+)\((.+\..+)\)', stmt)
        #     outside_function = None
        #     if outsider:
        #         outside_function = outsider.group(1)
        #         stmt = outsider.group(2)
        #
        #     dots = stmt.split('.')
        #     code = self.handle_stmt(dots[0])
        #     args = ', '.join(repr(d) for d in dots[1:])
        #
        #     if not outside_function:
        #         code = f'handle_dot({code}, {args})'
        #     else:
        #         code = f'{outside_function}(handle_dot({code}, {args}))'

        else:
            code = f'{stmt}'

        return code

    def handle_expr(self, expr: list, token: str, ops_stack: list,
                    code: CodeBuilder, diff_end: bool):
        """
        processing expressions such as if/for/lambda

        a token is a string of template text:
            {{ for topic in topics }}

        a expr is a list of split token:
            ['for', 'topic', 'in', 'topics']
        """

        # a if expression is:
        # if stmt
        if expr[0] == 'if':
            ops_stack.append('if')
            code.add_line(f'if {self.handle_stmt(" ".join(expr[1:]))}:')
            code.indent()

        # a for expression is:
        # for var in stmt
        #
        # e.g.
        # for var1, var2 in stmt
        elif expr[0] == 'for':
            ops_stack.append('for')

            if expr.index('in') != 2:
                self.record_var_name(expr[1:expr.index('in')], self.loop_vars)
                code.add_line(
                    f'for {" ".join(expr[1:expr.index("in")])} in {self.handle_stmt(" ".join(expr[expr.index("in") + 1:]))}:'
                )
            else:
                self.record_var_name(expr[1], self.loop_vars)
                code.add_line(
                    f'for {expr[1]} in {self.handle_stmt(expr[3])}:'
                )
            code.indent()

        elif expr[0].startswith('end'):
            # an end tag can followed by a comment
            if len(expr) != 1 and not expr[1].startswith('#'):
                self.syntax_error('Invalid end tad', token)

            if not ops_stack:
                self.syntax_error('Too many ends', token)
            if diff_end:
                end_what = expr[0][3:]
                start_what = ops_stack.pop()
                if start_what != end_what:
                    self.syntax_error('Mismatched end tag', end_what)
            else:
                ops_stack.pop()
            code.dedent()

        else:
            self.syntax_error('Unknown tag', expr[0])

    def render(self, context = None, diff_end: bool = False):
        if context:
            self.context.update(context)
            for key in context:
                self.all_vars.add(key)

        self.builder(diff_end)
        return self._render_function(self.context, self.handle_dot)

    def builder(self, diff_end: bool):
        code = CodeBuilder()
        code.add_line('def render_function(context, handle_dot):')
        code.indent()
        if self.imported:
            code.add_line(self.imported)
        code.add_line('result = []')
        # var name `append_result` as function `list.append()`
        # var name `extend_result` as function `list.extend()`
        code.add_line('append_result = result.append')
        code.add_line('extend_result = result.extend')

        # code section for storing variable context
        vars_code = code.add_section()
        # stack for `if`, `for`, etc.
        ops_stack = []
        buffered = []
        tokens = self.split_template_text()

        for token in tokens:

            # skip comment lines
            if any(token.startswith(''.join([tag, '#'])) for tag in self.template_tag):
                continue

            # if both stmt tag and expr tag are provided
            if len(self.template_tag) > 1:
                if token.startswith(self.template_tag[0]):
                    # simple statement: variable/pipeline/dot operation
                    # statement tag is self.template_tag[0]
                    stmt = self.handle_stmt(token[2:-2].strip(), code=code)
                    if stmt != '_VAR_DEF':
                        buffered.append(f'str({stmt})')

                elif token.startswith(self.template_tag[1]):
                    # expressions
                    # statement tag is self.template_tag[1], or self.template_tag[0] if
                    # only one tag provided
                    self.flush_output(code, buffered)
                    expr = token[2:-2].strip().split()
                    self.handle_expr(expr, token, ops_stack, code, diff_end)

                else:
                    buffered.append(repr(token))

            # if only one tag is provided
            else:
                if token.startswith(self.template_tag[0]):
                    # simple statement: variable/pipeline/dot operation
                    # statement tag is self.template_tag[0]
                    #
                    # try to handle stmt, set test_stmt flag to True
                    # if exception raised, turn to handle_expr
                    try:
                        stmt = self.handle_stmt(token[2:-2].strip(),
                                                test_stmt=True, code=code)
                    except:
                        # handle_expr
                        # statement tag is still self.template_tag[1] when only
                        # one tag provided
                        self.flush_output(code, buffered)
                        expr = token[2:-2].strip().split()
                        self.handle_expr(expr, token, ops_stack, code, diff_end)

                    else:
                        # if no exception raised in try, proceed this stmt
                        if stmt != '_VAR_DEF':
                            buffered.append(f'str({stmt})')

                else:
                    buffered.append(repr(token))

        if ops_stack:
            self.syntax_error('Mismatched operation tag', ops_stack[-1])

        self.flush_output(code, buffered)

        # some variables are from context, e.g. `user_name` and `product_list`,
        # they are pre-defined in all_vars
        # some variables are only in loop, e.g. `product`
        # they are updated when handling loop/condition
        #
        # hence all variable are in all_vars but not in loop_vars are needed
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line(f'{var_name} = context[{repr(var_name)}]')

        code.add_line('return "".join(result)')
        code.dedent()

        # get `render_function` from `global_namespace`
        # now `_render_function` is a ready-to-use function now
        self._render_function = code.get_globals()['render_function']


if __name__ == '__main__':
    xplan = XPLAN(
'''
<:let abc = list(filter(lambda x: x % 2, [1,2,3,4,5,6,7,8,9,0])):>
<:let topics = zip(['ML', 0, True],['PY', 1, False]):>
<:=my_name|upper|lower:>!
<:=my_name:>!
<:=abc.append(99):>
<: for i in abc :>
    <:=i:>
<: end #end of for:>
<:for trust in $trust:>
<:let aa = 999999999:>
    <:=trust.name:>
    <:=trust:>
    <:=aa:>
<:end:>
<:let client = 'abcd':>
<:=client.upper().lower():>
<:=$client.sample_method('abcd').upper():>
<:=str(list(filter(lambda x: x % 2, map(int, [1, 2, 3, 4, 5, 6, 7])))).upper():>




<:if float(list(map(lambda x: x.startswith('(') and ('-'+x[1:]) or x, list(filter(lambda x: x in '0123456789.(', $client.sample_method(['1', '2', '3', '4', '5'])))))[0]):>
fdsafsdfd
<:end:>
''',
        {'upper': str.upper, 'lower': str.lower},
        template_tag=['<::>'],
        print_tag='=',
        instance_tag='$',  # call imported class instance
        imported='import template_engine.global_context as entity',  # must be ended with "as xxx", in order to call module's content
        var_define='let',
        iter_to_list=True
    )

    text = xplan.render({
        'my_name': "abc",
        'my_ass': 'butt'
    },
        diff_end=False)

    print(text)

