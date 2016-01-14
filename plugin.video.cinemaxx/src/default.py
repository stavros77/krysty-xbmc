"""
	cinemaxx.ro Addon for KODI (formerly knows as XBMC)
	Copyright (C) 2012-2016 krysty
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

import sys, os, re
import urllib, urllib2, urlparse
import xbmcplugin, xbmcgui
from bs4 import BeautifulSoup
import json
import plugin, db
from resources.lib.ga import track

URL = {}
URL['base']			= 'http://www.cinemaxx.rs/'
URL['search']		= 'http://www.cinemaxx.rs/search.php?keywords='
URL['newMovies']	= 'http://www.cinemaxx.rs/newvideos.html'

HEADERS = {
	'User-Agent': 	 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
	'Accept': 		 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Cache-Control': 'no-transform'
}

ICON = {
	'movie':	'moviesicon.png',
	'search':	'searchicon.png',
	'settings': 'settingsicon.png'
}

PLUGIN_PATH = plugin.getPluginPath()

for k, v in ICON.iteritems():
	ICON[k] = os.path.join(PLUGIN_PATH, 'resources', 'media', v)

print plugin.getPluginVersion()

DB = db.DB()

track(plugin.getPluginVersion())


def MAIN():
	addDir('Categorii', URL['base'], 1, ICON['movie'])
	addDir('Adaugate Recent', URL['newMovies'], 11, ICON['movie'])
	addDir('Cautare', URL['base'], 2, ICON['search'])
	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def categories(url):
	html = BeautifulSoup(http_req(url)).find('ul', {'id': 'ul_categories'}).findAll('a')
	
	total = len(html)
	
	for tag in html:
		addDir(tag.get_text(), tag.get('href'), 10, '', True, total)
	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def getMovies(url, limit=None):
    soup = BeautifulSoup(http_req(url))

    pages = soup.find('ul', {'class': 'pagination'})
    if pages and not limit:
        pages = pages.findAll('a')
        pages = max(int(x) for x in re.findall('(\d+)', str(pages)))
        page = int(re.search('\d+', url).group(0))
    else:
        pages = 1
        page = 1

    tags = soup.find('ul', {'class': 'videolist'}).findAll('a', limit=limit)

    total = len(tags)

    for tag in tags:
        img = tag.select('img')[0]
        name = nameFilter(img.get('alt').encode('utf-8'))
        link = tag.get('href')
        thumbnail = img.get('src')
        
        addDir(name, link, 3, thumbnail, totalItems=total)

    if not page == pages:
        url = re.sub('\d+', str(page + 1), url)
        addDir("Pagina Urmatoare >>", url, 10)

    xbmcplugin.endOfDirectory(int(sys.argv[1]))

	
def search():
    kb = xbmc.Keyboard('', 'Search', False)

    lastSearch = None
    try:
        lastSearch = plugin.loadData('search')
        if lastSearch:
            kb.setDefault(lastSearch)
    except:
        pass

    kb.doModal()

    if (kb.isConfirmed()):
        inputText = kb.getText()
        
        try:
            plugin.saveData('search', inputText)
        except:
            pass
        
        if inputText == '':
            dialog = xbmcgui.Dialog().ok('Cautare', 'Nimic de cautat.')
            sys.exit()
        
        url = URL['search'] + urllib.quote_plus(inputText)
        tags = BeautifulSoup(http_req(url)).find('ul', {'class': 'videolist'}).findAll('a', limit=10)
        
        total = len(tags)
        
        for tag in tags:
            img = tag.select('img')[0]
            name = nameFilter(img.get('alt').encode('utf-8'))
            link = tag.get('href')
            thumbnail = img.get('src')
            
            addDir(name, link, 3, thumbnail, totalItems=total)
    else:
        sys.exit()

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def http_req(url, getCookie=False, data=None, customHeader=None):
	if data: data = urllib.urlencode(data)
	req = urllib2.Request(url, data, HEADERS)
	if customHeader:
		req = urllib2.Request(url, data, customHeader)
	response = urllib2.urlopen(req)
	source = response.read()
	response.close()
	if getCookie:
		cookie = response.headers.get('Set-Cookie')
		return {'source': source, 'cookie': cookie}
	return source


def playStream(url,title,thumbnail):
	win = xbmcgui.Window(10000)
	win.setProperty('cinemaxx.playing.title', title.lower())
	
	item = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
	item.setInfo(type = "Video", infoLabels = {"title": title})
	
	xbmc.Player().play(item=url, listitem=item)
	
	return True


def selectSource(url, title='', thumbnail=''):
    progress = xbmcgui.DialogProgress()
    progress.create('Incarcare', 'Asteptati...')
    progress.update(1, "", "Cautare surse video...", "")

    sources = getSources(url)

    progress.close()

    if not sources:
        xbmcgui.Dialog().ok("", "Sursele video nu au fost gasite.")
        sys.exit()

    labels = []

    for item in sources:
        labels.append(item['name'])

    dialog = xbmcgui.Dialog()

    index = dialog.select('Selectati sursa video', labels)
    if index > -1:
        playStream(sources[index]['url'], title, thumbnail)
    else:
        sys.exit()


def getSources(url):
    sources = []

    soup = BeautifulSoup(http_req(url))



    params = {}

    try:
        params['vid'] = re.search(r'_([0-9a-z]+).html?', url).group(1)
    except:
        html = soup.findAll('script', {'type': 'text/javascript'})
        html = "".join(line.strip() for line in str(html).split("\n"))
        html = re.findall(r'\$\.ajax\({.+?data: {(.+?)}', html)
        html = html[1].replace('"', '').split(',')

        for parameter in html:
            key, value = parameter.split(':')
            params[key] = value.strip()

    mirrors = []

    if(soup.find('iframe')):
        mirrors.append(url)
    else:
        mirrors.append('%sajax.php?p=video&do=getplayer&vid=%s' % (URL['base'], params['vid']))

    multiMirrors = soup.find('ul', {'id': 'menu-bar'})
    if multiMirrors:
        multiMirrors = multiMirrors.findAll('a')

    if(multiMirrors):
        for i in range(len(multiMirrors)):
            mirrors.append('%sajax.php?p=custom&do=requestmirror&vid=%s&mirror=%s' % (URL['base'], params['vid'], str(i+1)))

    mirrors.reverse()

    for mirror in mirrors:
        try:
            if mirror == url:
                mirrorUrl = soup.find('iframe').attrs['src']
            else:
                mirrorUrl = BeautifulSoup(http_req(mirror)).find('iframe').attrs['src']
            mirrorUrl = re.sub(r'https?:\/\/(?:www\.)?.+?\.li/?\??', '', mirrorUrl)
        except:
            continue
        
        if(re.search(r'mail.ru', mirrorUrl)):
            try:
                source = BeautifulSoup(http_req(mirrorUrl)).findAll('script', {'type': 'text/javascript'})
                jsonUrl = re.search(r'"metadataUrl":"(.+?)"', str(source)).group(1)
                req = http_req(jsonUrl, True)
                jsonSource = json.loads(req['source'])
                
                for source in jsonSource['videos']:
                    name = '%s %s' % ('[mail.ru]', source['key'])
                    link = '%s|Cookie=%s' % (source['url'], urllib.quote_plus(req['cookie']))
                    item = {'name': name, 'url': link}
                    sources.append(item)
            except:
                pass
        
        elif(re.search(r'vk.com', mirrorUrl)):
            try:
                from resources.lib.getvk import getVkVideos
                for source in getVkVideos(http_req(mirrorUrl)):
                    item = {'name': source[0], 'url': source[1]}
                    sources.append(item)
            except:
                pass
        
        elif(re.search(r'ok.ru', mirrorUrl)):
            try:
                id = re.search('\d+', mirrorUrl).group(0)
                u = urlparse.urlparse(mirrorUrl)
                hostUrl = '://'.join([u.scheme, u.netloc])
                jsonUrl = 'http://ok.ru/dk?cmd=videoPlayerMetadata&mid=' + id
                jsonSource = json.loads(http_req(jsonUrl))
                
                for source in jsonSource['videos']:
                    quality = {
                        'mobile':   '144p',
                        'lowest':   '240p',
                        'low':      '360p',
                        'sd':       '480p',
                        'hd':       '720p',
                        'full':     '1080p'
                    }
                    q = source['name'].strip()
                    q = quality.get(q, None)
                    if not q:
                        continue
                    name = '%s %s' % ('[ok.ru]', q)
                    params = {
                        'User-Agent':   HEADERS['User-Agent'],
                        'Referer':      mirrorUrl,
                        'Origin':       hostUrl
                    }
                    params = '&'.join(['%s=%s' % (k, urllib.quote_plus(v)) for k, v in params.iteritems()])
                    link = '%s|%s' % (source['url'], params)
                    
                    item = {'name': name, 'url': link}
                    sources.append(item)
            except:
                pass
    return sources


def nameFilter(name):
	return re.sub('F?f?ilme? ?-?|vizioneaza|online|subtitrat', '', name).strip()


def addDir(name, url, mode, thumbnail='', folder=True, totalItems=0):
    params = {'name': name, 'mode': mode, 'url': url, 'thumbnail': thumbnail}

    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnail)

    if not folder:
        liz.setProperty('isPlayable', 'true')
        liz.setProperty('resumetime', str(0))
        liz.setProperty('totaltime', str(1))
        
    liz.setInfo(type="Video", infoLabels = {"title": name})

    empty_keys = [k for k in params if not params[k]]
    for key in empty_keys:
        del params[key]

    u = sys.argv[0] + '?' + urllib.urlencode(params)

    return xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = liz, isFolder = folder, totalItems=totalItems)


params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

mode = int(params.get('mode', 0))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumbnail = urllib.unquote_plus(params.get('thumbnail', ''))


if mode: print 'Mode: ' + str(mode)
if url: print 'URL: ' + str(url)


if mode == 0 or not url or len(url) < 1: MAIN()
elif mode == 1: categories(url)
elif mode == 2: search()
elif mode == 3: selectSource(url, name, thumbnail)
elif mode == 10: getMovies(url)
elif mode == 11: getMovies(url, 25)
