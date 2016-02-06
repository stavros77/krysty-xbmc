import re, time, datetime
from resources.lib import htmlcleaner

def titlecase(s):
	s = re.sub(r'\d{1,2}x\d{1,2}(-\d{1,2})?', '', s).strip()
	return re.sub(r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(), s)


#getSeconds('02.02.2016 07:23', '%d.%m.%Y %H:%M')
def getSeconds(datetime_string, format):
    return time.mktime(datetime.datetime.strptime(datetime_string, format).timetuple())


def unescape(string, strip=False):
    if string == '':
        return string
    unichars = (
        ('', u'\u200e'),
        ('', u'\u200f'),
        ('-', u'\u2013'),
        ('-', u'\u2014')
    )
    utfchars = (
        ('', '\xe2\x80\x8e'),
        ('', '\xe2\x80\x8f'),
        ('-', '\xe2\x80\x93'),
        ('-', '\xe2\x80\x94')
    )
    html_codes = (
        ("'", '&#39;'),
        ('"', '&quot;'),
        ('>', '&gt;'),
        ('<', '&lt;'),
        ('&', '&amp;'),
        ('-', '&ndash;'),
        ('-', '&mdash;')
    )
    if isinstance(string, unicode):
        for code in unichars:
            string = string.replace(code[1], code[0])
    elif isinstance(string, str):
        for code in utfchars:
            string = string.replace(code[1], code[0])
    hex2dec = lambda x: re.sub(r'&#x([^;]+);', lambda m: '&#%d;' % int(m.group(1), 16), x)
    dec2uni = lambda x: re.sub(r'&#([^x;]+);', lambda m: unichr(int(m.group(1))), x)
    string = hex2dec(string)
    string = dec2uni(string).encode('utf-8')
    for code in html_codes:
        string = string.replace(code[1], code[0])
    if strip:
        string = htmlcleaner.clean(string, True)
    return string
