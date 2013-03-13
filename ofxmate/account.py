import security
from ofxparse import OfxParser
from ofxparse.ofxparse import InvestmentAccount as OfxInvestmentAccount
from request import Builder
from institution import Institution
from settings import Settings
import StringIO, hashlib, time, datetime
import ofxclient.account

class Account(ofxclient.account.Account):

    def is_bank_account(self):
        return 1 if self.type_key() == 'bank' else 0

    def is_brokerage_account(self):
        return 1 if self.type_key() == 'brokerage' else 0

    def is_credit_card_account(self):
        return 1 if self.type_key() == 'credit' else 0
        
    def type_key(self):
        if hasattr(self,'broker_id'):
            return 'brokerage' 
        if hasattr(self,'routing_number'):
            return 'bank'
        return 'credit'

    def type_str(self):
        if self.is_bank_account():
            return 'Bank Account'
        if self.is_brokerage_account():
            return 'Brokerage Account'
        if self.is_credit_card_account():
            return 'Credit Card Account'

    def save(self):
        # always save the original account number in the keystore
        security.set_password( self.local_id(), self.number or '' )
        struct = {
            'local_id': self.local_id(),
            'institution': self.institution.local_id(),
            'description': self.description,
            'routing_number': self.routing_number if hasattr(self,'routing_number') else '',
            'account_type': self.account_type if hasattr(self,'account_type') else '',
            'broker_id': self.broker_id if hasattr(self,'broker_id') else '',
            'type': self.type_key(),
        } 

        config = Settings.config()
        new_accounts = []
        for a in Settings.accounts():
            if a['local_id'] != self.local_id():
                new_accounts.append(a)
        new_accounts.append(struct)

        config['accounts'] = new_accounts
        Settings.config_save(config)


    @staticmethod
    def list():
        return [ Account.from_config(s) for s in Settings.accounts() ]

    @staticmethod
    def list_from_institution( institution ):
        return [ x for x in Account.list() if x.institution == institution ]

    @staticmethod
    def query_from_institution( institution ):
        found = super( Institution, institution ).accounts()
        accounts = []
        for a in found:
            add = None
            if type(a) == ofxclient.account.BrokerageAccount:
                add = BrokerageAccount(
                    number = a.number,
                    institution = institution,
                    broker_id = a.broker_id,
                    description = a.description
                )
            if type(a) == ofxclient.account.CreditCardAccount:
                add = CreditCardAccount(
                    number = a.number,
                    institution = institution,
                    description = a.description
                )
            if type(a) == ofxclient.account.BankAccount:
                add = BankAccount(
                    number = a.number,
                    institution = institution,
                    routing_number = a.routing_number,
                    account_type = a.account_type,
                    description = a.description
                )
            if add:
                accounts.append( add )
        return accounts

    @staticmethod
    def from_config(c):
        institution = Institution.from_config(Settings.banks(c['institution']))
        number = security.get_password( c['local_id'] )
        if c['type'] == 'brokerage':
            return BrokerageAccount(
                    number = number,
                    institution = institution,
                    broker_id = c['broker_id'],
                    description = c['description']
            )
        if c['type'] == 'credit':
            return CreditCardAccount(
                    number = number,
                    institution = institution,
                    description = c['description']
            )
        if c['type'] == 'bank':
            return BankAccount(
                    number = number,
                    institution = institution,
                    routing_number = c['routing_number'],
                    account_type = c['account_type'],
                    description = c['description']
            )

    @staticmethod
    def from_id(guid):
        return Account.from_config( Settings.accounts(guid) )

    def delete(self):
        # remove the account number from the security store
        security.set_password( self.local_id(), None )

        config = Settings.config()
        new_accounts = []
        for a in Settings.accounts():
            if a['local_id'] != self.local_id():
                new_accounts.append(a)
        config['accounts'] = new_accounts
        Settings.config_save(config)

class BrokerageAccount(Account, ofxclient.account.BrokerageAccount):
    pass
class CreditCardAccount(Account, ofxclient.account.CreditCardAccount):
    pass
class BankAccount(Account, ofxclient.account.BankAccount):
    pass
