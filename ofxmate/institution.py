import hashlib
import logging
import ofxclient.institution
import os.path
import security
import StringIO
from ofxhome import OFXHome
from ofxhome import Institution as OFXHomeInstitution
from settings import Settings

class Institution(ofxclient.institution.Institution):

    def __init__(self, ofxhome_id=None, **kwargs):
        super(Institution,self).__init__(**kwargs)
        if ofxhome_id:
            self.ofxhome_id = ofxhome_id

    @staticmethod
    def from_config(c):
        return Institution(
            id = c['id'],
            org = c['org'],
            url = c['url'],
            username = c['username'],
            password = security.get_password( c['local_id'] ),
            description = c['description']
        )

    @staticmethod
    def from_id(local_id):
        return Institution.from_config( Settings.banks(local_id) )

    @staticmethod
    def list():
        return [ Institution.from_config(s) for s in Settings.banks() ]

    @staticmethod
    def from_ofxhome(result):
        return Institution.from_ofxhome_id(result['id'])

    @staticmethod
    def from_ofxhome_id(id):
        dsn = bank_config(id)
        return Institution(
            id = dsn['fid'],
            org = dsn['org'],
            url = dsn['url'],
            username = None,
            password = None,
            description = dsn['name'],
            ofxhome_id = id
        )

    @staticmethod
    def search(query):
        results = OFXHome.search(query)
        return [ Institution.from_ofxhome(r) for r in results ]

    def save(self):
        # always save the password
        security.set_password(
            self.local_id(),
            self.password or ''
        )

        config = Settings.config()
        new_banks = []
        for s in Settings.banks():
            i = Institution.from_config(s)
            if i != self:
                new_banks.append(s)
        new_banks.append({
            'id': self.id,
            'org': self.org,
            'url': self.url,
            'username': self.username,
            'description': self.description,
            'local_id': self.local_id()
        })

        config['banks'] = new_banks
        Settings.config_save(config)

    def delete(self):
        # delete the password
        security.set_password(
            self.local_id(),
            None
        )

        accounts = self.local_accounts()
        for a in accounts:
            a.delete()

        config = Settings.config()
        new_banks = []
        for s in Settings.banks():
            i = Institution.from_config(s)
            if i != self:
                new_banks.append(s)
        config['banks'] = new_banks
        Settings.config_save(config)

    def accounts(self):
        local = self.local_accounts()
        if len(local):
            return local
        else:
            return self.cache_remote_accounts()

    def remote_accounts(self):
        return Account.query_from_institution( self )

    def cache_remote_accounts(self):
        accounts = self.remote_accounts()
        for a in accounts:
            a.save()
        return accounts

    def local_accounts(self):
        return Account.list_from_institution( self )

    def __eq__(self, b):
        return self.local_id() == b.local_id()

    def __ne__(self, b):
        return self.local_id() != b.local_id()

    def __cmp__(self, b):
        if self.description == b.description:
            return 0
        elif self.description > b.description:
            return 1
        return -1

    def __json__(self):
        return {
            'id': self.id,
            'org': self.org,
            'url': self.url,
            'username': self.username,
            'description': self.description,
            'local_id': self.local_id()
        }

    def __repr__(self):
        return repr(self.__json__())

bank_config_cache = {}
def bank_config(guid):
    if bank_config_cache.has_key(guid):
        return bank_config_cache[guid]
    path = os.path.join( Settings.fi_cache(), '%s.xml' % guid )
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        logging.info("uncached bank config %s" % guid)
        institution = OFXHome.lookup(guid)
        file = open(path,'w')
        file.write(institution.xml)
        file.close()
    logging.info("parsing file %s" % path)
    bank_config_cache[guid] = OFXHomeInstitution.from_file(path).__dict__
    return bank_config_cache[guid]

# yes this is at the bottom for a reason: circular deps
from account import Account
