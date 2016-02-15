import time, os, platform, hashlib, random
import urllib, urllib2
import xbmc, xbmcaddon
from cookielib import LWPCookieJar
from resources.lib import phpserialize
import log_utils


EMAIL = ''
AUTH_HASH = ''
DEVICE_UUID = ''
ONERROR_CALLBACK = None


_API_URL = 'https://www.livetvonline.ro/api/'
_API_VERSION = 1

_ADDON = xbmcaddon.Addon()
_PROJECT_NAME = 'Plugin Kodi'
_PROJECT_VERSION = _ADDON.getAddonInfo('version')
_USER_AGENT = 'Kodi %s; %s; Plugin v%s' % (xbmc.getInfoLabel('System.BuildVersion').split(' ')[0], platform.system(), _PROJECT_VERSION)
_LOGIN_COOKIE_FILE = os.path.join(xbmc.translatePath(_ADDON.getAddonInfo('profile')), 'login_cookie')


def onError (message):
    if ONERROR_CALLBACK:
        ONERROR_CALLBACK(message)


def getAuthHash(email, password):
    pwd_md5 = hashlib.md5(password).hexdigest()
    return hashlib.sha256(email+pwd_md5).hexdigest()


def _apiCall(method, params={}):
    params['v'] = _API_VERSION
    params = urllib.unquote_plus(urllib.urlencode(params))
    cj = LWPCookieJar()
    if os.path.isfile(_LOGIN_COOKIE_FILE):
        cj.load(_LOGIN_COOKIE_FILE, ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    req = urllib2.Request(_API_URL + method, params)
    req.add_header('User-Agent', _USER_AGENT)
    conn = urllib2.urlopen(req)
    if conn.code != 200:
        conn.close()
        onError('Eroare de conexiune.')
        return
    response = conn.read()
    conn.close()
    response = phpserialize.loads(response)
    if not response['api_status_general']:
        onError('Server indisponibil.')
        return
    cj.save(_LOGIN_COOKIE_FILE, ignore_discard=True)
    return response


def login(email, auth_hash):
    params = {
        'u': email,
        'p': auth_hash,
        's': DEVICE_UUID,
        'pn': _PROJECT_NAME,
        'pv': _PROJECT_VERSION
    }
    response = _apiCall('login', params)
    if int(response['status']) == 0:
        onError(response['status_message'])
        return False
    return True


def logout():
    _apiCall('logout')
    if os.path.isfile(_LOGIN_COOKIE_FILE):
        os.remove(_LOGIN_COOKIE_FILE)


def getTVChannels():
    tries = 2
    while tries > 0:
        response = _apiCall('app')
        if int(response['status']) > 0:
            registered = int(response['is_registered']) > 0
            channels = []
            for channel in response['channels'].itervalues():
                if not registered and int(channel['payment']) > 0:
                    continue
                channels.append(channel)
            return channels
        login(EMAIL, AUTH_HASH)
        tries -= 1
        time.sleep(0.5)
    onError('Nu s-a putut obtine lista canalelor.')


def getStreamURL(id):
    random_number = lambda: str(random.randint(10**(10-1), 10**10-1))
    params = {'e': id, 'r': random_number()}
    response = _apiCall('stream', params)
    if int(response['status']) == 0:
        onError(response['status_message'])
        return
    return '%s://%s/%s/%s' % (response['stream_type'], response['server'], response['app'], response['stream'])


def getAccountStatus():
    tries = 2
    while tries > 0:
        response = _apiCall('status')
        if int(response['status']) > 0:
            return response['status_message']
        login(EMAIL, AUTH_HASH)
        tries -= 1
        time.sleep(0.5)
    return 'EROARE'
