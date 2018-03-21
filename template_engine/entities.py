from fuzzier.jison import Jison
from template_engine.features import *


class BaseEntity:
    def __init__(self, context):
        if isinstance(context, str):
            try:
                context = Jison(context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in context:
            setattr(self, key, context.get(key))

    def sample_method(self, text):
        return text


class BaseOtherEntity:
    def __init__(self, context):
        if isinstance(context, str):
            try:
                context = Jison(context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in context:
            setattr(self, key, context.get(key))


class Client(BaseEntity):
    def __init__(self, basic_context, client_context: dict = None):
        super().__init__(basic_context)
        if isinstance(client_context, str):
            try:
                client_context = Jison(client_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        if client_context:
            for key in client_context:
                setattr(self, key, client_context.get(key))


class Partner(BaseEntity):
    def __init__(self, basic_context, partner_context):
        super().__init__(basic_context)
        if isinstance(partner_context, str):
            try:
                partner_context = Jison(partner_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in partner_context:
            setattr(self, key, partner_context.get(key))


class Trust(BaseOtherEntity):
    def __init__(self, basic_context, trust_context):
        super().__init__(basic_context)
        if isinstance(trust_context, str):
            try:
                trust_context = Jison(trust_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in trust_context:
            setattr(self, key, trust_context.get(key))


class Superfund(BaseOtherEntity):
    def __init__(self, basic_context, super_context):
        super().__init__(basic_context)
        if isinstance(super_context, str):
            try:
                super_context = Jison(super_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in super_context:
            setattr(self, key, super_context.get(key))


class Company(BaseOtherEntity):
    def __init__(self, basic_context, company_context):
        super().__init__(basic_context)
        if isinstance(company_context, str):
            try:
                company_context = Jison(company_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in company_context:
            setattr(self, key, company_context.get(key))


class Partnership(BaseOtherEntity):
    def __init__(self, basic_context, partnership_context):
        super().__init__(basic_context)
        if isinstance(partnership_context, str):
            try:
                partnership_context = Jison(partnership_context).parse()
            except:
                raise Exception('Invalid Json for entity data')

        for key in partnership_context:
            setattr(self, key, partnership_context.get(key))


class TrustList:
    def __init__(self, trust_list: list = None):
        if trust_list is not None:
            self.l = trust_list
        else:
            self.l = []

    def __iter__(self):
        return iter(self.l)

    def __len__(self):
        return len(self.l)

    def add(self, trust: Trust):
        self.l.append(trust)

    def remove(self):
        pass


class SuperfundList:
    def __init__(self, superfund_list: list = None):
        if superfund_list is not None:
            self.l = superfund_list
        else:
            self.l = []

    def __iter__(self):
        return iter(self.l)

    def __len__(self):
        return len(self.l)

    def add(self, super: Superfund):
        self.l.append(super)

    def remove(self):
        pass


class CompanyList:
    def __init__(self, company_list: list = None):
        if company_list is not None:
            self.l = company_list
        else:
            self.l = []

    def __iter__(self):
        return iter(self.l)

    def __len__(self):
        return len(self.l)

    def add(self, com: Company):
        self.l.append(com)

    def remove(self):
        pass


class PartnershipList:
    def __init__(self, partnership_list: list = None):
        if partnership_list is not None:
            self.l = partnership_list
        else:
            self.l = []

    def __iter__(self):
        return iter(self.l)

    def __len__(self):
        return len(self.l)

    def add(self, par: Partnership):
        self.l.append(par)

    def remove(self):
        pass
