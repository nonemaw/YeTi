import os
from uni_parser.ebnf.ebnf_scanner import EBNFScanner, SourceFile
from uni_parser.ebnf.ebnf_grammar_reverse_builder import EBNFGrammarReverseBuilder
from uni_parser.ebnf.ebnf_grammar_source import *
from uni_parser.reserved_names import ReservedNames
from uni_parser.scanner import Scanner  # must be imported
from datetime import datetime


def parser_generator(grammar: str,
                     source_file: str = None,
                     source_code: str = None,
                     template_tag: str = None,
                     print_ast: bool = False,
                     save_to_file: bool = False,
                     reserved_names: list = None,
                     debug: int = 0):
    ReservedNames.add_name(*iter(reserved_names))

    this_path = os.path.dirname(os.path.realpath(__file__))
    ebnf_lexer = Lexer(EBNFScanner(
        SourceFile(os.path.join(this_path, 'grammars', f'{grammar}.ebnf'))))
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
        if source_file:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_file=os.path.join(this_path, 'sources', '{source_file}')), template_tag={template_tag}))"
        else:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_code=source_code), template_tag={template_tag}))"
    else:
        if source_file:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_file=os.path.join(this_path, 'sources', '{source_file}')), template_tag='{template_tag}'))"
        else:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_code=source_code), template_tag='{template_tag}'))"
    parser += f"\nEBNF.build(tracker, *{str(grammar_namelist)}, debug={debug})"

    if print_ast or save_to_file:
        parser += f"\nresult = EBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"
        if print_ast:
            parser += "\nprint(result.format())\n"
        elif save_to_file:
            parser += f"\ntime = datetime.now()\nfile_name = f'{grammar}_ast_{{time.year}}{{time.month}}{{time.day}}_{{time.hour}}{{time.minute}}{{time.second}}'\nwith open(os.path.join(this_path, 'ast_results', f'{{file_name}}.ast'), 'w') as F:\n    F.write(result.format())"
    else:
        parser += f"\nEBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"

    print(parser)

    exec(parser)


if __name__ == '__main__':
    parser_generator(grammar='xplan',
                     source_file='sample.txt',
                     source_code=None,
                     template_tag='<::>',
                     print_ast=False,
                     save_to_file=True,
                     reserved_names=['end', 'let'],
                     debug=0)
