from uni_parser.ebnf.errors import UnknownGrammarObj
from uni_parser.ebnf.ebnf_ast import Ast
from uni_parser.ebnf.ebnf_build_tools import Lexer, BuildTracker
from uni_parser.token_source import TokenType
from uni_parser.reserved_names import *
import re


class EpsilonGrammar:
    def __init__(self):
        self.name = 'EPSILON'
        self.regex = '_e'
        self.recursion = False

    def __str__(self):
        return f'<{self.name}>'

    def __repr__(self):
        return str(self)

    def match(self, *args, **kwargs):
        # epsilon always returns mark '_E' when a token comes
        return '_E'


class LiteralGrammar:
    def __init__(self, regex, name: str = None, escape: bool = False):
        self.escape = escape
        if name:
            self.name = name
        else:
            self.name = regex
        if escape:
            self.regex = re.escape(regex)
        else:
            self.regex = regex
        self.recursion = False

    def __str__(self):
        return f'<{self.name}>'

    def __repr__(self):
        return str(self)

    def match(self, lexer: Lexer, debug: int = 0):
        # the most fundamental match() function:
        # match current_token's spelling with LiteralGrammar's regex text
        if lexer.current_token is None or lexer.current_token.spelling == '_EOF':
            return None

        # reserve epsilon expression match to real 'EPSILON_EXPR' instance
        if self.name != 'EPSILON_EXPR' and lexer.current_token.spelling == '_e':
            return None

        # if a TEXT grammar meets a text-literal token, return an ast node directly
        if self.name == 'TEXT' and lexer.current_token.type == TokenType.TEXTLITERAL:
            node = Ast(self.name, lexer.current_token.position,
                       grammar=lexer.current_token.spelling)
            if debug:
                print(' ' * (
                    debug - 1) + f'+++ {self.name}.match() {repr(self.regex)} with TEXT {lexer.current_token.spelling} finished')
            lexer.forward()
            if debug:
                print(
                    f'>>> lexer forwarded, current token: {lexer.current_token}')
            return node

        # if a NAME grammar meets a token with reserved word, return None directly
        # a reserved word can be only matched by a STRING grammar
        if self.name == 'NAME' and lexer.current_token.spelling in ReservedNames.names:
            return None

        # a text-literal token cannot match any other grammars
        if lexer.current_token.type != TokenType.TEXTLITERAL:
            regex_obj = re.compile(self.regex)
            match_result = regex_obj.match(lexer.current_token.spelling)

            if self.name == 'STRING' and not (
                        match_result and match_result.span()[1] == len(
                        lexer.current_token.spelling)):
                # if atom `STRING` match failed, try a special case:
                match_result = re.match(
                    '\\\'\(\\\'\[\\\\w\\\\W\]\*\?\\\'\|\\\"\[\\\\w\\\\W\]\*\?\\\"\)\\\'',
                    lexer.current_token.spelling)

            if match_result and match_result.span()[1] == len(
                    lexer.current_token.spelling):
                # matched, build AST node for this token's spelling, move lexer to next token
                node = Ast(self.name, lexer.current_token.position,
                           grammar=lexer.current_token.spelling)
                if debug:
                    print(' ' * (
                        debug - 1) + f'+++ {self.name}.match() {repr(self.regex)} with token <{lexer.current_token}> SUCCESS')
                lexer.forward()
                if debug:
                    print(
                        f'>>> lexer forwarded, current token: {lexer.current_token}')
                return node

            if debug:
                print(' ' * (
                    debug - 1) + f'--- {self.name}.match() {repr(self.regex)} with token <{lexer.current_token}> FAILED')

        return None


class BaseGrammar:
    """
    Base grammar:

    SAMPLE: G1 G2 | SAMPLE
    SAMPLE = BaseGrammar(
        [Refer(G1), Refer(G2)],  # grammar list 1 [G1, G2]
        [Refer(SAMPLE)],         # grammar list 2 [SAMPLE]
        name='SAMPLE')
    """

    def __init__(self, *grammar_list, name: str = None,
                 ignore_set: set = None):
        self.grammars = grammar_list
        self.done = False

        self.recursion = False
        self.productions = []
        self.ignore_set = ignore_set
        if name:
            self.name = name
        else:
            self.name = ' | '.join(
                ' '.join([grammar.name for grammar in each_list]) for each_list
                in grammar_list)

    def __str__(self):
        return f'BaseGrammar<{self.name}>'

    def __repr__(self):
        return str(self)

    def print_productions(self):
        return f'{str(self)}: ' + ' | '.join(
            str(production_list) for production_list in self.productions)

    def build(self, tracker: BuildTracker):
        """
        one-time recursive runner, build all possible productions of a given grammar
        """
        if self.done:
            return

        if self.name not in tracker.on_track:
            tracker.on_track.append(self.name)
        else:
            # if another `me` already on track, set recursion flag and skip operation
            self.recursion = True
            return

        for grammar_list in self.grammars:
            self.productions.append([])
            for grammar in grammar_list:
                if isinstance(grammar, GroupGrammar):
                    if grammar.name not in tracker.grammars:
                        # if this group of grammars is not in tracker, put it in
                        tracker.grammars[grammar.name] = grammar
                    else:
                        # else, take the old group grammar, as there must be a same
                        # group grammar which has been built already, no need to
                        # keep the current un-built one
                        grammar = tracker.grammars.get(grammar.name)

                    # build grammar, for an old group grammar the build() will be
                    # skipped as the `done` flag
                    grammar.build(tracker=tracker)
                    if grammar.recursion:
                        self.recursion = True
                    self.productions[-1].append(grammar)

                elif isinstance(grammar, Refer):
                    # get real grammar from tracker's grammar dict based on reference
                    grammar = tracker.grammars.get(grammar.name)
                    if isinstance(grammar, BaseGrammar):
                        grammar.build(tracker=tracker)
                    if grammar.recursion:
                        self.recursion = True
                    self.productions[-1].append(grammar)

                elif isinstance(grammar, LiteralGrammar) or isinstance(grammar,
                                                                       EpsilonGrammar):
                    # a simple EBNF literal grammar, no further operations
                    self.productions[-1].append(grammar)

                else:
                    raise UnknownGrammarObj('Unknown grammar object.')

        # set done flag, remove `me` from tracker after built is finished
        self.done = True
        tracker.on_track.remove(self.name)
        del self.grammars

    def match(self, lexer: Lexer, debug: int = 0, partial=True):
        """
        try to match lexer's current token with a production list in productions

        return AST instance: match SUCCESS with a production list in productions
        return None: match FAILED with whole productions
        """
        tree = Ast(self.name, lexer.current_position(), grammars=[])
        recursive_productions = []
        for production_list in self.productions:
            lexer.anchor()
            if debug:
                print(' ' * (
                    debug - 1) + f'### {self.name}.match() with production_list: {production_list}')
            # productions: [[G1, G2], [G3, G4], ...] <-> G1 G2 | G3 G4 | ...
            #
            # try to match all tokes with a production_list, mark the tracker
            # case 1: matched & break loop
            # case 2: unmatched, try next production_list in productions until
            # loop ends and function returns `None`
            success = self.build_ast(tree, lexer, production_list,
                                     recursive_productions,
                                     debug) if debug else self.build_ast(tree,
                                                                         lexer,
                                                                         production_list,
                                                                         recursive_productions)
            if success is True or success is None:
                # success case or Epsilon case
                if debug:
                    print(
                        ' ' * (debug - 1) + f'+++ {self.name}.match() SUCCESS')
                break
            else:
                # failed case
                continue
        else:
            if debug:
                print(' ' * (debug - 1) + f'--- {self.name}.match() FAILED')
            return None

        # one production_list is fully matched, pop anchor stack by one
        lexer.release_anchor()

        if lexer.current_token is None or tree.children or partial:
            return tree
        return None

    def build_ast(self, tree: Ast, lexer: Lexer, production_list: list,
                  recursive_productions: list = None, debug: int = 0):
        """
        build ast tree on the given instance (parameter `tree`)

        return True: SUCCESS, tree is appended with nodes
        return False: FAILED, and tree is untouched
        return None: Epsilon
        """
        if debug:
            print(' ' * (debug - 1) + f'### {self.name}.build_ast()')

        for grammar in production_list:
            nodes = grammar.match(lexer,
                                  debug + 4) if debug else grammar.match(lexer)

            # this grammar not matched:
            # 1. abandon whole production_list and skipped loop
            # 2. lexer setup rollback flag
            if nodes is None:

                if debug:
                    print(' ' * (
                        debug - 1) + f'--- {self.name}.build_ast() with grammar <{grammar}> FAILED')

                tree.empty()
                lexer.backward()

                if debug:
                    print(
                        f'<<< lexer backwarded, current token: {lexer.current_token}')

                return False

            if nodes == '_E':
                # Epsilon
                if debug:
                    print(' ' * (debug - 1) + f'+++ Epsilon match')
                    tree.append(Ast('Epsilon', lexer.current_token.position,
                                    grammar='_e'))
                return None

            if isinstance(grammar, GroupGrammar):
                # grammar is a GroupGrammar
                if not self.ignore_set:
                    tree.extend(nodes)
                else:
                    for node in nodes:
                        if node.name not in self.ignore_set:
                            tree.append(node)
            else:
                # grammar is a Token, only one production hence nodes is actually a `node`
                if not self.ignore_set or nodes.name not in self.ignore_set:
                    tree.append(nodes)

        # all grammar in current production_list matched, operation SUCCESS

        if debug:
            print(' ' * (debug - 1) + f'+++ {self.name}.build_ast() SUCCESS')

        return True


class GroupGrammar(BaseGrammar):
    """
    Base grammar in group:

    SAMPLE:  [ G1 G2 | G3 ] G4 | SAMPLE
    SAMPLE = BaseGrammar(
        [
            GroupGrammar(
                [Ref]er(G1), Refer(G2)],
                [Refer(G3)],
                repeat=[0, 1]),
            Refer(G4)
        ],
        [Refer(SAMPLE)],
        name='SAMPLE')
    """

    def __init__(self, *grammar_list, name=None, repeat=(0, -1)):
        super().__init__(*grammar_list, name=name)
        self.repeat = repeat
        if repeat[1] == -1:
            # repeat from some value to infinite
            if repeat[0] == 0:
                # repeat from 0 to infinite: ( ... )*
                self.name = f'({self.name})*'
            else:
                # repeat from some value to infinite: ( ... ){x,}
                self.name = f'({self.name}){{{repeat[0]},}}'
        else:
            # repeat from some value to some value
            if repeat[0] == 1 and repeat[1] == 1:
                # repeat only once: ( ... )
                self.name = f'({self.name})'
            else:
                if repeat[0] == 0 and repeat[1] == 1:
                    # an optional group, repeat at most 1 time: [ ... ]
                    self.name = f'[{self.name}]'
                else:
                    # repeat from x to y times: ( ... ){x,y}
                    self.name = f'({self.name}){{{repeat[0]},{repeat[1]}}}'

    def __str__(self):
        return f'GroupGrammar<{self.name}>'

    def __repr__(self):
        return str(self)

    def match(self, lexer: Lexer, debug: int = 0, partial=True):

        if debug:
            print(' ' * (
                debug - 1) + f'### GroupGrammar {self.name}.match(), calling super\'s match()')

        tree = Ast(self.name, lexer.current_position(), grammars=[])
        if lexer.current_token is None or lexer.current_token.spelling == '_EOF':
            if self.repeat[0] == 0:
                return tree
            return None

        lexer.anchor()
        repetition = 0
        if self.repeat[1] == -1:
            # can repeat for infinite times: grammar* | grammar+ | grammar{a,}
            while True:
                nodes = super().match(lexer, debug)
                if nodes is None:
                    break
                tree.extend(nodes)
                repetition += 1
                if lexer.current_token is None:
                    break
        else:
            # repeat for limited times: grammar{a, b} | grammar{a} | [grammar]
            while True:
                if repetition >= self.repeat[1]:
                    break
                nodes = super().match(lexer, debug)
                if nodes is None:
                    break
                tree.extend(nodes)
                repetition += 1
                if lexer.current_token is None:
                    break

        if repetition < self.repeat[0]:
            # if actual repetition is smaller than minimum times

            if debug:
                print(' ' * (
                    debug - 1) + f'--- GroupGrammar {self.name}.match() FAILED in minimal repetition)')

            lexer.backward()

            if debug:
                print(
                    f'<<< lexer backwarded, current token: {lexer.current_token}')

            return None

        if debug:
            print(' ' * (
                debug - 1) + f'+++ GroupGrammar {self.name}.match() SUCCESS')
        lexer.release_anchor()
        return tree


class Refer:
    """
    Referring another grammar's name
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)
