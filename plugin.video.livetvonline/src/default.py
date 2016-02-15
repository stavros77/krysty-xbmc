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

import sys, os, re, time, uuid
import urllib, urlparse
import xbmc, xbmcplugin, xbmcgui
import common, api, utils, tvguide, gui_utils, log_utils
from resources.lib import b64

script_start = time.time()

PARAMS = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

MODE = int(PARAMS.get('mode', 0))
URL = PARAMS.get('url', '')
NAME = PARAMS.get('name', '')
THUMBNAIL = PARAMS.get('thumbnail', '')
CHANNEL_ID = PARAMS.get('channel_id', '')
PARENTAL = int(PARAMS.get('parental', 0))


if MODE == 99:
    api.logout()
    common.setSetting('email', '')
    common.setSetting('auth_hash', '')
    sys.exit()


if MODE in (2, 10) and PARENTAL > 0:
    pwd = xbmcgui.Dialog().input('Reintroduceti parola')
    if not pwd:
        sys.exit()
    email = b64.decode(common.getSetting('email'))
    if api.getAuthHash(email, pwd) != common.getSetting('auth_hash'):
        xbmcgui.Dialog().ok('EROARE', 'Parola incorecta')
        sys.exit()


if MODE == 2:
    progress = xbmcgui.DialogProgress()
    progress.create('Asteptati...', 'Cautare program TV...')

    tvchannel = re.sub(r'\(\d+p\)', r'', NAME).strip()
    
    info = tvguide.getTVGuide(tvchannel)
    
    if not info:
        xbmcgui.Dialog().ok('EROARE', 'Programul TV pentru acest canal nu a fost gasit.')
        sys.exit()
    
    items = []
    
    x = False
    y = 0
    for i in xrange(len(info)):
        item = info[i][0] + ' ' * 5 + info[i][1]
        if info[i][2]:
            item = '[COLOR red]' + item + '[/COLOR]'
            x = True
            y = i
        items.append(item)
    
    if x:
        items = items[y:]
    
    progress.close()
    
    xbmcgui.Dialog().select(tvchannel + ' Program TV', items)
    
    sys.exit()


def onError(message):
    log_utils.log(message)
    xbmcgui.Dialog().ok('EROARE', message)
    sys.exit()

api.ONERROR_CALLBACK = onError

if not common.getSetting('device_uuid'):
    uuid = uuid.uuid1().get_hex()[-12:-2].upper()
    common.setSetting('device_uuid', uuid)

api.DEVICE_UUID = common.getSetting('device_uuid')

if not common.getSetting('email'):
        dialog = gui_utils.LoginDialog()
        dialog.doModal()
        loginData = dialog.get_query()
        del dialog
        
        if not loginData:
            sys.exit()
        
        auth_hash = api.getAuthHash(loginData['email'], loginData['password'])
        
        api.login(loginData['email'], auth_hash)
        
        common.setSetting('email', b64.encode(loginData['email']))
        common.setSetting('auth_hash', auth_hash)

api.EMAIL = b64.decode(common.getSetting('email'))
api.AUTH_HASH = common.getSetting('auth_hash')


def main():
    items = [
        ['Canale TV', 1, 'tvicon.png'],
        ['Stare Cont', 98, 'accountinfoicon.png'],
        ['Logout', 99, 'logouticon.png']
    ]
    
    for item in items:
        thumbnail = os.path.join(common.addon_path, 'resources', 'media', item[2])
        listitem = xbmcgui.ListItem()
        listitem.setLabel(item[0])
        listitem.setIconImage(thumbnail)
        listitem.setThumbnailImage(thumbnail)
        listitem.setProperty('fanart_image', os.path.join(common.addon_path, 'fanart.jpg'))
        listitem.addContextMenuItems([], replaceItems=True)
        
        params = {'name': item[0], 'mode': item[1], 'thumbnail': thumbnail}
        
        u = sys.argv[0] + '?' + urllib.urlencode(params)
        
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=listitem,isFolder=True)
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))    
    xbmc.executebuiltin('Container.SetViewMode(500)')


def TVChannels():
    channels = api.getTVChannels()
    total = len(channels)
    
    for channel in channels:
        addChannel(
            formatTVChannelName(channel['name']), 
            channel['e'],
            channel['img_url'],
            int(channel['parental']),
            total
        )
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    xbmc.executebuiltin('Container.SetViewMode(500)')


def playStream(id, name, thumbnail):
    progress = xbmcgui.DialogProgress()
    progress.create('Asteptati...', 'Cautare stream...')
    
    stream = api.getStreamURL(id)
    
    progress.close()
    
    liz = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
    liz.setInfo(type = 'Video', infoLabels = {'title': name})
    
    xbmc.Player().play(item=stream, listitem=liz)


def formatTVChannelName(name):
    name = utils.titlecase(name)
    name = re.sub(r'(\d+)P', r'\1p', name)
    name = re.sub(r'((?i)TVR|Antena|Sport|Dolcesport|Eurosport)(\d)', r'\1 \2', name)
    nsplit = name.split(' ')
    
    for i in xrange(len(nsplit)):
        if len(nsplit[i]) <= 3:
            nsplit[i] = nsplit[i].upper()
    name = ' '.join(nsplit)
    
    if 'HD' in name:
        x = name.find('HD')
        if name[x-1:x] != ' ':
            name = name.replace('HD', ' HD')
    
    name = name.replace('Animal HD', 'Animal Planet HD')
    name = name.replace('Showcase HD', 'Discovery Showcase HD')
    
    dict = {
        'Discovery':        'Discovery Channel',
        'World':            'Discovery World',
        'Science':          'Discovery Science',
        'Comedy Extra':     'Comedy Central Extra',
        'MTV':              'MTV Romania',
        'Digi Animal':      'Digi Animal World',
        'Investigation':    'Discovery Investigation',
        'History Channel':  'History',
        'Geographic':       'National Geographic',
        'Geographic Wild':  'Nat Geo Wild',
        'Disney':           'Disney Channel',
        'Travel':           'Travel Channel',
        'RTV':              'Romania TV'
    }
    
    if name in dict:
        return dict[name]
    
    return name


def addChannel(name,id,thumbnail,parental=0,totalItems=0):
    listitem = xbmcgui.ListItem()
    listitem.setLabel(name)
    listitem.setIconImage(thumbnail)
    listitem.setThumbnailImage(thumbnail)
    listitem.setProperty('fanart_image', os.path.join(common.addon_path, 'fanart.jpg'))    
    listitem.setInfo(type = 'Video', infoLabels = {'title': name})
    
    contextMenuItems = []
    params = {'name': name, 'mode': 2, 'parental': parental}
    u = sys.argv[0] + '?' + urllib.urlencode(params)
    contextMenuItems.append(('Program TV', 'XBMC.RunPlugin(%s)' % u))
    listitem.addContextMenuItems(contextMenuItems, replaceItems=True)
    
    params = {}
    params['name'] = name
    params['channel_id'] = id
    params['parental'] = parental
    params['mode'] = 10
    params['thumbnail'] = thumbnail
    
    u = sys.argv[0] + '?' + urllib.urlencode(params)
    
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=listitem,isFolder=False,totalItems=totalItems)


if MODE == 0:
    main()

elif MODE == 1:
    TVChannels()

elif MODE == 10:
    playStream(CHANNEL_ID, NAME, THUMBNAIL)

elif MODE == 98:
    xbmcgui.Dialog().ok('Stare Cont', api.getAccountStatus())
    sys.exit()


script_end = time.time() - script_start

log_utils.log('Script took %f seconds to execute.' % (script_end))
