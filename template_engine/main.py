import re
import ast
from uni_parser.reserved_names import ReservedNames


class XPLANSyntaxError(Exception):
    pass


class StmtError(Exception):
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
                 display_tag: str = None, var_define: str = None):
        self.template_text = template_text
        self.context = {}
        self.all_vars = set()
        self.loop_vars = set()
        self.display_tag = display_tag
        self.var_define = var_define
        for c in func_contexts:
            self.context.update(c)
        try:
            self.template_tag = [t[:int(len(t) / 2)] for t in template_tag]
            self.template_close = [t[int(len(t) / 2):] for t in template_tag]
        except:
            raise Exception('Invalid template tag')

    def _syntax_error(self, msg, token):
        raise XPLANSyntaxError(f'{msg}: {repr(token)}')

    def record_var_name(self, name, vars_set):
        """
        put a var_name into the target var_set
        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error('Invalid name', name)
        vars_set.add(name)

    def handle_dot(self, value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]

            if callable(value):
                value = value()
        return value

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
        return re.split(re_string, self.template_text)

    def handle_print(self, stmt: str) -> str:
        if not stmt.startswith(self.display_tag):
            return ''

    def handle_var_value(self, value: str):
        re_keyword = '|'.join(f'\\b{word}\\b' for word in ReservedNames.names)
        re_keyword = '|'.join([re_keyword, '|'.join(s for s in ReservedNames.operation_symbols)])

        print(self.all_vars)
        print(self.loop_vars)
        print(self.context)

        # if key word contains statements (like generator) in value, e.g.
        #
        # "[x for x in range(10)]"
        # "2 + 4"
        # "'abc' + 'efg'"
        if re.search(re_keyword, value):
            return eval(value)

        # normal value, can be a simple int, str, list, or dict in str format
        else:
            return ast.literal_eval(value)

    def handle_stmt(self, stmt: str, test_stmt: bool = False):
        """
        processing simple one-line statement: pipeline or dot operation

        a stmt is the string between two template tags, e.g.:

        let my_name= = 'huang'
        =my_name|upper
        user.username
        """
        if test_stmt:
            re_keyword = '|'.join(f'\\b{word}\\b' for word in ReservedNames.names)
            if stmt.startswith('end') or (re.search(re_keyword, stmt) and not stmt.startswith('let')):
                raise StmtError('Stmt contains keyword, switch to Expr')

            # if current syntax is a stmt and display_tag is provided
            if self.display_tag:

                if not stmt.startswith(self.display_tag):
                    # add variable to context if it's a var definition
                    if self.var_define and stmt.startswith(self.var_define):
                        stmt = re.sub(self.var_define, '', stmt).strip().split('=')
                        if len(stmt) != 2:
                            raise StmtError('Invalid variable creation syntax')
                        var_name = stmt[0].strip()
                        var_value = self.handle_var_value(stmt[1].strip())
                        self.context[var_name] = var_value
                        return ''

                    # return None if the syntax has no display_tag
                    else:
                        return ''

                # if the syntax has display_tag, handle it
                else:
                    stmt = re.sub(self.display_tag, '', stmt).strip()

        if '|' in stmt:
            pipes = stmt.split('|')
            code = self.handle_stmt(pipes[0])
            for pipe_func in pipes[1:]:
                # put the piped function into var list
                self.record_var_name(pipe_func, self.all_vars)
                code = f'c_{pipe_func}({code})'

        elif '.' in stmt:
            # when doing `x.y` meas either `x.y` or `x[y]` in Python
            #
            # therefore, for example, doing `x.y.z`, we just throw `x`, `y` and
            # `z` to method `handle_dot()` as `handle_dot(x, y, z)` and try which
            # way will work
            dots = stmt.split('.')
            code = self.handle_stmt(dots[0])
            args = ', '.join(repr(d) for d in dots[1:])
            code = f'handle_dot({code}, {args})'

        else:
            self.record_var_name(stmt, self.all_vars)
            code = f'c_{stmt}'

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
        if expr[0] == 'if':
            if len(expr) != 2:
                self._syntax_error('Invalid if condition', token)
            ops_stack.append('if')
            code.add_line(f'if {self.handle_stmt(expr[1])}:')
            code.indent()

        elif expr[0] == 'for':
            if len(expr) != 4:
                self._syntax_error('Invalid for condition', token)
            ops_stack.append('for')
            self.record_var_name(expr[1], self.loop_vars)
            code.add_line(
                f'for c_{expr[1]} in {self.handle_stmt(expr[3])}:'
            )
            code.indent()

        elif expr[0].startswith('end'):
            # an end tag can followed by a comment
            if len(expr) != 1 and not expr[1].startswith('#'):
                self._syntax_error('Invalid end tad', token)

            if not ops_stack:
                self._syntax_error('Too many ends', token)
            if diff_end:
                end_what = expr[0][3:]
                start_what = ops_stack.pop()
                if start_what != end_what:
                    self._syntax_error('Mismatched end tag', end_what)
            else:
                ops_stack.pop()
            code.dedent()

        else:
            self._syntax_error('Unknown tag', expr[0])

    def render(self, context = None, diff_end: bool = False):
        if context:
            self.context.update(context)
        self.builder(diff_end)
        return self._render_function(self.context, self.handle_dot)

    def builder(self, diff_end: bool):
        code = CodeBuilder()
        code.add_line("def render_function(context, handle_dot):")
        code.indent()
        code.add_line("result = []")
        # var name `append_result` as function `list.append()`
        # var name `extend_result` as function `list.extend()`
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")

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
                    stmt = self.handle_stmt(token[2:-2].strip())
                    buffered.append(f'str({stmt})')

                elif token.startswith(self.template_tag[1]):
                    # expressions
                    # statement tag is self.template_tag[1], or self.template_tag[0] if
                    # only one tag provided
                    self.flush_output(code, buffered)
                    expr = token[2:-2].strip().split()
                    self.handle_expr(expr, token, ops_stack, code, diff_end)

                else:
                    if token:
                        buffered.append(repr(token))

            # if only one tag is provided
            else:
                if token.startswith(self.template_tag[0]):
                    # simple statement: variable/pipeline/dot operation
                    # statement tag is self.template_tag[0]
                    #
                    # try to handle stmt, if exception raised, turn to handle
                    # expr
                    try:
                        stmt = self.handle_stmt(token[2:-2].strip(),
                                                test_stmt=True)
                    except:
                        # expressions
                        # statement tag is still self.template_tag[1] when only
                        # one tag provided
                        self.flush_output(code, buffered)
                        expr = token[2:-2].strip().split()
                        self.handle_expr(expr, token, ops_stack, code, diff_end)

                    else:
                        # if no exception raised in try
                        # proceed this stmt
                        buffered.append(f'str({stmt})')

                else:
                    if token:
                        buffered.append(repr(token))

        if ops_stack:
            self._syntax_error('Mismatched operation tag', ops_stack[-1])

        self.flush_output(code, buffered)

        # some variables are from context, e.g. `user_name` and `product_list`,
        # they are pre-defined in all_vars
        # some variables are only in loop, e.g. `product`
        # they are updated when handling loop/condition
        #
        # hence all variable are in all_vars but not in loop_vars are needed
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line(f'c_{var_name} = context[{repr(var_name)}]')

        code.add_line('return "".join(result)')
        code.dedent()

        # get `render_function` from `global_namespace`
        # now `_render_function` is a ready-to-use function now
        self._render_function = code.get_globals()['render_function']


if __name__ == '__main__':
    templite = XPLAN(
'''
<:let abc = list(map(lambda x: x % 2, [1,2,3,4,5,6,7,8,9,0])):>
<:let topics = ['ML', 'PY', 'DA']:>
Hello <:=my_name|upper:>!
Hello <:=my_name:>!
<:=abc:>
<: for topic in topics :>
    You are interested in <:=topic:>
    <:let bbs = [c for c in topic]:>
    <:#let bbs = ['aa', 'bb', 'cc']:>
    <: for bb in bbs :>
        haha <:=bb:>
    <:end:>
<: end #end of for:>
''',
        {'upper': str.upper},
        template_tag=['<::>'],
        display_tag='=',
        var_define='let'
    )

    text = templite.render({
        'my_name': "abc",
    },
        diff_end=False)

    print(text)


def render_function(context, handle_dot):
    result = []
    append_result = result.append
    extend_result = result.extend
    c_my_name = context['my_name']
    c_abc = context['abc']
    c_topics = context['topics']
    c_bbs = context['bbs']
    c_upper = context['upper']
    extend_result(['\n', str(), '\n', str(), '\nHello ', str(c_upper(c_my_name)), '!\nHello ', str(c_my_name), '!\n', str(c_abc), '\n'])
    for c_topic in c_topics:
        extend_result(['\n    You are interested in ', str(c_topic), '\n    ', '\n    ', str(), '\n    '])
        for c_bb in c_bbs:
            extend_result(['\n        haha ', str(c_bb), '\n    '])
        append_result('\n')
    append_result('\n')
    return "".join(result)
