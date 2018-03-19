from template_engine.entities import *

client = Client({'name': 'Butcher'})
partner = Partner({'name': 'Butcher2'}, {})
trust = TrustList([Trust({'name': 'Butcher trust'}, {'entity_name': 'trust1'})])
superfund = SuperfundList([Trust({'name': 'Butcher super'}, {'entity_name': 'super1'})])
company = CompanyList([Trust({'name': 'Butcher com'}, {'entity_name': 'com1'})])
partnership = PartnershipList()