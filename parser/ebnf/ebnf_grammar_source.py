from ebnf.ebnf_grammar_obj import *
from ebnf.errors import GrammarNotExists, SyntaxError


class EBNFAtom:
    # match the `name` of a grammar
    NAME    = LiteralGrammar(re.compile('[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*'), 'NAME')
    # match the value of `number` of a grammar
    NUMBER  = LiteralGrammar(re.compile('-?[0-9]{0,10}'), 'NUMBER')
    # match the value of `string` of a grammar, with format in `' ... '`
    STRING  = LiteralGrammar(re.compile('\'[\w\W]*?\''), 'STRING')  # which already includes some atoms like 'True', ',', '.', etc.

    NEWLINE = LiteralGrammar(r'\n', 'NEWLINE')
    STAR    = LiteralGrammar('*', 'STAR', escape=True)
    PLUS    = LiteralGrammar('+', 'PLUS', escape=True)
    ALT     = LiteralGrammar('|', 'ALT', escape=True)
    EXCEP   = LiteralGrammar('-', 'EXCEP', escape=True)
    LREP    = LiteralGrammar('{', 'LREP', escape=True)
    RREP    = LiteralGrammar('}', 'RREP', escape=True)
    LGR     = LiteralGrammar('(', 'LGR', escape=True)
    RGR     = LiteralGrammar(')', 'RGR', escape=True)
    LOP     = LiteralGrammar('[', 'LOP', escape=True)
    ROP     = LiteralGrammar(']', 'ROP', escape=True)
    DEF     = LiteralGrammar('::=', 'DEF', escape=True)  # DEF should be assigned manually
    EPSILON_EXPR = LiteralGrammar('_e', 'EPSILON_EXPR', escape=True)
    EPSILON      = EpsilonGrammar()


class EBNF:
    # `test` is the top level statement
    # `test`: (( `\n` )* (define)+ ( `\n` )*)+
    test = BaseGrammar(
        [
            GroupGrammar(
                [
                    GroupGrammar(
                        [EBNFAtom.NEWLINE],
                    ),
                    GroupGrammar(
                        [Refer('define')],
                        repeat=(1, -1)
                    ),
                    GroupGrammar(
                        [EBNFAtom.NEWLINE],
                    ),
                ],
                repeat=(1, -1)
            ),
        ],
        name='test'
    )

    # `define`: NAME '::=' expr
    define = BaseGrammar(
        [
            EBNFAtom.NAME,
            EBNFAtom.DEF,
            Refer('expr')
        ],
        name='define'
    )

    # `repetition`: '+' | '*' | '{' n1 n2 '}'
    # [ expr ] was handled in token scanner, will be convert to ( expr ){0, 1}
    repetition = BaseGrammar(
        [EBNFAtom.PLUS],
        [EBNFAtom.STAR],
        [
            EBNFAtom.LREP,
            GroupGrammar(
                [
                    EBNFAtom.NUMBER
                ],
                repeat=(1, 2)
            ),
            EBNFAtom.RREP
        ],
        name='repetition'
    )

    # `expr`: base_expr ( '|' base_expr )*
    expr = BaseGrammar(
        [
            Refer('base_expr'),
            GroupGrammar(
                [
                    EBNFAtom.ALT,
                    Refer('base_expr')
                ],
            ),

        ],
        name='expr'
    )

    # `base_expr`: ( atom_expr )+
    base_expr = BaseGrammar(
        [
            GroupGrammar(
                [Refer('atom_expr')],
                repeat=(1, -1)
            )
        ],
        name='base_expr'
    )

    # `atom_expr`: atom ( '+' | '*' | {x, x} )*
    atom_expr = BaseGrammar(
        [
            Refer('atom'),
            GroupGrammar([Refer('repetition')])
        ],
        name='atom_expr'
    )

    # `atom`: NAME | STRING | '(' expr ')' | EPSILON
    atom = BaseGrammar(
        [EBNFAtom.NAME],
        [EBNFAtom.STRING],
        [
            EBNFAtom.LGR,
            Refer('expr'),
            EBNFAtom.RGR
        ],
        [EBNFAtom.EPSILON_EXPR],
        name='atom'
    )

    tracker = BuildTracker({
        'test': test,
        'define': define,
        'repetition': repetition,
        'expr': expr,
        'base_expr': base_expr,
        'atom_expr': atom_expr,
        'atom': atom,
    })

    @staticmethod
    def eliminate_i_lr(tracker:BuildTracker):
        """
        accept a tracker instance, format indirect left recursion to direct left recursion

        A ::= C X
        B ::= C Y
        C ::= A | B | Z
        ==>
        C ::= C X | C Y | Z
        """
        # TODO
        path_stack = []

        pass

    @staticmethod
    def eliminate_lr(tracker:BuildTracker):
        """
        accept a tracker instance, for eliminating direct left recursion

        E ::= E A B | E C D | F | G
                   expr1    , expr2
        ==>
        E ::= F E_LR | G E_LR
        E_LR ::= A B E_LR | C D E_LR | epsilon
        """
        expr1 = []
        expr2 = []

        # use `list()` force a copy of keys into a list rather than an iterator
        # otherwise error is thrown during operation to the dictionary
        for key in list(tracker):

            # `self` is a BaseGrammar or GroupGrammar instance
            self = tracker.grammars.get(key)
            if isinstance(self, BaseGrammar):
                if self.grammars[0][0].name == self.name:

                    # eliminate direct left recursion
                    for grammar_list in self.grammars:
                        if grammar_list[0].name == self.name:
                            temp_list = grammar_list[1:]
                            temp_list.append(Refer(f'_{self.name}'))
                            expr1.append(temp_list)
                        else:
                            temp_list = grammar_list
                            temp_list.append(Refer(f'_{self.name}'))
                            expr2.append(temp_list)

                    # expand the two expr list into *args
                    del tracker.grammars[self.name]
                    tracker.grammars[self.name] = \
                        BaseGrammar(*expr1,
                                    name=self.name)
                    tracker.grammars[f'_{self.name}'] = \
                        BaseGrammar(*expr2,
                                    [EBNFAtom.EPSILON],
                                    name=f'_{self.name}')

    @staticmethod
    def build(tracker:BuildTracker, *grammars, debug=0):
        """
        build entry point

        set `debug` to `1` to print productions of all grammars
        """
        EBNF.eliminate_lr(tracker)
        EBNF.eliminate_i_lr(tracker)

        if not grammars:
            tracker['test'].build(tracker)
        else:
            for grammar in grammars:
                try:
                    _grammar = tracker[grammar]
                except:
                    raise GrammarNotExists(f'Unknown EBNF grammar \'{grammar}\'.')
                else:
                    if isinstance(_grammar, BaseGrammar):
                        _grammar.build(tracker)
        if debug:
            for grammar in tracker:
                if isinstance(tracker[grammar], BaseGrammar):
                    print(tracker[grammar].print_productions())

    @staticmethod
    def match(tracker:BuildTracker, lexer:Lexer, grammar:str=None, debug=0) -> Ast:
        """
        match entry point

        set `debug` to `1` to enable debug message with recursion indent
        """
        if not grammar:
            result = tracker.grammars.get('test').match(lexer, debug)
        else:
            result = tracker.grammars.get(grammar).match(lexer, debug)
        if not (lexer.scanner.look_ahead(1) == '_EOF'or lexer.current_token == '_EOF') or not result:
            if not result:
                raise SyntaxError(
f"""\n    Syntax Error while parsing, around line {lexer.current_token.position[0]}[{lexer.current_token.position[1]}] ... line {lexer.last_token.position[2]}[{lexer.last_token.position[3]}], near spelling < {repr(lexer.current_token.spelling)} >""")
            else:
                raise SyntaxError(
f"""\n    Syntax Error while parsing, around line {lexer.current_token.position[0]}[{lexer.current_token.position[1]}] ... line {lexer.last_token.position[2]}[{lexer.last_token.position[3]}], near spelling < {repr(lexer.current_token.spelling)} >
    {result.format()}""")

        return result
