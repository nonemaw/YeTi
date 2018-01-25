class ParserLoader:
    def __new__(cls, grammar: str):
        if not hasattr(cls, '_singleton'):
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self, grammar: str):
        self.grammar = grammar

    def change_grammar(self, grammar: str):
        self.grammar = grammar

    def generator(self,
                  template_tag: str = None,
                  var_define: str = None,
                  end_tag: list = None,
                  return_ast: bool = False,
                  save_ast: bool = True,
                  reserved_names: list = None,
                  overwrite: bool = True,
                  indent: int = 4):
        """
        Parameters
        --------
        template_tag: str
            for parsing template
        var_define: str
            definition to variable declare in template
        end_tag: list
            end tag for loop and if conditions
        return_ast: bool
            whether print ast result
        save_ast: bool
            whether save the ast result to a file
        reserved_names: list
            customized reserved key words
        overwrite: bool
            whether overwrite existing parser file, written by default
        indent: int
            indent level for target file
        """
        if var_define not in reserved_names:
            reserved_names.append(var_define)
        if end_tag:
            for tag in end_tag:
                if tag not in reserved_names:
                    reserved_names.append(tag)

        from uni_parser.generator import parser_generator
        parser_generator(grammar=self.grammar,
                         template_tag=template_tag,
                         var_define=var_define,
                         end_tag=end_tag,
                         return_ast=return_ast,
                         save_ast=save_ast,
                         reserved_names=reserved_names,
                         overwrite=overwrite,
                         indent=indent)
        return self

    def parse(self,
              source_file: str = None,
              source_code: str = None,
              message_only: bool = False,
              debug: int = 0) -> str:
        """
        return a formatted AST string
        """
        result = None
        local_dict = locals()
        if source_file and source_code:
            exec(
                f'from uni_parser.parser_{self.grammar} import parse\nresult = parse({source_file}, """{source_code}""", {message_only}, "{debug}")',
                globals(),
                local_dict)
        elif source_file:
            exec(
                f'from uni_parser.parser_{self.grammar} import parse\nresult = parse("{source_file}", None, {message_only}, {debug})',
                globals(),
                local_dict)
        elif source_code:
            exec(
                f'from uni_parser.parser_{self.grammar} import parse\nresult = parse(None, """{source_code}""", {message_only}, {debug})',
                globals(),
                local_dict)
        return local_dict.get('result')


if __name__ == '__main__':
    # TODO: FATAL BUG: two `stmt` syntax on same line can pass the judge
    # TODO: FATAL BUG: `stmt` ends with `.` can pass the judge, e.g. `let a = b.`
    p = ParserLoader('xplan')
    p.generator(template_tag='<::>',
                var_define='let',
                end_tag=['end'],
                return_ast=True,
                save_ast=False,
                reserved_names=[],
                overwrite=True,
                indent=4)
    r = p.parse(source_file='', source_code="""<:if$partner:>""",
                message_only=True, debug=0)
    print(r)
