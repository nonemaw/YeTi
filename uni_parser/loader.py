class ParserLoader:
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
                         var_define = var_define,
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
            exec(f'from uni_parser.parser_{self.grammar} import parse\nresult = parse({source_file}, """{source_code}""", {message_only}, "{debug}")',
                 globals(), local_dict)
        elif source_file is not None:
            exec(
                f'from uni_parser.parser_{self.grammar} import parse\nresult = parse("{source_file}", None, {message_only}, {debug})',
                globals(), local_dict)
        elif source_code:
            exec(
                f'from uni_parser.parser_{self.grammar} import parse\nresult = parse(None, """{source_code}""", {message_only}, {debug})',
                globals(), local_dict)
        return local_dict.get('result')


if __name__ == '__main__':
    p = ParserLoader('xplan')
    r = p.generator(template_tag='<::>',
                    var_define='let',
                    end_tag=['end'],
                    return_ast=False,
                    save_ast=False,
                    reserved_names=[],
                    overwrite=False,
                    indent=4).parse(source_file=None, source_code=
"""<:let ShowC=False:>
<:let ShowP=False:>
<:let ShowJ=False:>
<:let Company=False:>
<:let Trust=False:>
<:let Superfund=False:>
<:if str($client.valueOf('addressed_to')) in ['Client']:>
    <:let ShowC=True:>
<:end:>
<:if $partner:>
    <:if str($client.valueOf('addressed_to')) in ['Partner']:>
        <:let ShowP=True:>
    <:end:>
    <:if str($client.valueOf('addressed_to')) in ['Joint']:>
        <:let ShowJ=True:>
        <:let Cname=str($client.preferred_name):>
        <:let Pname=str($partner.preferred_name):>
    <:end:>
<:end:>
<:if filter(lambda x: x in ['Company'], map(str,$client.valueOf('include_other_entities'))) :>
    <:let Company=True:>
<:end:>
<:if filter(lambda x: x in ['Trust'], map(str,$client.valueOf('include_other_entities'))) :>
    <:let Trust=True:>
<:end:>
<:if filter(lambda x: x in ['Superfund'], map(str,$client.valueOf('include_other_entities'))) :>
    <:let Superfund=True:>
<:end:>

<:let advisor_t = $client.client_adviser.preferred_phone:>
<:let advisor_e = $client.client_adviser.preferred_email:>

<:for name in [company.name for company in $company]:>
    <:if 1:><:let company_name = name:>
    <:end:>
<:end:>
<:for name in [superfund.name for superfund in $superfund]:>
    <:if 1:><:let smsf_name = name:>
    <:end:>
<:end:>
<:for name in [trust.name for trust in $trust]:>
    <:if 1:><:let trust_name = name:>
    <:end:>
<:end:>

<:let sorted_client = []:>
<:let sorted_partner = []:>
<:let sorted_joint = []:>
<:let sorted_trust = []:>
<:let sorted_company = []:>
<:let sorted_smsf = []:>
<:for item in $client.nb_soa_product_recommendations:>
    <:if str(item.entity) == 'Client':>
        <:=sorted_client.append(item):>
    <:end:>
    <:if str(item.entity) == 'Partner':>
        <:=sorted_partner.append(item):>
    <:end:>
    <:if str(item.entity) == 'Joint':>
        <:=sorted_joint.append(item):>
    <:end:>
    <:if str(item.entity) == 'Trust':>
        <:=sorted_trust.append(item):>
    <:end:>
    <:if str(item.entity) == 'Company':>
        <:=sorted_company.append(item):>
    <:end:>
    <:if str(item.entity) == 'Superfund':>
        <:=sorted_smsf.append(item):>
    <:end:>
<:end:>
<:let sorted_soa_product_recommendations = sorted_client + sorted_partner + sorted_joint + sorted_trust + sorted_company + sorted_smsf:>

<:let sorted_client = []:>
<:let sorted_partner = []:>
<:let sorted_joint = []:>
<:let sorted_trust = []:>
<:let sorted_company = []:>
<:let sorted_smsf = []:>
<:for item in $client.nb_soa_service_recommendations:>
    <:if str(item.entity) == 'Client':>
        <:=sorted_client.append(item):>
    <:end:>
    <:if str(item.entity) == 'Partner':>
        <:=sorted_partner.append(item):>
    <:end:>
    <:if str(item.entity) == 'Joint':>
        <:=sorted_joint.append(item):>
    <:end:>
    <:if str(item.entity) == 'Trust':>
        <:=sorted_trust.append(item):>
    <:end:>
    <:if str(item.entity) == 'Company':>
        <:=sorted_company.append(item):>
    <:end:>
    <:if str(item.entity) == 'Superfund':>
        <:=sorted_smsf.append(item):>
    <:end:>
<:end:>
<:let sorted_soa_service_recommendations = sorted_client + sorted_partner + sorted_joint + sorted_trust + sorted_company + sorted_smsf:>

<:let sorted_client = []:>
<:let sorted_partner = []:>
<:let sorted_joint = []:>
<:let sorted_trust = []:>
<:let sorted_company = []:>
<:let sorted_smsf = []:>
<:for item in $client.nb_soa_strategy_recommendations:>
    <:if str(item.entity) == 'Client':>
        <:=sorted_client.append(item):>
    <:end:>
    <:if str(item.entity) == 'Partner':>
        <:=sorted_partner.append(item):>
    <:end:>
    <:if str(item.entity) == 'Joint':>
        <:=sorted_joint.append(item):>
    <:end:>
    <:if str(item.entity) == 'Trust':>
        <:=sorted_trust.append(item):>
    <:end:>
    <:if str(item.entity) == 'Company':>
        <:=sorted_company.append(item):>
    <:end:>
    <:if str(item.entity) == 'Superfund':>
        <:=sorted_smsf.append(item):>
    <:end:>
<:end:>
<:let sorted_soa_strategy_recommendations = sorted_client + sorted_partner + sorted_joint + sorted_trust + sorted_company + sorted_smsf:>



<:=$client.date_of_advice.format('%d %B %Y'):>

<:if ShowC:><:let title = str($client.title) + ' ' + str($client.preferred_name) + ' ' + str($client.last_name):>
    <:for item in $client.address.filter('preferred=True'):>
        <:let suburb = str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=title:>
    <:=str(item.street):>
    <:=suburb:>
<:end:>
<:if ShowP:><:let title = str($partner.title) + ' ' + str($partner.preferred_name) + ' ' + str($partner.last_name):>
    <:for item in $client.address.filter('preferred=True'):>
        <:let suburb = str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=title:>
    <:=str(item.street):>
    <:=suburb:>
<:end:>
<:if ShowJ:><:let title = str($client.title) + ' ' + str($client.preferred_name) + ' ' + str($client.last_name) + ' and ' + str($partner.title) + ' ' + str($partner.preferred_name) + ' ' + str($partner.last_name):>
    <:for item in $client.address.filter('preferred=True'):>
        <:let suburb = str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=title:>
    <:=str(item.street):>
    <:=suburb:>
<:end:>
		<:let flag = True:>
Perpetual Trustee
Company Limited
ABN 42 000 001 007

AFSL 236643

<:for item in $client.client_adviser.address:>
    <:if item.preferred:>
        <:if item.type == '0':><:let flag = False:>
        <:end:>
        <:for s in str(item.street).split(','):>
            <:=s.strip():>
        <:end:>
        <:=str(item.suburb):> <:=str(item.state):> <:=str(item.postcode):>
    <:end:>
<:end:>

<:if flag:>
    <:for item in $client.client_adviser.address:>
        <:if item.type == '0':>
            <:for s in str(item.street).split(','):>
                <:=s.strip():>
            <:end:>
            <:=item.suburb:> <:=item.state:> <:=item.postcode:>
        <:end:>
    <:end:>
<:end:>

Telephone: <:=advisor_t:>
Facsimile: <:=$client.client_adviser.preferred_fax:>
www.perpetual.com.au
Dear
<:if ShowC:>
    <:=$client.preferred_name:>
<:end:>
<:if $partner:>
    <:if ShowP:> and
        <:=$partner.preferred_name:>
    <:end:>
<:end:>
<:if ShowJ:>
    <:=$client.preferred_name:> and
    <:=$partner.preferred_name:>
<:end:>,

Thank you for seeking our advice regarding your financial plan.
Please find enclosed your plan (Statement of Advice), which outlines our strategic and investment recommendations to help achieve your financial goals. All the recommendations are based on your personal profile and objectives which are also outlined in the document. If your situation has changed, please let us know as soon as possible.
Your personal financial plan includes detailed information on our recommendations and why they are appropriate to you. It also outlines the service we provide, any investment recommendations and associated fees and charges.
NEXT STEPS
Please read your Statement of Advice carefully. If you are happy with the recommendations and wish to implement your financial plan, please complete the ‘Authority to proceed’ letter which is found at the back of your plan. This formally instructs us to put the recommended strategies and investments in place.
MORE INFORMATION
We are committed to providing you with the highest quality service and support to ensure your needs are met. If you have any further questions, please contact me on <:=advisor_t:> or at <:=advisor_e:> your earliest convenience.
We look forward to assisting you with your financial needs now and in the future.
Yours sincerely



<:=$client.client_adviser.first_name:> <:=$client.client_adviser.last_name:>
<:=$client.client_adviser.jobtitle:>
<:=advisor_t:>






CONTENTS

PART 1 – YOUR FINANCIAL
Highlight below and F9 to update the page numbers
YOUR PROFILE	2

SCOPE OF ADVICE	2

STRATEGY RECOMMENDATIONS	2

<:if len($client.nb_soa_projections.filter('location=Projection Section'))>0:>
PROJECTIONS AND ANALYSIS	Error! Bookmark not defined.

<:end:>
INVESTMENT RECOMMENDATIONS	2

PRODUCT COMPARISONS	Error! Bookmark not defined.

FEES AND CHARGES	2

IMPORTANT INFORMATION	 2

PART 2 – ADDITIONAL INFORMATION

<:if len($client.nb_soa_projections.filter('location=Appendix'))>0:>
FINANCIAL ANALYSIS AND PROJECTIONS	Error! Bookmark not defined.

<:end:>
ABOUT YOUR STRATEGIES	2

ABOUT OUR ADMINISTRATION AND SERVICES	2

<:if len((($client.nb_soa_product_recommendations.filter('product=Perpetual  Private Investment Wrap') or $client.nb_soa_product_recommendations.filter('product=Perpetual  Private Super/Pension Wrap')) >0)) and (len(($client.nb_soa_service_recommendations.filter('service=Advisory Service') or $client.nb_soa_service_recommendations.filter('service=Custody Service') or $client.nb_soa_service_recommendations.filter('service=Discretionary Service') or $client.nb_soa_service_recommendations.filter('service=Full Financial Management Plan') or $client.nb_soa_service_recommendations.filter('service=Lifestyle Assist Service Core') or $client.nb_soa_service_recommendations.filter('service=Lifestyle Assist Service Essential'))>0)):>
ADMINISTRATION SERVICE COMPARISON 	2

<:end:>
PERPETUAL PRIVATE INVESTMENT PHILOSOPHY	2

PART 3 – AUTHORITY TO PROCEED








EXECUTIVE SUMMARY
RECOMMENDATIONS
Thank you for allowing me the opportunity to develop your Financial Plan (Statement of Advice) which has been developed to help achieve your goals and aspirations. This section of the report is designed to give you a quick snapshot of the recommendations, charges and risks which we will detail further in the document. In order to achieve your objectives, we recommend the following:
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income'))>0:>
 	INCOME
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Client'):>
            <:=item. recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management'))>0:>
 	DEBT MANAGEMENT
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest'))>0:>
 	BORROWING TO INVEST
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure'))>0:>

 	STRUCTURE
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation'))>0:>
 	TAXATION
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation'))>0:>

 	SUPERANNUATION
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning'))>0:>
 	RETIREMENT
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security'))>0:>

 	SOCIAL SECURITY
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance'))>0:>
 	RISK INSURANCE
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_product_recommendations)>0 or len($client.nb_soa_service_recommendations)>0:>
 	INVESTMENT ADMINISTRATION
    <:if len($client.nb_soa_product_recommendations.filter('entity=Client'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_product_recommendations.filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
        <:for item in $client.nb_soa_service_recommendations.filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_product_recommendations.filter('entity=Partner'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_product_recommendations.filter('entity=Joint'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Company'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Trust'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Superfund'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning'))>0:>

 	ESTATE PLANNING
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy'))>0:>
 	PHILANTHROPY
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Client'):>
            <:=item.recommendation:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Partner'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Joint'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Company'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Trust'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Superfund'):>
                <:=item.recommendation:>
            <:end:>
        <:end:>
    <:end:>
<:end:>


OUTCOMES OF OUR ADVICE
The following provides a summary of the outcomes of our advice:
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income'))>0:>
 	INCOME
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Income').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management'))>0:>
 	PROTECT
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Debt Management').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest'))>0:>
 	BORROWING TO INVEST
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Borrowing to invest').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure'))>0:>
 	STRUCTURE
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Structure').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation'))>0:>
 	TAXATION
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Taxation').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation'))>0:>
 	SUPERANNUATION
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Superannuation').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning'))>0:>
 	RETIREMENT PLANNING
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Retirement Planning').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security'))>0:>
 	SOCIAL SECURITY
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Social Security').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance'))>0:>
 	RISK INSURANCE
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Risk Insurance').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_product_recommendations)>0 or len($client.nb_soa_service_recommendations)>0:>
 	INVESTMENT ADMINISTRATION
    <:if len($client.nb_soa_product_recommendations.filter('entity=Client'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_product_recommendations.filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
        <:for item in $client.nb_soa_service_recommendations.filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_product_recommendations.filter('entity=Partner'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_product_recommendations.filter('entity=Joint'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Company'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Trust'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_product_recommendations.filter('entity=Superfund'))>0 or len($client.nb_soa_service_recommendations.filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_product_recommendations.filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
            <:for item in $client.nb_soa_service_recommendations.filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning'))>0:>
 	ESTATE PLANNING
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Estate Planning').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy'))>0:>
 	PHILANTHROPY
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Client'))>0:>
        <:=$CLIENT.PREFERRED_NAME:>
        <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Client'):>
            <:=item.outcomes:>
        <:end:>
    <:end:>
    <:if $partner:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Partner'))>0:>
            <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Partner'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
        <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Joint'))>0:>
            <:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Joint'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Company'))>0:>
        <:if Company:>
            <:for company in $company:>
                <:=COMPANY.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Company'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Trust'))>0:>
        <:if Trust:>
            <:for trust in $trust:>
                <:=TRUST.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Trust'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
    <:if len($client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Superfund'))>0:>
        <:if Superfund:>
            <:for superfund in $superfund:>
                <:=SUPERFUND.ENTITY_NAME:>
            <:end:>
            <:for item in $client.nb_soa_strategy_recommendations.filter('sub_category=Philanthropy').filter('entity=Superfund'):>
                <:=item.outcomes:>
            <:end:>
        <:end:>
    <:end:>
<:end:>


YOUR PROFILE
YOUR PERSONAL DETAILS
From the information provided by you, we understand your current personal and financial details to be as follows.  Please let us know if any of these details are incorrect, as this may impact our recommendations.
The table below provides a summary of your personal details:
<:if ShowC:>
	<:=$client.preferred_name:> <:=$client.last_name:>
Date of birth:	<:=$client.dob.format('%d %B %Y'):>
Age:	<:=$client.age:>
Marital Status:	<:=$client.marital_status:>
State of Health:	<:=$client.health:>
Employment:	<:=$client.emp_status:>
    <:if not str($client.valueOf('emp_status')) in ['Retired']:>
Expected Retirement Age:	<:=$client.retirement_age:>
    <:end:>
Postal Address:
    <:for item in $client.address.filter('preferred=True'):>
        <:let addr = str(item.street) + ', ' + str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=addr:>
<:end:>
<:if $partner:>
    <:if ShowJ:>
	<:=$client.preferred_name:> <:=$client.last_name:> 	<:=$partner.preferred_name:> <:=$partner.last_name:>
Date of birth:	<:=$client.dob.format('%d %B %Y'):>	<:=$partner.dob.format('%d %B %Y'):>
Age:	<:=$client.age:> 	<:=$partner.age:>
Marital Status:	<:=$client.marital_status:> 	<:=$partner.marital_status:>
State of Health:	<:=$client.health:> 	<:=$partner.health:>
Employment:	<:=$client.emp_status:> 	<:=$partner.emp_status:>
Expected Retirement Age:
        <:if str($client.valueOf('emp_status')) in ['Retired']:>
Not applicable
        <:else:>
            <:=$client.retirement_age:>
        <:end:>	<:if str($partner.valueOf('emp_status')) in ['Retired']:>
Not applicable
    <:else:>
        <:=$partner.retirement_age:>
    <:end:>
Postal Address:
    <:for item in $client.address.filter('preferred=True'):>
        <:let addr = str(item.street) + ', ' + str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=addr:>
<:end:>
<:if ShowP:>
	<:=$partner.preferred_name:> <:=$partner.last_name:>
Date of birth:	<:=$partner.dob.format('%d %B %Y'):>
Age:	<:=$partner.age:>
Marital Status:	<:=$partner.marital_status:>
State of Health:	<:=$partner.health:>
Employment:	<:=$partner.emp_status:>
    <:if not str($partner.valueOf('emp_status')) in ['Retired']:>
Expected Retirement Age:	<:=$partner.retirement_age:>
    <:end:>
Postal Address:
    <:for item in $client.address.filter('preferred=True'):>
        <:let addr = str(item.street) + ', ' + str(item.suburb) + ' ' + str(item.state) + ' ' + str(item.postcode):>
    <:end:>
    <:=addr:>
<:end:>
<:end:>

<:if filter(lambda x: x in ['1'], map(str,$client.valueOf('commentary_personal_details'))) :>
•	<:=$client.comment:>
<:end:>
INCOME AND EXPENSES
The following table provides an estimate of your current expenses and after-tax income based upon the information you have provided to us.
<:if 1:><:let line = 0:>
<:end:>
Income per annum	Owner	Estimated amount ($)
<:for item in $client.cashflow.filter(‘owner=Client’):>
<:if item.type.value and item.type.value.startswith(‘i’):><:let line = line + 1:>
    <:if line % 2 != 0:>
        <:=item.type:> <:=item.desc:> 	<:=$client.preferred_name:>	<:=currency(item.annual_amount.value,0):>
    <:else:>
        <:=item.type:> <:=item.desc:> 	<:=$client.preferred_name:>	<:=currency(item.annual_amount.value,0):>
    <:end:>
<:end:>
<:end:>
<:if $partner:>
<:for item in $client.cashflow.filter(‘owner=Partner’):>
    <:if item.type.value and item.type.value.startswith(‘i’):><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=item.type:> <:=item.desc:> 	<:=$partner.preferred_name:>	<:=currency(item.annual_amount.value,0):>
        <:else:>
            <:=item.type:> <:=item.desc:> 	<:=$partner.preferred_name:>	<:=currency(item.annual_amount.value,0):>
        <:end:>
    <:end:>
<:end:>
<:for item in $client.cashflow.filter(‘owner=Joint’):>
    <:if item.type.value and item.type.value.startswith(‘i’):><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=item.type:> <:=item.desc:> 	Joint	<:=currency(item.annual_amount.value,0):>
        <:else:>
            <:=item.type:> <:=item.desc:> 	Joint	<:=currency(item.annual_amount.value,0):>
        <:end:>
    <:end:>
<:end:>
<:end:>
Total income		<:=currency($client.total_income.value,0):>

<:if 1:><:let line = 0:>
<:end:>
Expenses per annum	Owner	Estimated amount ($)
<:for item in $client.cashflow.filter(‘owner=Client’):>
<:if item.type.value and item.type.value.startswith(‘e’):><:let line = line + 1:>
    <:if line % 2 != 0:>
        <:=item.type:> <:=item.desc:> 	<:=$client.preferred_name:>	<:=currency(item.annual_amount.value,0):>
    <:else:>
        <:=item.type:> <:=item.desc:> 	<:=$client.preferred_name:>	<:=currency(item.annual_amount.value,0):>
    <:end:>
<:end:>
<:end:>
<:if $partner:>
<:for item in $client.cashflow.filter(‘owner=Partner’):>
    <:if item.type.value and item.type.value.startswith(‘e’):><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=item.type:> <:=item.desc:> 	<:=$partner.preferred_name:>	<:=currency(item.annual_amount.value,0):>
        <:else:>
            <:=item.type:> <:=item.desc:> 	<:=$partner.preferred_name:>	<:=currency(item.annual_amount.value,0):>
        <:end:>
    <:end:>
<:end:>
<:for item in $client.cashflow.filter(‘owner=Joint’):>
    <:if item.type.value and item.type.value.startswith(‘e’):><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=item.type:> <:=item.desc:> 	Joint	<:=currency(item.annual_amount.value,0):>
        <:else:>
            <:=item.type:> <:=item.desc:> 	Joint	<:=currency(item.annual_amount.value,0):>
        <:end:>
    <:end:>
<:end:>
<:end:>
Estimated tax (Note to Advisers: Paraplanner to calculate)
Total expenses		<:=currency($client.total_expense.value,0):>

Income surplus/deficit		<:=currency($client.net_cashflow.value,0):>

<:if filter(lambda x: x in ['1'], map(str,$client.valueOf('commentary_cashflow'))) :>
We make the following remarks regarding your income and expenses:
•	<:=$client.cashflow_notes:>
<:end:>
<:let property_p = [x for x in $client.asset.filter('type_group=3') if str(x.type) in ['301']]:>
<:let property_i = [x for x in $client.asset.filter('type_group=3') if str(x.type) in ['302']]:>

ASSETS AND LIABILITIES
Our understanding of your assets and liabilities is set out in the table below.  To assist us in the preparation of our recommendations, we have divided these into two groups: lifestyle assets (and related borrowings) and investment assets (and related borrowings).
<:let totalvalue=0:><:let assetvalue=0:><:let liabilityvalue=0:>
<:if 1:><:let line = 0:>
<:end:>
Type	Owner	Estimated amount ($)
<:if len($client.asset.filter('type_group=5')) or len(property_p):>
Lifestyle assets:
<:for item in property_p:>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:> <:=item.desc:>

        <:=item:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
<:end:>
<:for item in $client.asset.filter('type_group=5'):>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
    <:if item.linked_liability:><:let line = 0:>
Related lifestyle assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue= item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue= item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if len($client.liability)>0:><:let line = 0:>
Other Unrelated lifestyle borrowing:
<:for item in $client.liability:>
    <:if not item.linked_asset:><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=item.owner:>
            <:=item.type:>
            <:=item.inst:>
            <:if item.owner == 'Client':>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner == 'Partner':>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:=item.owner:>
                <:end:>
            <:end:>	<:=currency(item.amount.value, 0):><:let liabilityvalue= item.amount.value+liabilityvalue:>
        <:else:>
            <:=item.type:>
            <:=item.inst:>
            <:if item.owner == 'Client':>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner == 'Partner':>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:=item.owner:>
                <:end:>
            <:end:>	<:=currency(item.amount.value, 0):><:let liabilityvalue= item.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if len($client.asset.filter('type_group=1')) or len($client.asset.filter('type_group=2')) or len(property_i):><:let line = 0:>
Investment assets:
<:for item in $client.asset.filter('type_group=2'):>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
    <:if item.linked_liability:><:let line = 0:>
Related investment assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
Superannuation Accounts:
<:for item in $client.fund:><:let line = 0:>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.fund_super_plan:>	<:=$client.preferred_name:>	<:=currency(item.fund_total_balance.value,0):><:let assetvalue=item.fund_total_balance.value+assetvalue:>
    <:else:>
        <:=item.fund_super_plan:>	<:=$client.preferred_name:>	<:=currency(item.fund_total_balance.value,0):><:let assetvalue=item.fund_total_balance.value+assetvalue:>
    <:end:>
<:end:>
<:for item in $partner.fund:><:let line = 0:>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.fund_super_plan:>	<:=$partner.preferred_name:>	<:=currency(item.fund_total_balance.value,0):><:let assetvalue=item.fund_total_balance.value+assetvalue:>
    <:else:>
        <:=item.fund_super_plan:>	<:=$partner.preferred_name:>	<:=currency(item.fund_total_balance.value,0):><:let assetvalue=item.fund_total_balance.value+assetvalue:>
    <:end:>
<:end:>
<:for item in $client.asset.filter('type_group=1'):>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
    <:if item.linked_liability:><:let line = 0:>
Related liquid assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:for item in property_i:><# investment property as investment#>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
<:end:>
<:end:>
<:if len($client.asset.filter('type_group=3'))>0:>
<:for item in $client.asset.filter('type_group=3'):>
    <:if item.linked_liability:><:let line = 0:>
Related property assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if len($client.asset.filter('type_group=7'))>0:>
<:for item in $client.asset.filter('type_group=7'):>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
    <:if item.linked_liability:><:let line = 0:>
Related business assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if len($client.asset.filter('type_group=4'))>0:>
<:for item in $client.asset.filter('type_group=4'):>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:for owner in item.owner_list:>
            <:if item.owner==”Client” and len(owner.first_name)>0:>
                <:=$client.preferred_name:>
            <:else:>
                <:if item.owner==”Partner” and len(owner.first_name)>0:>
                    <:=$partner.preferred_name:>
                <:else:>
                    <:if item.owner==”Joint” and len(owner.first_name)>0:>
Joint
                    <:else:>
                        <:=owner.preferred_name:>
                    <:end:>
                <:end:>
            <:end:>
        <:end:>	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
    <:end:>
    <:if item.linked_liability:><:let line = 0:>
Related retirement assets borrowing:
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:else:>
            <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	<:=item.linked_liability_owner:>	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if Company:>
<:for company in $company:>
    <:if len(company.asset)>0:><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=company.entity_name:> assets:

        <:else:>
            <:=company.entity_name:> assets:
        <:end:>
        <:for item in company.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.desc:>	Company	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:else:>
                <:=item.type:> <:=item.desc:>	Company	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:end:>
            <:if item.linked_liability:><:let line = 0:>
Related borrowing:
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Company	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Company	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
    <:if len(company.liability)>0:><:let line = 0:>
Other Unrelated borrowing:
        <:for item in company.liability:>
            <:if not item.linked_asset:><:let line = line + 1:>
                <:if line % 2 != 0:>
                    <:=item.type:> <:=item.inst:>	Company	<:=currency(item.amount.value, 0):> <:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.type:> <:=item.inst:>	Company	<:=currency(item.amount.value, 0):> <:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if Trust:>
<:for trust in $trust:>
    <:if len(trust.asset) > 0:><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=trust.entity_name:> assets:
        <:else:>
            <:=trust.entity_name:> assets:
        <:end:>
        <:for item in trust.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.desc:>	Trust	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:else:>
                <:=item.type:> <:=item.desc:>	Trust	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:end:>
            <:if item.linked_liability:><:let line = 0:>
Related borrowing:
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Trust	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Trust	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
    <:if len(trust.liability)>0:><:let line = 0:>
Other Unrelated borrowing:
        <:for item in trust.liability:>
            <:if not item.linked_asset:><:let line = line + 1:>
                <:if line % 2 != 0:>
                    <:=item.type:> <:=item.inst:>	Trust	<:=currency(item.amount.value, 0):><:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.type:> <:=item.inst:>	Trust	<:=currency(item.amount.value, 0):> <:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if Superfund:>
<:for superfund in $superfund:>
    <:if len(superfund.asset) > 0:><:let line = line + 1:>
        <:if line % 2 != 0:>
            <:=superfund.entity_name:> assets:
        <:else:>
            <:=superfund.entity_name:> assets:
        <:end:>
        <:for item in superfund.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.desc:>
	Superfund	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:else:>
                <:=item.type:> <:=item.desc:>
	Superfund	<:=currency(item.amount.value,0):><:let assetvalue= item.amount.value+assetvalue:>
            <:end:>
            <:if item.linked_liability:><:let line = 0:>
Related borrowing:
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Superfund	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.linked_liability.type:> <:=item.linked_liability.inst:>	Superfund	<:=currency(item.linked_liability.amount.value,0):><:let liabilityvalue=item.linked_liability.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
    <:if len(superfund.liability)>0:><:let line = 0:>
Other Unrelated borrowing:
        <:for item in superfund.liability:>
            <:if not item.linked_asset:><:let line = line + 1:>
                <:if line % 2 != 0:>
                    <:=item.type:> <:=item.inst:>	Superfund	<:=currency(item.amount.value, 0):> <:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:else:>
                    <:=item.type:> <:=item.inst:>	Superfund	<:=currency(item.amount.value, 0):> <:let liabilityvalue=item.amount.value+liabilityvalue:>
                <:end:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:end:>
<:if 1:><:let line = line + 1:>
<:end:>
<:let totalvalue=assetvalue-liabilityvalue:>
<:if line % 2 != 0:>
Total assets:		<:=currency(assetvalue,0):>
Total borrowings: 		<:=currency(liabilityvalue,0):>
<:else:>
Total assets:		<:=currency(assetvalue,0):>
Total borrowings: 		<:=currency(liabilityvalue,0):>
<:end:>
Net worth		<:=currency(totalvalue,0):>
*Included within the scope of advice and available for investment.

<:if len($client.liability)>0:><:let line = 0:>
The following table summarises your liabilities noted above:
Description	Borrower	Amount owed ($)	Repayments ($)	Interest rate (%)	I/O or P&I	Loan term	Personal deductible (%)
<:for item in $client.liability:>
    <:if 1:><:let line = line + 1:>
    <:end:>
    <:if line % 2 != 0:>
        <:=item.type:> <:=item.inst:> 	<:=item.owner:>	<:=currency(item.amount.value,0):>	<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
    <:else:>
        <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=currency(item.amount.value,0):>	<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
    <:end:>
<:end:>
<:if Company:>
    <:for company in $company:>
        <:for item in company.liability:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	<:=currency(item.amount.value,0):>	<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:else:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	<:=currency(item.amount.value,0):>	<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if Trust:>
    <:for trust in $trust:>
        <:for item in trust.liability:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	$<:=currency(item.amount.value,0):>	$<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:else:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	$<:=currency(item.amount.value,0):>	$<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
<:if Superfund:>
    <:for superfund in $superfund:>
        <:for item in superfund.liability:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	$<:=currency(item.amount.value,0):>	$<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:else:>
                <:=item.type:> <:=item.inst:> 	<:=item.owner:>	$<:=currency(item.amount.value,0):>	$<:=currency(item.repayment.value,0):> <:=item.frequency:>	<:=item.rate:> <:=item.rate_type:>	<:=item.repayment_type:> 	<:=item.loan_term_amount:> <:=item.loan_term_type:>	<:=item.deductible:>
            <:end:>
        <:end:>
    <:end:>
<:end:>
Total		$<:=currency($client.total_liabilities.value,0):>
*Included within the scope of advice and available for investment.
<:end:>

<:if filter(lambda x: x in ['1'], map(str,$client.valueOf('commentary_net_position'))) :>
•	<:=$client.balance_sheet_comments:>
<:end:>
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
        <:=item.type:>
        <:=item.desc:>
        <:if 1:>
            <:let feq = item.frequency:>
        <:end:>
        <:=feq:>	<:=currency(item.payment.value,0):>
        <:let total = total + int(item.payment.value) * int(freq):>
    <:else:>
        <:=item.type:>
        <:=item.desc:>
        <:if 1:>
            <:let feq = item.frequency:>
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
            <:=item.type:>
            <:=item.desc:>
            <:if 1:>
                <:let feq = item.frequency:>
            <:end:>
            <:=feq:>	<:=currency(item.payment.value,0):>
            <:let total = total + int(item.payment.value) * int(freq):>
        <:else:>
            <:=item.type:>
            <:=item.desc:>
            <:if 1:>
                <:let feq = item.frequency:>
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
RISK INSURANCE
<:if len(($client.insurance_by_cover) or ($partner.insurance_by_cover))>0:>
You have advised that you currently hold the following risk insurance policies.
<:if len($client.insurance_by_cover)>0:><:let line = 0:><:let total = 0:>
Life insured	Owner	Insurer 	Type and level of cover	Premium per annum ($)	Loadings/ exclusions
    <:for item in $client.insurance_by_cover:>
        <:if 1:><:let freq = item.frequency:>
        <:end:>
        <:if 1:><:let line = line + 1:>
        <:end:>
        <:if line % 2 != 0:>
            <:=item.covers()[0].life_insured:>
            <:if item.owner_type == 'Client' or item.owner_type == 'Partner':>
                <:=item.owner.preferred_name:>
            <:else:>
                <:=item.owner.name:>
            <:end:>	<:=item.coy:>	Life $<:=currency(int(item.life_sum_insured_by_cover()),0):>
TPD $<:=currency(int(item.tpd_sum_insured_by_cover()),0):>
Trauma $<:=currency(int(item.trauma_sum_insured_by_cover()),0):>
Income Protection $<:=currency(int(item.ip_benefit_amount_by_cover()),0):>	$<:=currency(int(item.benefit_premium.value) * int(freq),0):>
            <:let total = total + int(item.benefit_premium.value) * int(freq):>
        <:else:>
            <:=item.covers()[0].life_insured:>
            <:if item.owner_type == 'Client' or item.owner_type == 'Partner':>
                <:=item.owner.preferred_name:>
            <:else:>
                <:=item.owner.name:>
            <:end:>	<:=item.coy:>	Life $<:=currency(int(item.life_sum_insured_by_cover()),0):>
TPD $<:=currency(int(item.tpd_sum_insured_by_cover()),0):>
Trauma $<:=currency(int(item.trauma_sum_insured_by_cover()),0):>
Income Protection $<:=currency(int(item.ip_benefit_amount_by_cover()),0):>	$<:=currency(int(item.benefit_premium.value) * int(freq),0):>
            <:let total = total + int(item.benefit_premium.value) * int(freq):>
        <:end:>
    <:end:>
Total Annual Premium				$<:=currency(total,0):>
<:end:>


<:if $partner:>
    <:if len($partner.insurance_by_cover)>0:><:let line = 0:><:let total = 0:>
Life insured	Owner	Insurer 	Type and level of cover	Premium per annum ($)	Loadings/ exclusions
        <:for item in $partner.insurance_by_cover:>
            <:if 1:><:let freq = item.frequency:>
            <:end:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.covers()[0].life_insured:>
                <:if item.owner_type == 'Client' or item.owner_type == 'Partner':>
                    <:=item.owner.preferred_name:>
                <:else:>
                    <:=item.owner.name:>
                <:end:>	<:=item.coy:>	Life $<:=currency(int(item.life_sum_insured_by_cover()),0):>
TPD $<:=currency(int(item.tpd_sum_insured_by_cover()),0):>
Trauma $<:=currency(int(item.trauma_sum_insured_by_cover()),0):>
Income Protection $<:=currency(int(item.ip_benefit_amount_by_cover()),0):>	$<:=currency(int(item.benefit_premium.value) * int(freq),0):>
                <:let total = total + int(item.benefit_premium.value) * int(freq):>
            <:else:>
                <:=item.covers()[0].life_insured:>
                <:if item.owner_type == 'Client' or item.owner_type == 'Partner':>
                    <:=item.owner.preferred_name:>
                <:else:>
                    <:=item.owner.name:>
                <:end:>	<:=item.coy:>	Life $<:=currency(int(item.life_sum_insured_by_cover()),0):>
TPD $<:=currency(int(item.tpd_sum_insured_by_cover()),0):>
Trauma $<:=currency(int(item.trauma_sum_insured_by_cover()),0):>
Income Protection $<:=currency(int(item.ip_benefit_amount_by_cover()),0):>	$<:=currency(int(item.benefit_premium.value) * int(freq),0):>
                <:let total = total + int(item.benefit_premium.value) * int(freq):>
            <:end:>
        <:end:>
Total Annual Premium				$<:=currency(total,0):>
    <:end:>
<:end:>
<:else:>
You have advised that you do not currently hold any risk insurance policies.
<:end:>
<:if filter(lambda x: x in ['1'], map(str,$client.valueOf('commentary_risk_insurance'))) :>
•	<:=$client.risk_general_comment:>
<:end:>
ESTATE PLANNING
You have advised that your estate planning situation is as follows:
<:if ShowC:>
	<:=$client.preferred_name:> <:=$client.last_name:>
Does a Will exist?	<:=$client.will_exists:>
Date of the Will	<:=$client.date_of_will:>
Location of the Will	<:=$client.will_location:>
Name of the Executor	<:=$client.executor2:>
Has the Will been reviewed in the last 2 years	<:=$client.will_reviewed_last_2_years:>
Is there a testamentary trust?	<:=$client.testamentary_trusts:>
Is there a General Power of Attorney?	<:=$client.do_you_have_pow:>
Is there an Enduring Power of Attorney?	<:=$client.enduring_power_of_attorney:>
Is there a Medical Power of Attorney? 	<:=$client.do_you_have_a_medical_power:>

<:end:>
<:if $partner:>
<:if ShowJ:>
	<:=$client.preferred_name:> <:=$client.last_name:>	<:=$partner.preferred_name:> <:=$partner.last_name:>
Does a Will exist?	<:=$client.will_exists:> 	<:=$partner.will_exists:>
Date of the Will	<:=$client.date_of_will:> 	<:=$partner.date_of_will:>
Location of the Will	<:=$client.will_location:> 	<:=$partner.will_location:>
Name of the Executor	<:=$client.executor2:>	<:=$partner.executor2:>
Has the Will been reviewed in the last 2 years	<:=$client.will_reviewed_last_2_years:> 	<:=$partner.will_reviewed_last_2_years:>
Is there a testamentary trust?	<:=$client.testamentary_trusts:> 	<:=$partner.testamentary_trusts:>
Is there a General Power of Attorney?	<:=$client.do_you_have_pow:> 	<:=$partner.do_you_have_pow:>
Is there an Enduring Power of Attorney?	<:=$client.enduring_power_of_attorney:> 	<:=$partner.enduring_power_of_attorney:>
Is there a Medical Power of Attorney? 	<:=$client.do_you_have_a_medical_power:>	<:=$partner.do_you_have_a_medical_power:>

<:end:>
<:if ShowP:>
	<:=$partner.preferred_name:> <:=$partner.last_name:>
Does a Will exist?	<:=$partner.will_exists:>
Date of the Will	<:=$partner.date_of_will:>
Location of the Will	<:=$partner.will_location:>
Name of the Executor	<:=$partner.executor2:>
Has the Will been reviewed in the last 2 years	<:=$partner.will_reviewed_last_2_years:>
Is there a testamentary trust?	<:=$partner.testamentary_trusts:>
Is there a General Power of Attorney?	<:=$partner.do_you_have_pow:>
Is there an Enduring Power of Attorney?	<:=$partner.enduring_power_of_attorney:>
Is there a Medical Power of Attorney? 	<:=$partner.do_you_have_a_medical_power:>

<:end:>
<:end:>
<:if not $client.valueOf('bequeathed_assets')== 0 :>
<:=$client.bequeathed_assets:>
<:end:>
<:if filter(lambda x: x in ['1'], map(str,$client.valueOf('commentary_estate_planning'))) :>
<:=$client.commentary_estate_planning:>
<:end:>
<:if Superfund:>
<:for superfund in $superfund:>
    <:if str(superfund.valueOf('type_of_superfund')) in ['SMSF']:>
SELF MANAGED SUPER FUND
	<:=superfund.entity_name:>
Establishment date	<:=superfund.superfund_dod:>
Fund name	<:=superfund.entity_name:>
Trustee:
        <:for s in $superfund:><# loop in SMSF #>
            <:for t in s.trustee:><# loop in Trustee #>
                <:=t.fname:> <:=t.lname:>
            <:end:>
        <:end:>
Member:
        <:for item in superfund.fundmember:>
            <:=item.fname:> <:=item.lname:>
        <:end:>
    <:end:>

    <:if str(superfund.valueOf('type_of_superfund')) in ['SAF']:>
SMALL APRA FUND
	<:=superfund.entity_name:>
Establishment date	<:=superfund.superfund_dod:>
Fund name	<:=superfund.entity_name:>
Member:
        <:for item in superfund.fundmember:>
            <:=item.fname:> <:=item.lname:>
        <:end:>
    <:end:>
SUPERANNUATION INVESTMENT STRATEGY
It is a legal requirement for a DIY Superannuation Fund to have its own investment strategy. The strategy for <:=superfund.entity_name:> is <:=superfund.smsf_investment_strategy:> and has the following asset mix:
    <:if str(superfund.valueOf('smsf_investment_strategy')) in ['Secure']:>
Asset sector	Minimum (%)	Maximum (%)
Growth	0	10
Defensive	90	100
    <:end:>
    <:if str(superfund.valueOf('smsf_investment_strategy')) in ['Conservative Growth']:>
Asset sector	Minimum (%)	Maximum (%)
Growth	0	30
Defensive	70	100
    <:end:>
    <:if str(superfund.valueOf('smsf_investment_strategy')) in ['Balanced Growth']:>
Asset sector	Minimum (%)	Maximum (%)
Growth	30	70
Defensive	30	70
    <:end:>
    <:if str(superfund.valueOf('smsf_investment_strategy')) in ['Growth']:>
Asset sector	Minimum (%)	Maximum (%)
Growth	50	80
Defensive	20	50
    <:end:>
    <:if str(superfund.valueOf('smsf_investment_strategy')) in ['High Growth']:>
Asset sector	Minimum (%)	Maximum (%)
Growth	70	98
Defensive	2	30
    <:end:>
INVESTMENTS
    <:let empty=0:>
    <:if len(superfund.asset)>0:><:let line = 0:><:let empty=1:>
Investments as at <:=superfund.balancesheet_val_date:> 	Estimated amount ($)
        <:for item in superfund.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:else:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:end:>
        <:end:>
Total assets:	$<:=superfund.total_assets:>
    <:end:>
    <:for superfund in $superfund:><:let empty=1:>
        <:let proposals=superfund.DoReport.ipsv.any_report('value', portfolios='CX', date='Today', subreports=[‘portfolioid’, 'subfund','code','exchange'], report_source='proposedandcurrent'):>
        <:let line =0:>
        <:for proposal in proposals:>
            <:if floatify(proposal[‘unformatted_current_value’])>0.00:>
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:else:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:end:>
            <:end:>
        <:end:>
Total assets:	$<:= currency(sum([floatify(tr[‘unformatted_current_value’]) for tr in proposals]) / 100.0,0):>
    <:end:>
    <:if empty==0:>
The Fund has no assets.
    <:end:>

    <:if str(superfund.valueOf('type_of_superfund')) in ['SMSF']:>
LIABILITIES
        <:if len(superfund.liability)>0:><:let line = 0:>
Loan	Owner	Rate (%)	Amount ($)	Repayments($)
            <:for item in superfund.liability:>
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
                <:else:>
                    <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
                <:end:>
            <:end:>
Total 			$<:=superfund.total_liabilities:>
        <:else:>
The Fund has no liabilities.
        <:end:>
    <:end:>
    <:if filter(lambda x: x in ['1'], map(str, superfund.valueOf('commentary_net_position'))):>
•	<:=superfund.balance_sheet_comments:>
    <:end:>
MEMBER BALANCES
    <:if len(superfund.fundmember)>0:><:let line = 0:>
Member	Phase (Accumulation/Pension)	Amount ($)
        <:for item in superfund.fundmember:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.fname:> <:=item.lname:>	<:=item.phase:>	$<:=item.fund_balance:>
            <:else:>
                <:=item.fname:> <:=item.lname:>	<:=item.phase:>	$<:=item.fund_balance:>
            <:end:>
        <:end:>
    <:else:>
The Fund currently has no members.
    <:end:>

    <:if str(superfund.valueOf('type_of_superfund')) in ['SMSF']:>
INSURANCES WITHIN THE FUND
        <:if len(superfund.insurance_by_cover)>0:><:let line = 0:>
You have advised that the Fund currently holds the following risk insurance policies.
Life insured	Type and level of cover	Premium per annum ($)
            <:for item in superfund.insurance_by_cover:>
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=item.covers()[0].life_insured:> - <:=item.coy:>	Life $<:=item.life_sum_insured_by_cover:>
TPD $<:=item.tpd_sum_insured_by_cover:>
Trauma $<:=item.trauma_sum_insured_by_cover:>
Income Protection $<:=item.ip_benefit_amount_by_cover:>	$<:=item.benefit_premium:> <:=item.frequency:>
                <:else:>
                    <:=item.covers()[0].life_insured:> - <:=item.coy:>	Life $<:=item.life_sum_insured_by_cover:>
TPD $<:=item.tpd_sum_insured_by_cover:>
Trauma $<:=item.trauma_sum_insured_by_cover:>
Income Protection $<:=item.ip_benefit_amount_by_cover:>	$<:=item.benefit_premium:> <:=item.frequency:>
                <:end:>
            <:end:>
        <:else:>
You have advised the Fund does not currently hold any risk insurance policies.
        <:end:>

        <:if filter(lambda x: x in ['1'], map(str,superfund.valueOf('commentary_risk_insurance'))) :>
•	<:=superfund.risk_general_comment:>
        <:end:>
    <:end:>
<:end:>
<:end:>

<:if Trust:>
<:for trust in $trust:>
TRUST
	<:=trust.entity_name:>
Name	<:=trust.entity_name:>
Trustee	<:=trust.trust_trustee:>
BENEFICIARIES
    <:if len(trust.beneficiary)>0:><:let line = 0:>
Names	Date of birth (applicable for minors)
        <:for item in trust.beneficiary:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.entityname:>	<:=item.beneficiary_dob:>
            <:else:>
                <:=item.entityname:>	<:=item.beneficiary_dob:>
            <:end:>
        <:end:>
    <:else:>
You have not advised of any Beneficiaries of the Trust.
    <:end:>
INVESTMENTS
    <:let empty=0:>
    <:if len(trust.asset)>0:><:let line = 0:><:let empty=1:>
Investments as at <:=trust.balancesheet_val_date:> 	Estimated amount ($)
        <:for item in trust.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:else:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:end:>
        <:end:>
Total assets:	$<:=trust.total_assets:>
    <:end:>
    <:for trust in $trust:><:let empty=1:>
        <:let proposals=trust.DoReport.ipsv.any_report('value', portfolios='CX', date='Today', subreports=[‘portfolioid’, 'subfund','code','exchange'], report_source='proposedandcurrent'):>
        <:let line =0:>
        <:for proposal in proposals:>
            <:if floatify(proposal[‘unformatted_current_value’])>0.00:>
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:else:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:end:>
            <:end:>
        <:end:>
Total assets:	$<:= currency(sum([floatify(tr[‘unformatted_current_value’]) for tr in proposals]) / 100.0,0):>
    <:end:>
    <:if empty==0:>
The Trust has no assets.
    <:end:>

LIABILITIES
    <:if len(trust.liability)>0:><:let line = 0:>
Loan	Owner	Rate (%)	Amount ($)	Repayments($)
        <:for item in trust.liability:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
            <:else:>
                <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
            <:end:>
        <:end:>
Total 			$<:=trust.total_liabilities:>
    <:else:>
The Trust has no liabilities.
    <:end:>

    <:if filter(lambda x: x in ['1'], map(str,trust.valueOf('commentary_net_position'))) :>
•	<:=trust.balance_sheet_comments:>
    <:end:>
<:end:>
<:end:>

<:if Company:>
<:for company in $company:>
COMPANY
	<:=company.entity_name:>
Name	<:=company.entity_name:>
Date of incorporation:	<:=company.date_of_inception:>
Director	<:=company.company_director:>
Company Secretary	<:=company.company_secretary:>
Shareholder	<:=company.company_shareholder:>

INVESTMENTS
    <:let empty=0:>
    <:if len(company.asset)>0:><:let line = 0:><:let empty=1:>
Investments as at <:=company.balancesheet_val_date:> 	Estimated amount ($)
        <:for item in company.asset:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:else:>
                <:=item.type:> - <:=item.desc:>
	$<:=currency(item.amount.value,0):>
            <:end:>
        <:end:>
Total assets:	$<:=company.total_assets:>
    <:end:>
    <:for company in $company:><:let empty=1:>
        <:let proposals=company.DoReport.ipsv.any_report('value', portfolios='CX', date='Today', subreports=[‘portfolioid’, 'subfund','code','exchange'], report_source='proposedandcurrent'):>
        <:let line =0:>
        <:for proposal in proposals:>
            <:if floatify(proposal[‘unformatted_current_value’])>0.00:>
                <:if 1:><:let line = line + 1:>
                <:end:>
                <:if line % 2 != 0:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:else:>
                    <:=proposal['description']:>	$<:=currency(floatify(proposal[‘unformatted_current_value’]) / 100.0,0):>
                <:end:>
            <:end:>
        <:end:>
Total assets:	$<:= currency(sum([floatify(tr[‘unformatted_current_value’]) for tr in proposals]) / 100.0,0):>
    <:end:>
    <:if empty==0:>
The Company has no assets.
    <:end:>

LIABILITIES
    <:if len(company.liability)>0:><:let line = 0:>
Loan	Owner	Rate (%)	Amount ($)	Repayments($)
        <:for item in company.liability:>
            <:if 1:><:let line = line + 1:>
            <:end:>
            <:if line % 2 != 0:>
                <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
            <:else:>
                <:=item.type:> <:=item.inst:>	<:=item.owner:>	<:=item.rate:> <:=item.rate_type:>	$<:=item.amount:>	$<:=item.repayment:> <:=item.frequency:>
            <:end:>
        <:end:>
Total 			$<:=company.total_liabilities:>
    <:else:>
The Company has no liabilities.
    <:end:>

    <:if filter(lambda x: x in ['1'], map(str,company.valueOf('commentary_net_position'))) :>
•	<:=company.balance_sheet_comments:>
    <:end:>
<:end:>
<:end:>

YOUR GOALS AND OBJECTIVES
<:if ShowC:>
<:=$client.preferred_name:>, you have sought our advice for the following reasons:
<:end:>
<:if $partner:>
<:if ShowP:>
    <:=$partner.preferred_name:>, you have sought our advice for the following reasons:
<:end:>
<:if ShowJ:>
    <:=$client.preferred_name:> and <:=$partner.preferred_name:>, you have sought our advice for the following reasons:
<:end:>
<:end:>
•	<:=$client.reason_for_seeking_advice:>

We discussed your lifestyle goals and how these translate into financial goals. To ensure we are clear on what is most important for you to achieve, we break your goals and objectives into four distinct categories:
Lifestyle

Grow

	Protect
Legacy

Enabling your ideal lifestyle both now and into the future.	Putting your wealth to work the most effective way.	Protecting your family, your lifestyle and your wealth. 	Ensuring your wealth fulfils your intentions for future generations.

Based on our understanding, your current objectives are as follows:
<:if len($client.advice_goals.filter('category=Lifestyle'))>0:>
Lifestyle	Time Frame
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives'))>0:>
 	PERSONAL GOALS & OBJECTIVES
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Client'))>0:>
	<:=$CLIENT.PREFERRED_NAME:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Client')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Partner'))>0:>
	<:=$PARTNER.PREFERRED_NAME:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Partner')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Joint'))>0:>
	<:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Joint')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Company'))>0:>
<:if Company:>
    <:for company in $company:>
	<:=COMPANY.ENTITY_NAME:>
    <:end:>
<:end:>
<:end:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Company')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Trust'))>0:>
<:if Trust:>
    <:for trust in $trust:>
	<:=TRUST.ENTITY_NAME:>
    <:end:>
<:end:>
<:end:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Trust')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Superfund'))>0:>
<:if Superfund:>
    <:for superfund in $superfund:>
	<:=SUPERFUND.ENTITY_NAME:>
    <:end:>
<:end:>
<:end:>
<:for item in ($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Personal Goals & Objectives').filter('entity=Superfund')):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives'))>0:>
 	FINANCIAL GOALS & OBJECTIVES
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Client'))>0:>
	<:=$CLIENT.PREFERRED_NAME:>
<:for item in $client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Client'):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Partner'))>0:>
	<:=$PARTNER.PREFERRED_NAME:>
<:for item in $client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Partner'):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
<:end:>
<:if len($client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Joint'))>0:>
	<:=$CLIENT.PREFERRED_NAME:> AND <:=$PARTNER.PREFERRED_NAME:>
<:end:>
<:for item in $client.advice_goals.filter('category=Lifestyle').filter('sub_category=Financial Goals & Objectives').filter('entity=Joint'):>
	•	<:=item.details:> 	<:=item.timeframe:>
<:end:>
""", message_only=True, debug=0)
    print(r)