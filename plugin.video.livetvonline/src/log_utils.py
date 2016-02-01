import xbmc
import xbmcaddon

addon = xbmcaddon.Addon()
name = addon.getAddonInfo('id')
version = addon.getAddonInfo('version')

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING

def log(msg, level=xbmc.LOGNOTICE):
    if (addon.getSetting('addon_debug') == 'true') and (level == xbmc.LOGDEBUG):
        level = xbmc.LOGNOTICE

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('%s v%s: %s' % (name, version, msg), level)
    
    except Exception as e:
        try:
            xbmc.log('Logging Failure: %s' % (e), level)
        except:
            pass
