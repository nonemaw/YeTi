from uni_parser.ebnf.ebnf_grammar_source import *
from uni_parser.scanner import Scanner
from uni_parser.token_source import SourceFile


def parse(source_file: str = None, source_code: str = None, message_only: bool = False, debug: int = 0):
    single_input = Base([Refer("""NEWLINE""")], [Refer("""simple_stmt""")], [Refer("""compound_stmt"""), Refer("""NEWLINE""")], name='single_input')
    file_input = Base([Group([Refer("""NEWLINE""")], [Refer("""stmt""")]), Group([Refer("""NEWLINE""")])], name='file_input')
    eval_input = Base([Refer("""testlist"""), Group([Refer("""NEWLINE""")]), Refer("""NEWLINE""")], name='eval_input')
    xplan = Base([Group([Refer("""NEWLINE""")], [Refer("""stmt""")], [Refer("""TEXT""")]), Group([Refer("""NEWLINE""")])], name='xplan')
    decorator = Base([Literal("""@""", """'@'"""), Refer("""NAME"""), Group([Literal("""(""", """'('""", escape=True), Group([Refer("""arglist""")], repeat=(0, 1)), Literal(""")""", """')'""", escape=True)], repeat=(0, 1)), Refer("""NEWLINE""")], name='decorator')
    decorators = Base([Group([Refer("""decorator""")], repeat=(1, -1))], name='decorators')
    decorated = Base([Refer("""decorators"""), Group([Refer("""classdef""")], [Refer("""funcdef""")], [Refer("""async_funcdef""")], repeat=(1, 1))], name='decorated')
    import_name = Base([Literal("""import""", """'import'"""), Refer("""dotted_as_names""")], name='import_name')
    import_from = Base([Group([Literal("""from""", """'from'"""), Group([Group([Literal(""".""", """'.'""", escape=True)], [Literal("""...""", """'...'""", escape=True)]), Refer("""NAME""")], [Group([Literal(""".""", """'.'""", escape=True)], [Literal("""...""", """'...'""", escape=True)], repeat=(1, -1))], repeat=(1, 1)), Literal("""import""", """'import'"""), Group([Literal("""*""", """'*'""", escape=True)], [Literal("""(""", """'('""", escape=True), Refer("""import_as_names"""), Literal(""")""", """')'""", escape=True)], [Refer("""import_as_names""")], repeat=(1, 1))], repeat=(1, 1))], name='import_from')
    import_as_name = Base([Refer("""NAME"""), Group([Literal("""as""", """'as'"""), Refer("""NAME""")], repeat=(0, 1))], name='import_as_name')
    dotted_as_name = Base([Refer("""NAME"""), Group([Literal("""as""", """'as'"""), Refer("""NAME""")], repeat=(0, 1))], name='dotted_as_name')
    import_as_names = Base([Refer("""import_as_name"""), Group([Literal(""",""", """','"""), Refer("""import_as_name""")]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='import_as_names')
    dotted_as_names = Base([Refer("""dotted_as_name"""), Group([Literal(""",""", """','"""), Refer("""dotted_as_name""")])], name='dotted_as_names')
    async_funcdef = Base([Literal("""async""", """'async'"""), Refer("""funcdef""")], name='async_funcdef')
    funcdef = Base([Literal("""def""", """'def'"""), Refer("""NAME"""), Refer("""parameters"""), Group([Literal("""->""", """'->'"""), Refer("""test""")], repeat=(0, 1)), Literal(""":""", """':'"""), Refer("""suite"""), Literal("""end""", """'end'""")], name='funcdef')
    classdef = Base([Literal("""class""", """'class'"""), Refer("""NAME"""), Group([Literal("""(""", """'('""", escape=True), Group([Refer("""arglist""")], repeat=(0, 1)), Literal(""")""", """')'""", escape=True)], repeat=(0, 1)), Literal(""":""", """':'"""), Refer("""suite"""), Literal("""end""", """'end'""")], name='classdef')
    tfpdef = Base([Refer("""NAME"""), Group([Literal(""":""", """':'"""), Refer("""test""")], repeat=(0, 1))], name='tfpdef')
    vfpdef = Base([Refer("""NAME""")], name='vfpdef')
    lambdef = Base([Literal("""lambda""", """'lambda'"""), Group([Refer("""varargslist""")], repeat=(0, 1)), Literal(""":""", """':'"""), Refer("""test""")], name='lambdef')
    lambdef_nocond = Base([Literal("""lambda""", """'lambda'"""), Group([Refer("""varargslist""")], repeat=(0, 1)), Literal(""":""", """':'"""), Refer("""test_nocond""")], name='lambdef_nocond')
    stmt = Base([Refer("""compound_stmt""")], [Refer("""simple_stmt""")], name='stmt')
    simple_stmt = Base([Refer("""small_stmt"""), Group([Literal(""";""", """';'"""), Refer("""small_stmt""")]), Group([Literal(""";""", """';'""")], repeat=(0, 1))], name='simple_stmt')
    small_stmt = Base([Group([Refer("""expr_stmt""")], [Refer("""del_stmt""")], [Refer("""pass_stmt""")], [Refer("""flow_stmt""")], [Refer("""import_stmt""")], [Refer("""global_stmt""")], [Refer("""nonlocal_stmt""")], [Refer("""assert_stmt""")], repeat=(1, 1))], name='small_stmt')
    expr_stmt = Base([Refer("""testlist_star_expr"""), Group([Refer("""annassign""")], [Refer("""augassign"""), Refer("""testlist""")], [Group([Literal("""=""", """'='"""), Refer("""testlist_star_expr""")])], repeat=(1, 1))], name='expr_stmt')
    del_stmt = Base([Literal("""del""", """'del'"""), Refer("""exprlist""")], name='del_stmt')
    pass_stmt = Literal("""pass""", """pass_stmt""")
    flow_stmt = Base([Refer("""break_stmt""")], [Refer("""continue_stmt""")], [Refer("""return_stmt""")], [Refer("""raise_stmt""")], name='flow_stmt')
    break_stmt = Literal("""break""", """break_stmt""")
    continue_stmt = Literal("""continue""", """continue_stmt""")
    return_stmt = Base([Literal("""return""", """'return'"""), Group([Refer("""testlist""")], repeat=(0, 1))], name='return_stmt')
    raise_stmt = Base([Literal("""raise""", """'raise'"""), Group([Refer("""test"""), Group([Literal("""from""", """'from'"""), Refer("""test""")], repeat=(0, 1))], repeat=(0, 1))], name='raise_stmt')
    import_stmt = Base([Refer("""import_name""")], [Refer("""import_from""")], name='import_stmt')
    global_stmt = Base([Literal("""global""", """'global'"""), Refer("""NAME"""), Group([Literal(""",""", """','"""), Refer("""NAME""")])], name='global_stmt')
    nonlocal_stmt = Base([Literal("""nonlocal""", """'nonlocal'"""), Refer("""NAME"""), Group([Literal(""",""", """','"""), Refer("""NAME""")])], name='nonlocal_stmt')
    assert_stmt = Base([Literal("""assert""", """'assert'"""), Refer("""test"""), Group([Literal(""",""", """','"""), Refer("""test""")], repeat=(0, 1))], name='assert_stmt')
    compound_stmt = Base([Refer("""if_stmt""")], [Refer("""while_stmt""")], [Refer("""for_stmt""")], [Refer("""try_stmt""")], [Refer("""with_stmt""")], [Refer("""funcdef""")], [Refer("""classdef""")], [Refer("""decorated""")], [Refer("""async_stmt""")], name='compound_stmt')
    if_stmt = Base([Group([Refer("""NEWLINE""")]), Literal("""if""", """'if'"""), Refer("""test"""), Literal(""":""", """':'"""), Refer("""suite"""), Group([Group([Refer("""NEWLINE""")]), Literal("""elif""", """'elif'"""), Refer("""test"""), Literal(""":""", """':'"""), Refer("""suite""")]), Group([Group([Refer("""NEWLINE""")]), Literal("""else""", """'else'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(0, 1)), Group([Refer("""NEWLINE""")]), Literal("""end""", """'end'""")], name='if_stmt')
    while_stmt = Base([Group([Refer("""NEWLINE""")]), Literal("""while""", """'while'"""), Refer("""test"""), Literal(""":""", """':'"""), Refer("""suite"""), Group([Group([Refer("""NEWLINE""")]), Literal("""else""", """'else'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(0, 1)), Group([Refer("""NEWLINE""")]), Literal("""end""", """'end'""")], name='while_stmt')
    for_stmt = Base([Group([Refer("""NEWLINE""")]), Literal("""for""", """'for'"""), Refer("""exprlist"""), Literal("""in""", """'in'"""), Refer("""testlist"""), Literal(""":""", """':'"""), Refer("""suite"""), Group([Group([Refer("""NEWLINE""")]), Literal("""else""", """'else'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(0, 1)), Group([Refer("""NEWLINE""")]), Literal("""end""", """'end'""")], name='for_stmt')
    try_stmt = Base([Group([Refer("""NEWLINE""")]), Group([Literal("""try""", """'try'"""), Literal(""":""", """':'"""), Refer("""suite"""), Group([Group([Refer("""except_clause"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(1, -1)), Group([Group([Refer("""NEWLINE""")]), Literal("""else""", """'else'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(0, 1)), Group([Group([Refer("""NEWLINE""")]), Literal("""finally""", """'finally'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(0, 1))], [Group([Refer("""NEWLINE""")]), Literal("""finally""", """'finally'"""), Literal(""":""", """':'"""), Refer("""suite""")], repeat=(1, 1))], repeat=(1, 1)), Group([Refer("""NEWLINE""")]), Literal("""end""", """'end'""")], name='try_stmt')
    except_clause = Base([Group([Refer("""NEWLINE""")]), Literal("""except""", """'except'"""), Group([Refer("""test"""), Group([Literal("""as""", """'as'"""), Refer("""NAME""")], repeat=(0, 1))], repeat=(0, 1))], name='except_clause')
    with_stmt = Base([Group([Refer("""NEWLINE""")]), Literal("""with""", """'with'"""), Refer("""with_item"""), Group([Literal(""",""", """','"""), Refer("""with_item""")]), Literal(""":""", """':'"""), Refer("""suite"""), Group([Refer("""NEWLINE""")]), Literal("""end""", """'end'""")], name='with_stmt')
    with_item = Base([Refer("""test"""), Group([Literal("""as""", """'as'"""), Refer("""expr""")], repeat=(0, 1))], name='with_item')
    async_stmt = Base([Literal("""async""", """'async'"""), Group([Refer("""funcdef""")], [Refer("""with_stmt""")], [Refer("""for_stmt""")], repeat=(1, 1))], name='async_stmt')
    annassign = Base([Literal(""":""", """':'"""), Refer("""test"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))], name='annassign')
    testlist_star_expr = Base([Group([Refer("""star_expr""")], [Refer("""test""")], repeat=(1, 1)), Group([Literal(""",""", """','"""), Group([Refer("""star_expr""")], [Refer("""test""")], repeat=(1, 1))]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='testlist_star_expr')
    augassign = Base([Group([Literal("""+=""", """'+='""", escape=True)], [Literal("""-=""", """'-='""")], [Literal("""*=""", """'*='""", escape=True)], [Literal("""@=""", """'@='""")], [Literal("""/=""", """'/='""")], [Literal("""%=""", """'%='""")], [Literal("""&=""", """'&='""")], [Literal("""|=""", """'|='""")], [Literal("""^=""", """'^='""")], [Literal("""<<=""", """'<<='""")], [Literal(""">>=""", """'>>='""")], [Literal("""**=""", """'**='""", escape=True)], [Literal("""//=""", """'//='""")], repeat=(1, 1))], name='augassign')
    suite = Base([Refer("""NEWLINE"""), Group([Group([Refer("""NEWLINE""")]), Group([Refer("""TEXT""")], [Refer("""stmt""")], repeat=(1, 1))], repeat=(1, -1))], [Group([Refer("""TEXT""")], [Refer("""simple_stmt""")], repeat=(1, 1))], name='suite')
    test = Base([Refer("""lambdef""")], [Refer("""or_test"""), Group([Literal("""if""", """'if'"""), Refer("""or_test"""), Literal("""else""", """'else'"""), Refer("""test""")], repeat=(0, 1))], name='test')
    test_nocond = Base([Refer("""or_test""")], [Refer("""lambdef_nocond""")], name='test_nocond')
    or_test = Base([Refer("""and_test"""), Group([Literal("""or""", """'or'"""), Refer("""and_test""")])], name='or_test')
    and_test = Base([Refer("""not_test"""), Group([Literal("""and""", """'and'"""), Refer("""not_test""")])], name='and_test')
    not_test = Base([Literal("""not""", """'not'"""), Refer("""not_test""")], [Refer("""comparison""")], name='not_test')
    comparison = Base([Refer("""expr"""), Group([Refer("""comp_op"""), Refer("""expr""")])], name='comparison')
    comp_op = Base([Literal("""<""", """'<'""")], [Literal(""">""", """'>'""")], [Literal("""==""", """'=='""")], [Literal(""">=""", """'>='""")], [Literal("""<=""", """'<='""")], [Literal("""<>""", """'<>'""")], [Literal("""!=""", """'!='""")], [Literal("""in""", """'in'""")], [Literal("""not""", """'not'"""), Literal("""in""", """'in'""")], [Literal("""is""", """'is'""")], [Literal("""is""", """'is'"""), Literal("""not""", """'not'""")], name='comp_op')
    expr = Base([Refer("""xor_expr"""), Group([Literal("""|""", """'|'""", escape=True), Refer("""xor_expr""")])], name='expr')
    xor_expr = Base([Refer("""and_expr"""), Group([Literal("""^""", """'^'""", escape=True), Refer("""and_expr""")])], name='xor_expr')
    and_expr = Base([Refer("""shift_expr"""), Group([Literal("""&""", """'&'"""), Refer("""shift_expr""")])], name='and_expr')
    shift_expr = Base([Refer("""arith_expr"""), Group([Group([Literal("""<<""", """'<<'""")], [Literal(""">>""", """'>>'""")], repeat=(1, 1)), Refer("""arith_expr""")])], name='shift_expr')
    arith_expr = Base([Refer("""term"""), Group([Group([Literal("""+""", """'+'""", escape=True)], [Literal("""-""", """'-'""", escape=True)], repeat=(1, 1)), Refer("""term""")])], name='arith_expr')
    term = Base([Refer("""factor"""), Group([Group([Literal("""*""", """'*'""", escape=True)], [Literal("""@""", """'@'""")], [Literal("""/""", """'/'""")], [Literal("""%""", """'%'""")], [Literal("""//""", """'//'""")], repeat=(1, 1)), Refer("""factor""")])], name='term')
    factor = Base([Group([Literal("""+""", """'+'""", escape=True)], [Literal("""-""", """'-'""", escape=True)], [Literal("""~""", """'~'""")], repeat=(1, 1)), Refer("""factor""")], [Refer("""power""")], name='factor')
    power = Base([Refer("""atom_expr"""), Group([Literal("""**""", """'**'""", escape=True), Refer("""factor""")], repeat=(0, 1))], name='power')
    atom_expr = Base([Group([Literal("""await""", """'await'""")], repeat=(0, 1)), Refer("""atom"""), Group([Refer("""trailer""")])], name='atom_expr')
    atom = Base([Group([Literal("""(""", """'('""", escape=True), Group([Refer("""testlist_comp""")], repeat=(0, 1)), Literal(""")""", """')'""", escape=True)], [Literal("""[""", """'['""", escape=True), Group([Refer("""testlist_comp""")], repeat=(0, 1)), Literal("""]""", """']'""", escape=True)], [Literal("""{""", """'{{'""", escape=True), Group([Refer("""dictorsetmaker""")], repeat=(0, 1)), Literal("""}""", """'}}'""", escape=True)], [Refer("""NAME""")], [Refer("""NUMBER""")], [Group([Refer("""STRING""")], repeat=(1, -1))], [Literal("""...""", """'...'""", escape=True)], [Literal("""None""", """'None'""")], [Literal("""True""", """'True'""")], [Literal("""False""", """'False'""")], repeat=(1, 1))], name='atom')
    testlist_comp = Base([Group([Refer("""test""")], [Refer("""star_expr""")], repeat=(1, 1)), Group([Refer("""comp_for""")], [Group([Literal(""",""", """','"""), Group([Refer("""test""")], [Refer("""star_expr""")], repeat=(1, 1))]), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(1, 1))], name='testlist_comp')
    trailer = Base([Literal("""(""", """'('""", escape=True), Group([Refer("""arglist""")], repeat=(0, 1)), Literal(""")""", """')'""", escape=True)], [Literal("""[""", """'['""", escape=True), Refer("""subscriptlist"""), Literal("""]""", """']'""", escape=True)], [Literal(""".""", """'.'""", escape=True), Refer("""NAME""")], name='trailer')
    subscriptlist = Base([Refer("""subscript"""), Group([Literal(""",""", """','"""), Refer("""subscript""")]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='subscriptlist')
    subscript = Base([Group([Refer("""test""")], repeat=(0, 1)), Literal(""":""", """':'"""), Group([Refer("""test""")], repeat=(0, 1)), Group([Refer("""sliceop""")], repeat=(0, 1))], [Refer("""test""")], name='subscript')
    sliceop = Base([Literal(""":""", """':'"""), Group([Refer("""test""")], repeat=(0, 1))], name='sliceop')
    exprlist = Base([Group([Refer("""expr""")], [Refer("""star_expr""")], repeat=(1, 1)), Group([Literal(""",""", """','"""), Group([Refer("""expr""")], [Refer("""star_expr""")], repeat=(1, 1))]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='exprlist')
    testlist = Base([Refer("""test"""), Group([Literal(""",""", """','"""), Refer("""test""")]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='testlist')
    dictorsetmaker = Base([Group([Group([Group([Refer("""test"""), Literal(""":""", """':'"""), Refer("""test""")], [Literal("""**""", """'**'""", escape=True), Refer("""expr""")], repeat=(1, 1)), Group([Refer("""comp_for""")], [Group([Literal(""",""", """','"""), Group([Refer("""test"""), Literal(""":""", """':'"""), Refer("""test""")], [Literal("""**""", """'**'""", escape=True), Refer("""expr""")], repeat=(1, 1))]), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(1, 1))], repeat=(1, 1))], [Group([Group([Refer("""test""")], [Refer("""star_expr""")], repeat=(1, 1)), Group([Refer("""comp_for""")], [Group([Literal(""",""", """','"""), Group([Refer("""test""")], [Refer("""star_expr""")], repeat=(1, 1))]), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(1, 1))], repeat=(1, 1))], repeat=(1, 1))], name='dictorsetmaker')
    star_expr = Base([Literal("""*""", """'*'""", escape=True), Refer("""expr""")], name='star_expr')
    comp_iter = Base([Refer("""comp_for""")], [Refer("""comp_if""")], name='comp_iter')
    sync_comp_for = Base([Literal("""for""", """'for'"""), Refer("""exprlist"""), Literal("""in""", """'in'"""), Refer("""or_test"""), Group([Refer("""comp_iter""")], repeat=(0, 1))], name='sync_comp_for')
    comp_for = Base([Group([Literal("""async""", """'async'""")], repeat=(0, 1)), Refer("""sync_comp_for""")], name='comp_for')
    comp_if = Base([Literal("""if""", """'if'"""), Refer("""test_nocond"""), Group([Refer("""comp_iter""")], repeat=(0, 1))], name='comp_if')
    parameters = Base([Literal("""(""", """'('""", escape=True), Group([Refer("""typedargslist""")], repeat=(0, 1)), Literal(""")""", """')'""", escape=True)], name='parameters')
    typedargslist = Base([Group([Refer("""tfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""tfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""*""", """'*'""", escape=True), Group([Refer("""tfpdef""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""tfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""**""", """'**'""", escape=True), Refer("""tfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""**""", """'**'""", escape=True), Refer("""tfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""*""", """'*'""", escape=True), Group([Refer("""tfpdef""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""tfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""**""", """'**'""", escape=True), Refer("""tfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""**""", """'**'""", escape=True), Refer("""tfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(1, 1))], name='typedargslist')
    varargslist = Base([Group([Refer("""vfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""vfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""*""", """'*'""", escape=True), Group([Refer("""vfpdef""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""vfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""**""", """'**'""", escape=True), Refer("""vfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""**""", """'**'""", escape=True), Refer("""vfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""*""", """'*'""", escape=True), Group([Refer("""vfpdef""")], repeat=(0, 1)), Group([Literal(""",""", """','"""), Refer("""vfpdef"""), Group([Literal("""=""", """'='"""), Refer("""test""")], repeat=(0, 1))]), Group([Literal(""",""", """','"""), Group([Literal("""**""", """'**'""", escape=True), Refer("""vfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(0, 1))], repeat=(0, 1))], [Literal("""**""", """'**'""", escape=True), Refer("""vfpdef"""), Group([Literal(""",""", """','""")], repeat=(0, 1))], repeat=(1, 1))], name='varargslist')
    arglist = Base([Refer("""argument"""), Group([Literal(""",""", """','"""), Refer("""argument""")]), Group([Literal(""",""", """','""")], repeat=(0, 1))], name='arglist')
    argument = Base([Group([Literal("""**""", """'**'""", escape=True), Refer("""test""")], [Literal("""*""", """'*'""", escape=True), Refer("""test""")], [Refer("""test"""), Literal("""=""", """'='"""), Refer("""test""")], [Refer("""test"""), Group([Refer("""comp_for""")], repeat=(0, 1))], repeat=(1, 1))], name='argument')
    NAME = Literal("""[\$]?[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*""", """NAME""")
    NUMBER = Literal("""[+-]?([0-9]*[.])?[0-9]+""", """NUMBER""")
    STRING = Literal("""('[\w\W]*?'|"[\w\W]*?")""", """STRING""")
    NEWLINE = Literal("""\n""", """NEWLINE""")
    DEDENT = Literal("""<<<<""", """DEDENT""")
    INDENT = Literal(""">>>>""", """INDENT""")
    TEXT = Literal("""<TEXT>""", """TEXT""")

    tracker = BuildTracker({
        'single_input': single_input,
        'file_input': file_input,
        'eval_input': eval_input,
        'xplan': xplan,
        'decorator': decorator,
        'decorators': decorators,
        'decorated': decorated,
        'import_name': import_name,
        'import_from': import_from,
        'import_as_name': import_as_name,
        'dotted_as_name': dotted_as_name,
        'import_as_names': import_as_names,
        'dotted_as_names': dotted_as_names,
        'async_funcdef': async_funcdef,
        'funcdef': funcdef,
        'classdef': classdef,
        'tfpdef': tfpdef,
        'vfpdef': vfpdef,
        'lambdef': lambdef,
        'lambdef_nocond': lambdef_nocond,
        'stmt': stmt,
        'simple_stmt': simple_stmt,
        'small_stmt': small_stmt,
        'expr_stmt': expr_stmt,
        'del_stmt': del_stmt,
        'pass_stmt': pass_stmt,
        'flow_stmt': flow_stmt,
        'break_stmt': break_stmt,
        'continue_stmt': continue_stmt,
        'return_stmt': return_stmt,
        'raise_stmt': raise_stmt,
        'import_stmt': import_stmt,
        'global_stmt': global_stmt,
        'nonlocal_stmt': nonlocal_stmt,
        'assert_stmt': assert_stmt,
        'compound_stmt': compound_stmt,
        'if_stmt': if_stmt,
        'while_stmt': while_stmt,
        'for_stmt': for_stmt,
        'try_stmt': try_stmt,
        'except_clause': except_clause,
        'with_stmt': with_stmt,
        'with_item': with_item,
        'async_stmt': async_stmt,
        'annassign': annassign,
        'testlist_star_expr': testlist_star_expr,
        'augassign': augassign,
        'suite': suite,
        'test': test,
        'test_nocond': test_nocond,
        'or_test': or_test,
        'and_test': and_test,
        'not_test': not_test,
        'comparison': comparison,
        'comp_op': comp_op,
        'expr': expr,
        'xor_expr': xor_expr,
        'and_expr': and_expr,
        'shift_expr': shift_expr,
        'arith_expr': arith_expr,
        'term': term,
        'factor': factor,
        'power': power,
        'atom_expr': atom_expr,
        'atom': atom,
        'testlist_comp': testlist_comp,
        'trailer': trailer,
        'subscriptlist': subscriptlist,
        'subscript': subscript,
        'sliceop': sliceop,
        'exprlist': exprlist,
        'testlist': testlist,
        'dictorsetmaker': dictorsetmaker,
        'star_expr': star_expr,
        'comp_iter': comp_iter,
        'sync_comp_for': sync_comp_for,
        'comp_for': comp_for,
        'comp_if': comp_if,
        'parameters': parameters,
        'typedargslist': typedargslist,
        'varargslist': varargslist,
        'arglist': arglist,
        'argument': argument,
        'NAME': NAME,
        'NUMBER': NUMBER,
        'STRING': STRING,
        'NEWLINE': NEWLINE,
        'DEDENT': DEDENT,
        'INDENT': INDENT,
        'TEXT': TEXT,
    })

    ReservedNames.add_name(*['let', 'end'])
    code_lexer = Lexer(Scanner(SourceFile(source_file=source_file, source_code=source_code), template_tag='<::>', var_define='let', end_tag=['end']))
    EBNF.build(tracker, *['single_input', 'file_input', 'eval_input', 'xplan', 'decorator', 'decorators', 'decorated', 'import_name', 'import_from', 'import_as_name', 'dotted_as_name', 'import_as_names', 'dotted_as_names', 'async_funcdef', 'funcdef', 'classdef', 'tfpdef', 'vfpdef', 'lambdef', 'lambdef_nocond', 'stmt', 'simple_stmt', 'small_stmt', 'expr_stmt', 'del_stmt', 'pass_stmt', 'flow_stmt', 'break_stmt', 'continue_stmt', 'return_stmt', 'raise_stmt', 'import_stmt', 'global_stmt', 'nonlocal_stmt', 'assert_stmt', 'compound_stmt', 'if_stmt', 'while_stmt', 'for_stmt', 'try_stmt', 'except_clause', 'with_stmt', 'with_item', 'async_stmt', 'annassign', 'testlist_star_expr', 'augassign', 'suite', 'test', 'test_nocond', 'or_test', 'and_test', 'not_test', 'comparison', 'comp_op', 'expr', 'xor_expr', 'and_expr', 'shift_expr', 'arith_expr', 'term', 'factor', 'power', 'atom_expr', 'atom', 'testlist_comp', 'trailer', 'subscriptlist', 'subscript', 'sliceop', 'exprlist', 'testlist', 'dictorsetmaker', 'star_expr', 'comp_iter', 'sync_comp_for', 'comp_for', 'comp_if', 'parameters', 'typedargslist', 'varargslist', 'arglist', 'argument', 'NAME', 'NUMBER', 'STRING', 'NEWLINE', 'DEDENT', 'INDENT', 'TEXT'], debug=debug)
    result = EBNF.match(tracker, code_lexer, grammar='xplan', message_only=message_only, debug=debug)
    return result
