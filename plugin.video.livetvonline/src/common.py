import sys, os
import xbmc, xbmcaddon

addon_id = 'plugin.video.livetvonline'

URLS = {
    'host': 'www.livetvonline.ro',
    'strm_info': 'https://www.livetvonline.ro/analytics2.js?e=%s&r=%s',
    'login': 'https://www.livetvonline.ro/livetv.login'
}

HEADERS = {
    'User-Agent': 	             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Accept': 		             'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control':             'no-transform',
    'Upgrade-Insecure-Requests': '1',
    'Host':                      URLS['host']
}

addon = xbmcaddon.Addon(id=addon_id)
addon_version = addon.getAddonInfo('version')
addon_path = xbmc.translatePath(addon.getAddonInfo('path'))
profile_path = xbmc.translatePath(addon.getAddonInfo('profile'))
cache_path = os.path.join(profile_path, 'cache')
addon_fullname = "%s v%s" % (addon_id, addon_version)

for folder in [profile_path, cache_path]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def getSetting(settingId):
	return addon.getSetting(settingId)

def setSetting(settingId, value):
	addon.setSetting(settingId, value)

def notify(message,duration=3000):
    title = addon_id + ' Notification'
    icon = os.path.join(addon_path, 'resources', 'media', 'inficon.png')
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, message, duration, icon))
