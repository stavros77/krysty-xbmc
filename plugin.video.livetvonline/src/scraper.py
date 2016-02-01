import os, time, re, random, traceback
import urllib, urllib2
import common, log_utils
from cookielib import LWPCookieJar
from resources.lib import mechanize
from resources.lib.parsedom import parseDOM
from resources.lib import b64
from resources.lib import phpserialize


LOGIN_COOKIE_FILE = os.path.join(common.profile_path, 'login_cookie')


__email = None
__password = None

def setUserCredentials(email, password):
    global __email
    global __password
    
    __email = email
    __password = password


class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


def http_req(url, data=None, headers={}, cookie=None):
    if cookie:
        cj = LWPCookieJar()
        
        if os.path.isfile(cookie):
            cj.load(cookie, ignore_discard=True)
        
        opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    
    if data is not None:
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    
    for k, v in common.HEADERS.items():
        req.add_header(k, v)
    
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    
    conn = urllib2.urlopen(req)
    
    if cookie:
        cj.save(cookie, ignore_discard=True)
    
    return conn


def doLogin(email, password):
    global LOGIN_COOKIE_FILE
    
    try:
        if os.path.isfile(LOGIN_COOKIE_FILE):
            os.remove(LOGIN_COOKIE_FILE)
        
        data = {
            'email': email,
            'password': password,
            'remember': '1',
            'Submit': 'Login',
            'action': 'process'
        }
        
        conn = http_req(common.URLS['login'], data, common.HEADERS, LOGIN_COOKIE_FILE)
        ret_code = conn.code
        conn.close()

        if ret_code == 302:
            return True

    except:
        log_utils.log(traceback.print_exc())

    return False


def _getHtml():
    global LOGIN_COOKIE_FILE
    global __email
    global __password
    
    html = ''
    
    tries = 2
    while (tries > 0):
        try:
            cj = mechanize.LWPCookieJar()
            cj.load(LOGIN_COOKIE_FILE)
            opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cj))
            req = mechanize.Request(common.URLS['login'])
            for k, v in common.HEADERS.items():
                req.add_header(k, v)
            conn = opener.open(req)
            cj.save(LOGIN_COOKIE_FILE)
            html = conn.read()
            conn.close()
        except:
            log_utils.log(traceback.print_exc())
        
        if html and __email in html:
            break
        else:
            doLogin(__email, __password)
        
        tries -= 1
        
        time.sleep(1)
    
    return html


def getTVChannelsList():
    lst = []
    
    try:
        html = _getHtml()
        
        ul = parseDOM(html, 'ul', attrs={'class': 'sc_menu'})[0]
        
        results = re.findall(r'playFlowRtmpE\(\'(.+?)\'\).+?<img src="(.+?)".+?<a href.+?>(.+?)<\/a>', ul)
        
        for id, img, name in results:
            tv = {}
            tv['id'] = id.strip().encode('utf-8')
            tv['img'] = img.strip().encode('utf-8')
            tv['name'] = name.strip().encode('utf-8')
            lst.append(tv)
    
    except:
        log_utils.log(traceback.print_exc())
    
    return lst


def getStreamUrl(stream_id):
    try:
        u = common.URLS['strm_info'] % (stream_id, str(random.random()))
        conn = http_req(u, headers=common.HEADERS)
        p = conn.read()
        conn.close()
        
        if p == '1':
            conn = http_req(u, {}, headers=common.HEADERS)
            data = conn.read()
            conn.close()
            
            data = b64.decode(data)
            data = phpserialize.loads(data)
            
            rtmp = '%s://%s/%s/%s' % (data['stream_type'], data['server'], data['app'], data['stream'])
            
            return rtmp
    except:
        log_utils.log(traceback.print_exc())
    
    return None


def getAccountInfo():
    try:
        html = _getHtml()
        
        div = parseDOM(html, 'div', attrs={'id': 'messageDiv'})[0]
        
        if 'expirat' in div:
            return 'Abonamentul a expirat'
        
        m = re.search(r'Abonamentul este.+?inclusiv\)', div, re.DOTALL)
        
        if m:
            return m.group(0).encode('utf-8')
        
    except:
        log_utils.log(traceback.print_exc())
    
    return None
