import os
from uni_parser.ebnf.ebnf_scanner import EBNFScanner, SourceFile
from uni_parser.ebnf.ebnf_grammar_reverse_builder import EBNFGrammarReverseBuilder
from uni_parser.ebnf.ebnf_grammar_source import *


def parser_generator(grammar: str,
                     template_tag: list = None,
                     var_define: str = None,
                     end_tag: list = None,
                     return_ast: bool = False,
                     save_ast: bool = False,
                     reserved_names: list = None,
                     overwrite: bool = False,
                     indent: int = 4):
    """
    Run EBNF parser and generate grammar based on provided EBNF file, stored in
    `parser_{grammar}.py`

    Parameters
    --------
    grammar: str
        grammar file under directory grammars for target code (e.g., python means python.ebnf)
    template_tag: list
        for parsing template
    var_define: str
        definition to variable declare in template
    return_ast: bool
        whether print ast result
    save_ast: bool
        whether save the ast result to a file
    reserved_names: list
        customized reserved key words
    overwrite: bool
        whether overwrite existing parser file
    indent: int
        indent level for target file
    """
    indent = ' ' * indent
    this_path = os.path.dirname(os.path.realpath(__file__))
    ebnf_lexer = Lexer(EBNFScanner(
        SourceFile(os.path.join(this_path, 'grammars', f'{grammar}.ebnf'))))
    EBNF.build(EBNF.tracker, 'test', debug=0)
    ebnf_ast = EBNF.match(EBNF.tracker, ebnf_lexer, return_ast=True, debug=0)

    parser = [
f"""from uni_parser.ebnf.ebnf_grammar_source import *
from uni_parser.scanner import Scanner
from uni_parser.token_source import SourceFile


def parse(source_file: str = None, source_code: str = None, message_only: bool = False, debug: int = 0):
"""]
    parser.append(f'{EBNFGrammarReverseBuilder.build(ebnf_ast, indent=4)}\n')
    grammar_namelist = re.compile('(_*[_a-zA-Z0-9]+) =').findall(parser[1])
    parser.append(f'{indent}tracker = BuildTracker({{\n')
    for name in grammar_namelist:
        parser.append(f'{indent}{indent}\'{name}\': {name},\n')
    else:
        parser.append(f'{indent}}})\n')

    parser.append(f'\n{indent}ReservedNames.add_name(*{str(reserved_names)})')
    if template_tag and var_define:
        parser.append(f"\n{indent}code_lexer = Lexer(Scanner(SourceFile(source_file=source_file, source_code=source_code), template_tag={str(template_tag)}, var_define='{var_define}', end_tag={str(end_tag)}))")
    elif template_tag:
        parser.append(f"\n{indent}code_lexer = Lexer(Scanner(SourceFile(source_file=source_file, source_code=source_code), template_tag={str(template_tag)}, end_tag={str(end_tag)}))")
    elif var_define:
        parser.append(f"\n{indent}code_lexer = Lexer(Scanner(SourceFile(source_file=source_file, source_code=source_code), var_define='{var_define}', end_tag={str(end_tag)}))")
    else:
        parser.append(f"\n{indent}code_lexer = Lexer(Scanner(SourceFile(source_file=source_file, source_code=source_code), end_tag={str(end_tag)}))")

    parser.append(f"\n{indent}EBNF.build(tracker, *{str(grammar_namelist)}, debug=debug)")

    if return_ast or save_ast:
        parser.append(f"\n{indent}result = EBNF.match(tracker, code_lexer, grammar='{grammar}', return_ast=True, message_only=message_only, debug=debug)")
        if save_ast:
            parser.append(f"\n\n{indent}import os\n{indent}from datetime import datetime\n{indent}this_path = os.path.dirname(os.path.realpath(__file__))\n{indent}time = datetime.now()\n{indent}file_name = f'{grammar}_ast_{{time.year}}{{time.month}}{{time.day}}_{{time.hour}}{{time.minute}}{{time.second}}'\n{indent}with open(os.path.join(this_path, 'ast_results', f'{{file_name}}.ast'), 'w') as F:\n{indent}{indent}F.write(result.format())")
        if return_ast:
            parser.append(f"\n{indent}if not isinstance(result, dict):\n{indent}{indent}return result.format()\n{indent}else:\n{indent}{indent}return result\n")
    else:
        parser.append(f"\n{indent}result = EBNF.match(tracker, code_lexer, grammar='{grammar}', message_only=message_only, debug=debug)\n{indent}return result\n")

    if not os.path.isfile(os.path.join(this_path, f'parser_{grammar}.py')):
        with open(os.path.join(this_path, f'parser_{grammar}.py'), 'w') as F:
            for line in parser:
                F.write(line)
    elif overwrite:
        with open(os.path.join(this_path, f'parser_{grammar}.py'), 'w') as F:
            for line in parser:
                F.write(line)
    parser.clear()
