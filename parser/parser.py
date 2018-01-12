import os
from ebnf.ebnf_scanner import EBNFScanner, SourceFile
from ebnf.ebnf_grammar_reverse_builder import EBNFGrammarReverseBuilder
from ebnf.ebnf_grammar_source import *
from reserved_names import ReservedNames
from scanner import Scanner  # must be imported


def parser_generator(grammar: str,
                     source_file: str = None,
                     source_code: str = None,
                     template_tag: str = None,
                     print_result: bool = False,
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
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_file=os.path.join(this_path, 'source', '{source_file}')), template_tag={template_tag}))"
        else:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_code=source_code), template_tag={template_tag}))"
    else:
        if source_file:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_file=os.path.join(this_path, 'source', '{source_file}')), template_tag='{template_tag}'))"
        else:
            parser += f"\ncode_lexer = Lexer(Scanner(SourceFile(source_code=source_code), template_tag='{template_tag}'))"
    parser += f"\nEBNF.build(tracker, *{str(grammar_namelist)}, debug={debug})"

    if print_result or save_to_file:
        parser += f"\nresult = EBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"
        if print_result:
            parser += "\nprint(result.format())\n"
        elif save_to_file:
            parser += "\nwith open(os.path.join(this_path, 'ast_result.txt'), 'w') as F:\n    F.write(result.format())"
    else:
        parser += f"\nEBNF.match(tracker, code_lexer, grammar='{grammar}', debug={debug})"

    print(parser)

    exec(parser)


if __name__ == '__main__':

    sample = """<:let getAddressDetails=lambda entity, type: [str(entity.preferred_street), str(entity.preferred_suburb).upper()+’ ‘+str(entity.preferred_state)+’ ‘+str(entity.preferred_postcode)] if entity.preferred_street and str(type).lower()==’preferred’ else type and [’’.join([str(x.street) for x in entity.address.sort(‘-preferred’) if str(type).lower()==str(x.type.text).lower()][:1]), ‘’.join([str(x.suburb).upper()+’ ‘+str(x.state)+’ ‘+str(x.postcode) for x in entity.address.sort(‘-preferred’) if str(type).lower()==str(x.type.text).lower()][:1])] if len(type) and len([x for x in entity.address.sort(‘-preferred’) if x.type.text in [type]][:1]) else [‘Error: No matching types found’] if len(type) else [‘Error: Type argument not specified eg “Postal”, “Preferred”’]:>
SUPERANNUATION DETAILS
<:if len($client.fund) or len($partner.fund):>
 The following table outlines the details of your superannuation accounts.
EXISTING FUND
<:=$client.preferred_name:> <:=$client.last_name:>
<:if 1:><:let line = 0:><:let total = 0:>
<:end:>
Name of Fund	Type	Components	Balance ($)
<:for item in $client.fund:>
<:if 1:><:let line = line + 1:>
<:end:>
<:if line % 2 != 0:>
<:=item.fund_super_plan:>	<:=item.fund_type:>	Taxable (Taxed): $<:=currency(item.fund_taxable.value,0):>
Taxable (Untaxed): $<:=currency(item.fund_taxable_untaxed.value,0):>
Tax Free: $<:=currency(item.fund_tax_free.value,0):>	<:=currency(item.fund_total_balance.value,0):>
<:let total = total + item.fund_total_balance.value:>
<:else:>
<:=item.fund_super_plan:>	<:=item.fund_type:>	Taxable (Taxed): $<:=currency(item.fund_taxable.value,0):>
Taxable (Untaxed): $<:=currency(item.fund_taxable_untaxed.value,0):>
Tax Free: $<:=currency(item.fund_tax_free.value,0):>	<:=currency(item.fund_total_balance.value,0):>
<:let total = total + item.fund_total_balance.value:>
<:end:>
<:end:>
Total Balance:		<:=currency(total,0):>

<:if $partner:>
<:=$partner.preferred_name:> <:=$partner.last_name:>
<:if 1:><:let line = 0:><:let total = 0:>
<:end:>
Name of Fund	Nomination Type	Components	Balance ($)
<:for item in $partner.fund:>
<:if 1:><:let line = line + 1:>
<:end:>
<:if line % 2 != 0:>
<:=item.fund_super_plan:>	<:=item.fund_type:>	Taxable (Taxed): $<:=currency(item.fund_taxable.value,0):>
Taxable (Untaxed): $<:=currency(item.fund_taxable_untaxed.value,0):>
Tax Free: $<:=currency(item.fund_tax_free.value,0):>	<:=currency(item.fund_total_balance.value,0):>
<:let total = total + item.fund_total_balance.value:>
<:else:>
<:=item.fund_super_plan:>	<:=item.fund_type:>	Taxable (Taxed): $<:=currency(item.fund_taxable.value,0):>
Taxable (Untaxed): $<:=currency(item.fund_taxable_untaxed.value,0):>
Tax Free: $<:=currency(item.fund_tax_free.value,0):>	<:=currency(item.fund_total_balance.value,0):>
<:let total = total + item.fund_total_balance.value:>
<:end:>
<:end:>
Total Balance:		<:=currency(total,0):>
<:end:>
<:else:>
You have advised that you currently do not have any superannuation accounts.
<:end:>

<:if len($client.retirement_income) or len($partner.retirement_income):>
 The following table outlines the details of your retirement income.
RETIREMENT INCOME
<:=$client.preferred_name:> <:=$client.last_name:>
<:if 1:><:let line = 0:><:let total = 0:>
<:end:>
Type	Description	Frequency	Payment ($)
<:for item in $client.retirement_income:>
<:if 1:><:let freq = item.frequency:>
<:end:>
<:if 1:><:let line = line + 1:>
<:end:>
<:if line % 2 != 0:>
<:=item.type:>	<:=item.desc:>	<:if 1:><:let feq = item.frequency:>
<:end:>
<:=feq:>	<:=currency(item.payment.value,0):>
<:let total = total + int(item.payment.value) * int(freq):>
<:else:>
<:=item.type:>	<:=item.desc:>	<:if 1:><:let feq = item.frequency:>
<:end:>
<:=feq:>	<:=currency(item.payment.value,0):>
<:let total = total + int(item.payment.value) * int(freq):>
<:end:>
<:end:>
Total Annual Payment:		<:=currency(total,0):>

<:if $partner:>
<:=$partner.preferred_name:> <:=$partner.last_name:>
<:if 1:><:let line = 0:><:let total = 0:>
<:end:>
Type	Description	Frequency	Payment ($)
<:for item in $partner.retirement_income:>
<:if 1:><:let freq = item.frequency:>
<:end:>
<:if 1:><:let line = line + 1:>
<:end:>
<:if line % 2 != 0:>
<:=item.type:>	<:=item.desc:>	<:if 1:><:let feq = item.frequency:>
<:end:>
<:=feq:>	<:=currency(item.payment.value,0):>
<:let total = total + int(item.payment.value) * int(freq):>
<:else:>
<:=item.type:>	<:=item.desc:>	<:if 1:><:let feq = item.frequency:>
<:end:>
<:=feq:>	<:=currency(item.payment.value,0):>
<:let total = total + int(item.payment.value) * int(freq):>
<:end:>
<:end:>
Total Annual Payment:		<:=currency(total,0):>
<:end:>
<:else:>
You have advised that you currently do not have any retirement income.
<:end:>
"""
    parser_generator(grammar='xplan',
                     source_file='sample.txt',
                     source_code=sample,
                     template_tag='<::>',
                     print_result=False,
                     save_to_file=False,
                     reserved_names=['end', 'let'],
                     debug=0)
