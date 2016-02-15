from random import randint
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlunparse
from hashlib import sha1
try: from sys import getwindowsversion
except: pass
import xbmc, xbmcgui, xbmcaddon
import uuid

PROPERTY_ID = 'UA-46834994-1'

addon = xbmcaddon.Addon()
plugin = '%s v%s' % (addon.getAddonInfo('id'), addon.getAddonInfo('version'))


def getPlatform():
    try:
        os_platforms = {
            'Linux': 'X11; Linux',
            'Windows': 'Windows NT %d.%d',
            'OSX': 'Macintosh; Intel Mac OS X',
            'IOS': 'iPad; CPU OS 6_1 like Mac OS X'
        }
        
        for os, os_version in os_platforms.items():
            if xbmc.getCondVisibility('System.Platform.%s' % (os)):
                if os == 'Windows':
                    version = getwindowsversion()
                    os_version %= (version[0], version[1])
                platform = 'XBMC/Kodi %s (%s) %s' % (xbmc.getInfoLabel('System.BuildVersion').split(' ')[0], os_version, plugin)
                paltform = platform.strip()
        return platform

    except:
        return ('XBMC/Kodi %s' % (plugin)).strip()


class window(xbmcgui.Window):
    def getResolution(self):
        screenx = self.getWidth()
        screeny = self.getHeight()
        return str(screenx) + 'x' + str(screeny)


def track():
    try:        
        id = str(uuid.getnode())        
        visitor = str(int('0x%s' % sha1(id).hexdigest(), 0))[:10]
        
        data = {
            'utmwv': '5.2.2d',
            'utmn': str(randint(1, 9999999999)),
            'utmp': '/',
            'utmac': PROPERTY_ID,
            'utmdt': getPlatform(),
            'utmul': xbmc.getLanguage(),
            'utmsr': window().getResolution(),
            'utmcc': '__utma=%s;' % ('.'.join(['1', visitor, '1', '1', '1', '1']))
        }

        url = urlunparse(('http',
                          'www.google-analytics.com',
                          '/__utm.gif',
                          '',
                          urlencode(data),
                          ''))
        urlopen(url).info()

    except:
        pass