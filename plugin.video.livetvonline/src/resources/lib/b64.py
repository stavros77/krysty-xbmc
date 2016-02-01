def encode(s, padding = False):
    b64s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    b64p = '='
    ret = ''
    left = 0
    for i in range(0, len(s)):
        if left == 0:
            ret += b64s[ord(s[i]) >> 2]
            left = 2
        else:
            if left == 6:
                ret += b64s[ord(s[i - 1]) & 63]
                ret += b64s[ord(s[i]) >> 2]
                left = 2
            else:
                index1 = ord(s[i - 1]) & (2 ** left - 1)
                index2 = ord(s[i]) >> (left + 2)
                index = (index1 << (6 - left)) | index2
                ret += b64s[index]
                left += 2
    if left != 0:
        ret += b64s[(ord(s[len(s) - 1]) & (2 ** left - 1)) << (6 - left)]
    if(padding):
        for i in range(0, (4 - len(ret) % 4) % 4):
            ret += b64p
    return ret


def decode(data):
    b64s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    b64p = '='
    ret = ''
    data = data.replace(b64p, '')
    left = 0
    for i in range(0, len(data)):
        if left == 0:
            left = 6
        else:
            value1 = b64s.index(data[i - 1]) & (2 ** left - 1)
            value2 = b64s.index(data[i]) >> (left - 2)
            value = (value1 << (8 - left)) | value2
            ret += chr(value)
            left -= 2
    return ret
