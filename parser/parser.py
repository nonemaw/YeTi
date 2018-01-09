import os
from parser.ebnf.ebnf_scanner import EBNFScanner, SourceFile
from parser.ebnf.ebnf_grammar_reverse_builder import EBNFGrammarReverseBuilder
from parser.ebnf.ebnf_grammar_source import *
from parser.reserved_names import ReservedNames
from parser.scanner import Scanner  # must be imported


def parser_generator(grammar: str = 'xplan', template_tag: str = None,
                     print_result: bool = False, save_to_file: bool = False,
                     reserved_names: list = None, debug: int = 0):
    ReservedNames.add_name(*iter(reserved_names))

    this_path = os.path.dirname(os.path.realpath(__file__))
    ebnf_lexer = Lexer(EBNFScanner(
        SourceFile(os.path.join(this_path, 'ebnf', 'grammar.ebnf'))))
    EBNF.build(EBNF.tracker, 'test', debug=0)
    ebnf_ast = EBNF.match(EBNF.tracker, ebnf_lexer, debug=0)

    parser = EBNFGrammarReverseBuilder.build(ebnf_ast)
    grammar_namelist = re.compile('(_*[_a-zA-Z0-9]+) =').findall(parser)
    parser += '\ntracker = BuildTracker({\n'
    for name in grammar_namelist:
        parser += f'    \'{name}\': {name},\n'
    else:
        parser += '})\n'

    if template_tag is None:
        parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(os.path.join(this_path, 'code.txt')), template_tag={template_tag}))"
    else:
        parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(os.path.join(this_path, 'code.txt')), template_tag='{template_tag}'))"
    parser += f"\nEBNF.build(tracker, *{str(grammar_namelist)}, debug={debug})"

    if print_result or save_to_file:
        parser += f"\nresult = EBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"
        if print_result:
            parser += "\nprint(result.format())\n"
        elif save_to_file:
            parser += "\nwith open(os.path.join(this_path, 'ast_result.txt'), 'w') as F:\n    F.write(result.format())"
    else:
        parser += f"\nEBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"

    exec(parser)


if __name__ == '__main__':
    parser_generator(grammar='xplan', template_tag='<::>',
                     print_result=False, save_to_file=False,
                     reserved_names=['end', 'let'], debug=1)
