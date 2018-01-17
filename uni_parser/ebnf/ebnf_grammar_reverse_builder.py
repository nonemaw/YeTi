import re
from uni_parser.ebnf.ebnf_ast import Ast


class EBNFGrammarReverseBuilder:
    """
    build provided EBNF grammars reversely based on AST tree
    """
    escape_list = re.compile(
        '\'([\.\*\+\?\-\^\$\|\{\}\(\)\[\]]{1,}|(\*\*=)|(\*=)|(\+=)|())\'')
    literal_finder = re.compile(
        '^ *\[Literal\(""".+?""", """\{\}"""\)\] *$', re.DOTALL)
    literal_finder2 = re.compile('Literal')
    g_literal_name_finder = re.compile(
        'Literal\("""(.+?)""", """\{\}""".*?\)', re.DOTALL)

    @staticmethod
    def build(ast: Ast, indent: int = 0) -> str:
        """
        name:     test
        children: [define, NEWLINE, define, NEWLINE, ... ]

        return:   `name1 = definition1
                   name2 = definition2
                   ...`
        """
        indent = ' ' * indent
        definitions = []
        if ast.children:
            for child in ast:
                if child.name == 'define':
                    name, definition = EBNFGrammarReverseBuilder.build_define(
                        child)
                    if len(EBNFGrammarReverseBuilder.literal_finder2.findall(
                            definition)) == 1 and EBNFGrammarReverseBuilder.literal_finder.findall(
                            definition):
                        definitions.append(f'{indent}{name} = {definition[1:-1].format(name)}\n')
                    else:
                        g_literal_name_list = [repr(name) for name in
                                               EBNFGrammarReverseBuilder.g_literal_name_finder.findall(
                                                   definition)]
                        definitions.append(f'{indent}{name} = Base({definition.format(*g_literal_name_list)}, name=\'{name}\')\n')
        return ''.join(definitions)

    @staticmethod
    def build_define(ast: Ast) -> tuple:
        """
        name:     define
        children: [NAME, DEF, expr]

        return:   (name, definition)
        """
        return ast[0].child, EBNFGrammarReverseBuilder.build_expr(ast[2])

    @staticmethod
    def build_expr(ast: Ast) -> str:
        """
        name:     expr
        children: [base_expr, ALT, base_expr, ALT, ... ]

        return:   `[G1, G2], [G3, G4, G5], [G6] ...`
        """
        return ', '.join(EBNFGrammarReverseBuilder.build_base_expr(child)
                         for child in ast if child.name != 'ALT')

    @staticmethod
    def build_base_expr(ast: Ast) -> str:
        """
        name:     base_expr
        children: [atom_expr, atom_expr, ... ]

        return:   `[G1, G2, G3 ...]`
        """
        return f"[{', '.join(EBNFGrammarReverseBuilder.build_atom_expr(child)for child in ast)}]"

    @staticmethod
    def build_atom_expr(ast: Ast) -> str:
        """
        name:     atom_expr
        children: [atom, repetition] or [atom]

        return:   `grammar`
        """
        grammar = EBNFGrammarReverseBuilder.build_atom(ast[0])
        if len(ast.children) > 1:
            # case 1: atom_expr with repetition
            return f'Group([{grammar}]{EBNFGrammarReverseBuilder.build_repetition(ast[1])})'
        else:
            # case 2: without repetition, can be a Group with default
            # repetition (`*`) or an atom with Literal
            if len(ast[0].children) > 1:
                # the default repetition case
                return f'Group([{grammar}], repeat=(1, 1))'
            return grammar

    @staticmethod
    def build_repetition(ast: Ast) -> str:
        """
        name:     repetition
        children: [PLUS]/[STAR]/[LREP, NUMBER1, NUMBER2, RREP]

        return:   `repetition`
        """
        if ast[0].name == 'PLUS':
            return ', repeat=(1, -1)'
        elif ast[0].name == 'STAR':
            return ''
        elif len(ast.children) > 1:
            if ast[2].name == 'NUMBER':
                return f', repeat=({ast[1].child}, {ast[2].child})'
            return f', repeat=({ast[1].child}, -1)'

    @staticmethod
    def build_atom(ast: Ast) -> str:
        """
        name:     atom
        children: [NAME]/[STRING]/[LGR, expr, RGR]

        return:   `atom_literal` (without name)
        """
        if ast[0].name == 'NAME':
            return f'Refer("""{ast[0].child}""")'

        elif ast[0].name == 'STRING':
            if ast[0].child == '{' or '}':
                ast[0].child = ast[0].child.replace('{', '{{').replace('}',
                                                                       '}}')

            match_result = EBNFGrammarReverseBuilder.escape_list.match(
                ast[0].child)
            if match_result and match_result.span()[1] == len(ast[0].child):
                return f'Literal("""{ast[0].child[1:-1]}""", """{{}}""", escape=True)'

            return f'Literal("""{ast[0].child[1:-1]}""", """{{}}""")'

        elif ast[0].name == 'LGR':
            return EBNFGrammarReverseBuilder.build_expr(ast[1])[1:-1]
