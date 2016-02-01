"""
	livetvonline.ro XBMC Addon
	Copyright (C) 2016 krysty
	https://github.com/yokrysty/krysty-xbmc

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, time, traceback
import urllib, urlparse
import xbmc, xbmcplugin, xbmcgui
import common, enc, scraper, gui_utils, log_utils
from resources.lib import ga


script_start = time.time()
log_utils.log(ga.getPlatform())
ga.track()
PARAMS = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

MODE = int(PARAMS.get('mode', 0))
URL = PARAMS.get('url', '')
NAME = PARAMS.get('name', '')
THUMBNAIL = PARAMS.get('thumbnail', '')

log_utils.log('------------------PARAMS------------------')
log_utils.log('--- Mode: ' + str(MODE))
log_utils.log('--- Url: ' + URL)
log_utils.log('--- Name: ' + NAME)
log_utils.log('--- Thumbnail: ' + THUMBNAIL)
log_utils.log('------------------------------------------')

_email = None
_password = None

def getUserCredentials():
    global _email
    global _password
    
    email = common.getSetting('email')
    password = common.getSetting('password')
    if email and password:
        _email = enc.decrypt(email)
        _password = enc.decrypt(password)

getUserCredentials()

if not _email:
        dialog = gui_utils.loginDialog()
        dialog.doModal()
        loginData = dialog.get_query()
        del dialog
        
        if not loginData:
            sys.exit()
        
        if not scraper.doLogin(loginData['email'], loginData['password']):
            xbmcgui.Dialog().ok('LOGIN', 'Email-ul sau parola sunt incorecte.')
            sys.exit()
        
        _email = loginData['email']
        _password = loginData['password']
        
        q = 'Sunteti de acord ca datele de logare sa fie salvate pe dispozitiv?'
        qd = xbmcgui.Dialog().yesno('LOGIN', q, '', '', 'NU', 'DA')
        if qd:
            common.setSetting('email', enc.encrypt(loginData['email']))
            common.setSetting('password', enc.encrypt(loginData['password']))

getUserCredentials()
scraper.setUserCredentials(_email, _password)


def main():
    addDir('Stare Cont', '', 98, os.path.join(common.addon_path, 'resources', 'media', 'accountinfoicon.png'))
    addDir('Logout', '', 99, os.path.join(common.addon_path, 'resources', 'media', 'logouticon.png'))
    
    progress = xbmcgui.DialogProgress()
    progress.create('Asteptati...', 'Se descarca lista canalelor...')
    
    channels = scraper.getTVChannelsList()
    
    if not channels:
        xbmcgui.Dialog().ok('EROARE', 'Nu s-a putut obtine lista canalelor.')
    
    total = len(channels)
    
    for channel in channels:
        addDir(channel['name'], channel['id'], 10, channel['img'], False, total)
    
    progress.close()
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
    xbmc.executebuiltin('Container.SetViewMode(500)')


def playStream(id, name, thumbnail=''):
    progress = xbmcgui.DialogProgress()
    progress.create('Asteptati...', 'Cautare stream...')
    
    stream = scraper.getStreamUrl(id)
    
    progress.close()
    
    if not stream:
        xbmcgui.Dialog().ok('EROARE', 'Stream-ul nu a fost gasit.')
        sys.exit()
    
    liz = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
    liz.setInfo(type = 'Video', infoLabels = {'title': name})
    
    xbmc.Player().play(item=stream, listitem=liz)


def addDir(name,url,mode,thumbnail='',folder=True,totalItems=0):
    listitem = xbmcgui.ListItem()   
    listitem.setLabel(name)
    listitem.setIconImage(thumbnail)
    listitem.setThumbnailImage(thumbnail)
    listitem.setInfo(type = 'Video', infoLabels = {'title': name})
    listitem.addContextMenuItems([], replaceItems=True)
    listitem.setProperty('fanart_image', os.path.join(common.addon_path, 'fanart.jpg'))
    
    params = {}
    params['name'] = name
    params['url'] = url
    params['mode'] = mode
    params['thumbnail'] = thumbnail

    empty_keys = [k for k in params if not params[k]]
    for key in empty_keys:
        del params[key]
    
    u = sys.argv[0] + '?' + urllib.urlencode(params)
    
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=listitem,isFolder=folder,totalItems=totalItems)


if MODE == 0:
    main()

elif MODE == 10:
    playStream(URL, NAME, THUMBNAIL)

elif MODE == 98:
    info = scraper.getAccountInfo()
    if info:
        xbmcgui.Dialog().ok(common.URLS['host'], info)
    else:
        xbmcgui.Dialog().ok(common.URLS['host'], 'EROARE')
    sys.exit()

elif MODE == 99:
    try:
        common.setSetting('email', '')
        common.setSetting('password', '')
        if os.path.isfile(scraper.LOGIN_COOKIE_FILE):
            os.remove(scraper.LOGIN_COOKIE_FILE)
    except:
        log_utils.log(traceback.print_exc())
    xbmc.executebuiltin('XBMC.Action(Back)')
    sys.exit()


script_end = time.time() - script_start

log_utils.log('Script took %f seconds to execute.' % (script_end))
