class ReservedNames:
    """
    reserved names are those who appear in EBNF grammar directly

    for example:
    if_stmt ::= 'if' ':' suite ('elif' ':' suite) ['else' ':' suite]

    in this case, 'if', 'elif' and 'else' are reserved words which cannot be
    matched by NAME grammar because they cannot be a variable name, but matched
    by STRING grammar instead
    """
    names = {'and', 'assert', 'break', 'class', 'continue', 'def', 'del',
             'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
             'if', 'import', 'in', 'is', 'lambda', 'not', 'or', 'pass',
             'raise', 'return', 'try', 'while'}

    operation_symbols = {
        '\\+', '\\-', '\\*', '/', '%', '//', '\\*\\*'
    }

    @staticmethod
    def add_name(*names):
        for name in names:
            if name not in ReservedNames.names:
                ReservedNames.names.add(name)
