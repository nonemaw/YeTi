class ParserLoader:
    def __init__(self, grammar: str):
        self.grammar = grammar

    def change_grammar(self, grammar: str):
        self.grammar = grammar

    def generator(self,
                 source_file: str = None,
                 source_code: str = None,
                 template_tag: str = None,
                 return_ast: bool = False,
                 save_ast: bool = True,
                 reserved_names: list or tuple = None,
                 overwrite: bool = True,
                 indent: int = 4):
        """
        Parameters
        --------
        source_file: str
            code from a source file
        source_code: str
            code from a long string
        template_tag: str
            for parsing template
        return_ast: bool
            whether print ast result
        save_ast: bool
            whether save the ast result to a file
        reserved_names: list or tuple
            customized reserved key words
        overwrite: bool
            whether overwrite existing parser file, written by default
        indent: int
            indent level for target file
        """
        from uni_parser.generator import parser_generator
        parser_generator(grammar=self.grammar,
                         source_file=source_file,
                         source_code=source_code,
                         template_tag=template_tag,
                         return_ast=return_ast,
                         save_ast=save_ast,
                         reserved_names=reserved_names,
                         overwrite=overwrite,
                         indent=indent)
        return self

    def parse(self, debug: int = 0) -> str:
        """
        return a formatted AST string
        """
        result = None
        local_dict = locals()
        exec(f'from uni_parser.parser_{self.grammar} import parse\nresult = parse({debug})', globals(), local_dict)
        return local_dict.get('result')


if __name__ == '__main__':
    p = ParserLoader('xplan')
    p.generator(source_file='sample.txt',
                source_code=None,
                template_tag='<::>',
                return_ast=False,
                save_ast=False,
                reserved_names=['end', 'let'],
                overwrite=True,
                indent=4)
    print(p.parse(debug=0))