#!/usr/bin/python3
from Crypto.Cipher import AES
import base64

key = "8d127684cbc37c17616d806cf50473cc"
ccb64 = "5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc="
#iv = "\x00" * 16 

print(AES.new(bytes.fromhex(key), AES.MODE_ECB).decrypt(base64.b64decode(ccb64)))

key = "8d127684cbc37c17616d806cf50473cc"
ccb64 = "5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc="
iv = "\x00" * 16 

print(AES.new(bytes.fromhex(key), AES.MODE_CBC, iv).decrypt(base64.b64decode(ccb64)))