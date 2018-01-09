class Ast:
    def __init__(self, name: str, token_position: tuple, grammars: list = None,
                 grammar: str = None):
        """
        I am an AST tree, grammars are my children

        `grammars` can be both a spelling string, or a list of Ast instance
        """
        # matched grammar object name
        self.name = name
        self.children = grammars
        self.child = grammar
        # (line_start, char_start, line_end, char_end)
        self.position = token_position

    def __str__(self):
        return f'{self.name} {self.children} {self.print_position()}'

    def __repr__(self):
        return f'{self.name}'

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, item):
        if self.children:
            return self.children.__getitem__(item)
        else:
            return self.child

    def empty(self):
        self.children.clear()

    def append(self, obj):
        self.children.append(obj)

    def extend(self, obj):
        self.children.extend(obj.children)

    def print_position(self) -> str:
        return f'{self.position[0]}({self.position[1]})...{self.position[2]}({self.position[3]})'

    def format(self, level=4):
        indent = ' ' * level
        end_indent = ' ' * (level - 4)
        if self.child:
            child = 'CR' if self.child == '\n' else self.child
            return f'{self.name} < {child} >\n'
        else:
            next_indent = ' ' * level
            children = next_indent.join(
                map(lambda ast: ast.format(level + 4), self))
            return f'{self.name} {{\n{indent}{children}{end_indent}}}\n'
