import sys, os
import xbmc, xbmcaddon


addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_version = addon.getAddonInfo('version')
addon_path = xbmc.translatePath(addon.getAddonInfo('path'))
profile_path = xbmc.translatePath(addon.getAddonInfo('profile'))
cache_path = os.path.join(profile_path, 'cache')
addon_fullname = '%s v%s' % (addon_id, addon_version)

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
