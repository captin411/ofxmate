import cherrypy, os.path
from ofxclient import Institution, Account, OfxConfig
from ofxhome import OFXHome
from mako.template import Template
from mako.lookup import TemplateLookup
try:
    import json
except ImportError:
    import simplejson as json


current_dir = os.path.abspath( os.path.dirname(__file__) )
html_dir    = "%s/html" % current_dir
if not os.path.exists(html_dir):
    html_dir = '%s/html' % os.path.abspath(os.getcwd())

lookup = TemplateLookup(directories=[html_dir])
def _t(name,**kwargs):
    return lookup.get_template(name).render(**kwargs)

GlobalConfig = OfxConfig()

class REST(object):

    @cherrypy.expose
    def accounts(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        cherrypy.response.status = 200
        return json.dumps([ a.serialize() for a in GlobalConfig.accounts() ])

    @cherrypy.expose
    def add_bank(self,id=None,username=None,password=None):

        cherrypy.response.headers['Content-Type'] = 'application/json'
        cherrypy.response.status = 200

        result = {
            'status': 'ok',
            'message': ''
        }
        if id and username and password:
            bank = OFXHome.lookup(id)
            i = Institution(
                    id = bank['fid'],
                    org = bank['org'],
                    url = bank['url'],
                    broker_id = bank['brokerid'],
                    description = bank['name'],
                    username = username,
                    password = password
            )
            try:
                i.authenticate()
            except Exception as e:
                result['status'] = 'error'
                result['message'] = 'unable to log into bank with those credentials'

            for a in i.accounts():
                GlobalConfig.add_account(a)
            GlobalConfig.save()
        else:
            result['status'] = 'error'
            result['message'] = 'id, username, and password are all required'

        ret = json.dumps(result)
        cherrypy.response.body = ret
        if result['status'] == 'error':
            cherrypy.response.status = 400
        return ret

class Root(object):
    @cherrypy.expose
    def index(self):
        accounts = GlobalConfig.accounts()
        return _t('index.html',accounts=accounts)

    @cherrypy.expose
    def download(self,account_id,filename_arbitrary,days=60):
        account = GlobalConfig.account(account_id)
        cherrypy.response.headers['Content-Type'] = 'application/vnd.intu.QFX'
        cherrypy.lib.caching.expires(secs=0,force=True)
        return account.download(days=int(days)).read()

    @cherrypy.expose
    def search(self,q=None,**kwargs):
        if q:
            found = OFXHome.search(q)
        else:
            found = []
        return _t('search.html',institutions=found,q=q)

    @cherrypy.expose
    def delete_account(self,id=None):
        try:
            GlobalConfig.remove_account(id)
            GlobalConfig.save()
        except:
            pass
        raise cherrypy.HTTPRedirect("/")

    rest = REST()
