
"""
A mini XPLAN template parser

based on 500L's Templite
"""


import re


class SyntaxError(ValueError):
    pass


class CodeBuilder:
    def __init__(self, indent=0):
        self.code = []
        self.indent = indent

    def __str__(self):
        """ convert source code into a single string
        """
        return "".join(str(c) for c in self.code)

    def _add_line(self, line):
        self.code.extend([" " * self.indent, line, "\n"])

    def _add_section(self):
        """ add a section to current code
        """
        section = CodeBuilder(self.indent)
        self.code.append(section)
        return section

    def _indent(self):
        self.indent += 4

    def _dedent(self):
        self.indent -= 4

    def _get_globals(self):
        """ execute the code, and return a dict of globals it defines, e.g.:

        global_namespace = {}
        python_source = '''\
        SEVENTEEN = 17
        def fun_three():
            return 3
        '''

        In [28]: exec(python_source, global_namespace)
        In [31]: global_namespace['SEVENTEEN']
        Out[31]: 17
        In [32]: global_namespace['fun_three']
        Out[32]: <function fun_three>
        """
        assert self.indent == 0  # check if the indent is closed
        python_source = str(self)  # call __str__() to convert code into string
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace


class XPLAN:
    """A simple template renderer, for a nano-subset of Django syntax.

    Supported constructs are extended variable access::
        {{var.modifer.modifier|filter|filter}}

    define variable::
        <:let var = value:>

    loops::
        {% for var in list %}...{% endfor %}
        <:for var in list:>...<:end:>

    ifs::
        {% if var %}...{% endif %}
        <:if var:>...<:end:>

    Comments are within curly-hash markers::
        {# This will be ignored #}
        <:#This will be ignored#:>

    Construct a Templite with the template text, then use `render` against a
    dictionary context to create a finished string::

        templite = Templite('''
            <h1>Hello {{name|upper}}!</h1>
            {% for topic in topics %}
                <p>You are interested in {{topic}}.</p>
            {% endif %}
            ''',
            {'upper': str.upper},
        )
        text = templite.render({
            'name': "Ned",
            'topics': ['Python', 'Geometry', 'Juggling'],
        })

    """
    def __init__(self, text, *contexts):
        """Construct a Templite with the given `text`.

        `contexts` are dictionaries of values to use for future renderings.
        These are good for filters and global values.

        *contexts will accept any number of variables and pass them into a
        tuple as "contexts", for example:
        x = XPLAN(template_text)
        x = XPLAN(template_text, context1)
        x = XPLAN(template_text, context1, context2, context3, ...)
        """
        self.context = {}
        for context in contexts:
            self.context.update(context)
        self.all_vars = set()
        self.loop_vars = set()

        # We construct a function in source form, then compile it and hold onto
        # it, and execute it to render the template.
        code = CodeBuilder()
        code._add_line("def render_function(context, do_dots):")
        code._indent()
        vars_code = code._add_section()
        code._add_line("result = []")
        code._add_line("append_result = result.append")
        code._add_line("extend_result = result.extend")
        code._add_line("to_str = str")

        ops_stack = []  # operation stack, e.g. push 'if' for if condition, pop 'if' when end
        buffered = []
        def flush_output():
            if len(buffered) == 1:
                code._add_line("append_result({})".format(buffered[0]))
            elif len(buffered) > 1:
                code._add_line("extend_result([{}])".format(", ".join(buffered)))
            del buffered[:]


        """ split the text into pieces, e.g.:
        text = 'literal1 <:let name = 1:>: <:for t in topics:><:=t:>, <:end:>literal2'
        re.split(r"(?s)(<:.*?:>|<:#.*?#:>)", text)
        [
            'literal1 ',            # literal
            '<:let name = 1:>',     # expression, create variable
            ': ',                   # literal
            '<:for t in topics:>',  # expression, push 'for' to stack
            '',                     # literal
            '<:=t:>',               # expression, display variable
            ', ',                   # literal
            '<:end:>',              # end tag, pop 'for' from stack
            'literal2'              # literal
         ]
        
        NOTE: (?s) means DOTALL mode (except JS and Ruby), which makes the dot
        "." matches new line characters (\r\n). "." does not match new line by
        default. Also known as "single-line mode" because the dot treats the
        entire input as a single line
        """
        tokens = re.split(r"(?s)(<:=.*?:>|<:.*?:>|<:#.*?#:>)",text)

        for token in tokens:
            if token.startswith('<:#'):
                # comment, ignore
                continue

            elif token.startswith('<:=') or token.startswith('<:let'):
                # an expression to be evaluated, to "buffered"
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str({})".format(expr))

            elif token.startswith('<:if') or token.startswith('<:for') or token.startswith('<:end'):
                flush_output()
                if token.startswith('<:if'):
                    # if statement
                    # <:if long_condition:> -> ['', 'long_condition']
                    words = token[2:-2].strip().split('if ')
                    if len(words) != 2:
                        self._syntax_error("\"if\" statement is broken", token)
                    ops_stack.append('if')
                    code._add_line("if {}:".format(self._expr_code(words[1])))
                    code._indent()
                elif token.startswith('<:for'):
                    # for statement, var to "loop_vars"
                    # <:for t in long_topics:> -> [['', 't'], 'long_topics']
                    words = token[2:-2].strip().split(' in ')
                    var = words[0].strip().split('for ')
                    if len(var) != 2:
                        self._syntax_error("\"for\" statement is broken", token)
                    ops_stack.append('for')
                    self._variable(var[1], self.loop_vars)
                    code._add_line(
                        "for c_{} in {}:".format(
                            var[1],
                            self._expr_code(words[1])
                        )
                    )
                    code._indent()
                elif token.startswith('<:end'):
                    # statement ends, operate pop
                    # <:end:> -> ['end']
                    words = token[2:-2].strip().split()
                    if len(words) != 1:
                        self._syntax_error("\"end\" tag is broken", token)
                    if not ops_stack:
                        self._syntax_error("\"end\" tag is redundant", token)
                    ops_stack.pop()
                    code._dedent()
                else:
                    self._syntax_error("Unknown tag", token)
            else:
                # literal text content
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error("Tags not closed", ops_stack[-1])

        flush_output()

        for var_name in self.all_vars - self.loop_vars:
            vars_code._add_line("c_{} = context[{}]".format(str(var_name), repr(var_name)))

        code._add_line("return ''.join(result)")
        code._dedent()
        self._render_function = code._get_globals()['render_function']

    def _expr_code(self, expr):
        """ enerate a Python expression for `expr`
            evaluate <:let, <:=, <:if, <:for
        """
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
        elif "." in expr:
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

    def _syntax_error(self, msg, thing):
        """Raise a syntax error using `msg`, and showing `thing`."""
        raise SyntaxError("{}: {}".format(msg, thing))

    def _variable(self, name, vars_set):
        """Track that `name` is used as a variable.

        Adds the name to `vars_set`, a set of variable names.

        Raises an syntax error if `name` is not a valid name.

        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def render(self, context=None):
        """Render this template by applying it to `context`.

        `context` is a dictionary of values to use in this rendering.

        """
        # Make the complete context we'll use.
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots):
        """Evaluate dotted expressions at runtime."""
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
