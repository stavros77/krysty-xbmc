import re, urllib, urllib2, traceback
from difflib import SequenceMatcher
from resources.lib.parsedom import parseDOM
from resources.lib.bs4 import BeautifulSoup
import common, utils, log_utils


def getChannelGuideUrl(tvchannel):
    url = 'https://www.cinemagia.ro/program-tv/'
    
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', common.HEADERS['User-Agent'])
        conn = urllib2.urlopen(req, timeout=5)
        html = conn.read()
        conn.close()
        
        urls = parseDOM(html, 'a', attrs={'class': 'station-link'}, ret='href')
        names = parseDOM(html, 'a', attrs={'class': 'station-link'})
        
        ratio_list = []
        for name in names:
            str1 = name.lower().replace(' ', '').strip()
            str2 = tvchannel.lower().replace(' ', '').strip()
            ratio = SequenceMatcher(None, str1, str2).ratio()
            ratio_list.append(ratio)
        
        ratio_max_index = max(xrange(len(ratio_list)), key=ratio_list.__getitem__)
        
        return urls[ratio_max_index]
    
    except:
        log_utils.log(traceback.print_exc())
    
    return None


def getTVGuide(tvchannel):
    url = getChannelGuideUrl(tvchannel)
    
    if not url:
        return None
    
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', common.HEADERS['User-Agent'])
        conn = urllib2.urlopen(req, timeout=5)
        html = conn.read()
        conn.close()
        
        soup = BeautifulSoup(html, 'html5lib')
        tds = soup.findAll('td', attrs={'class': 'container_events'})
        tds = [tds[i] for i in xrange(len(tds)) if divmod(i, 4)[1] == 0]
        
        hours = []
        titles = []
        
        for td in tds:
            hours.extend(td.findAll('td', attrs={'class': 'ora'}))
            titles.extend(td.findAll('div', attrs={'class': 'title'}))
        
        if not hours or not titles or len(hours) != len(titles):
            return None
        
        items = []
        
        for i in xrange(len(titles)):
            current = 'current' in str(hours[i])
            hour = re.search(r'<div>(\d+:\d+)<\/div>', str(hours[i])).group(1)
            title = titles[i].getText().strip()
            title = ' '.join(title.split())
            title = utils.unescape(title, True)
            item = (hour, title, current)
            items.append(item)
        
        return items
    
    except:
        log_utils.log(traceback.print_exc())
    
    return None
