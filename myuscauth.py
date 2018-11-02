import requests
import lxml
from lxml import html


# Returns session
def usc_auth(username, password):

    s = requests.Session()
    r = s.get('https://my.usc.edu/')

    enter_page = lxml.html.fromstring(r.content)
    form_1 = enter_page.xpath("//form[@name='form1']")
    #print form_1[0].attrib['action']

    Query = "https://shibboleth.usc.edu" + form_1[0].attrib['action']
    #print Query
    payload = {'_eventId_proceed' : '', 'shib_idp_ls_exception.shib_idp_persistent_ss' : '',
     'shib_idp_ls_exception.shib_idp_session_ss' : '',
     'shib_idp_ls_success.shib_idp_persistent_ss' : 'false',
     'shib_idp_ls_success.shib_idp_session_ss' : 'false',
     'shib_idp_ls_supported' : '',
     'shib_idp_ls_value.shib_idp_persistent_ss' : '',
     'shib_idp_ls_value.shib_idp_session_ss': ''
     }

    bypass = s.post(Query, data=payload)
    #print bypass.content
    #print bypass.url

    payload = {
        '_eventId_proceed': '',
        'j_password': password,
        'j_username': username
    }

    login = s.post(bypass.url, data=payload)
    #print login.content
    #print login.url

    tree = lxml.html.fromstring(login.content)

    SAMLResponses = tree.xpath("//form//input[@name='SAMLResponse']")
    #print SAMLResponses[0]
    SAMLResponse = SAMLResponses[0].attrib['value']
    #print SAMLResponse

    payload = {'SAMLRequest':SAMLResponse}
    login = s.post('https://my.usc.edu/portal/Shibboleth.sso/SAML2/POST', payload)

    #print login.content
    #print login.url

    print "Are We Logged In? : " + str(username in login.text)

    return s

