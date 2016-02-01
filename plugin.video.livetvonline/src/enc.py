#import uuid, hashlib
#from resources.lib import pyaes
from resources.lib import b64

# temporary disable the aes key encryption
# and use only base 64 encode
# because on Android UUID is not unique
 
#_pwd = str(uuid.uuid1()).split('-')[-1]
#_key = hashlib.md5(_pwd).digest()

def encrypt(plaintext):
    #return b64.encode(pyaes.AESModeOfOperationCTR(_key).encrypt(plaintext))
    return b64.encode(plaintext)

def decrypt(encryptedtext):
    #return pyaes.AESModeOfOperationCTR(_key).decrypt(b64.decode(encryptedtext))
    return b64.decode(encryptedtext)