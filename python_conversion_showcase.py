#!/usr/bin/python3
import argparse
import socket
import sys
import base64
import re
import binascii

#Argparser to remind us of the days when we didn't have to make our own tools.
parser = argparse.ArgumentParser(description="h00p")
parser.add_argument("ip", help="IP (or hostname) of remote instance")
parser.add_argument("port", type=int, help="port for remote instance")
parser.add_argument("-v","--verbose",help="turn on debugging mode (verbose)", action='store_true')
args = parser.parse_args();

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((args.ip, args.port))

#Log function for debugging mode (verbose)
def log(message):
    if args.verbose:
        print(message)

#b64-----raw
def b642raw(value):
    return base64.b64decode(value)
def raw2b64(value):
    return base64.b64encode(value)

#raw-----hex
def hex2raw(value):
    return binascii.unhexlify(value)
def raw2hex(value):
    return binascii.hexlify(value)

#hex-----dec
def hex2dec(value):
    return str(int(value,base=16)).encode()
def dec2hex(value):
    return ("%X" % int(value.decode())).encode()

#dec-----oct
def dec2oct(value):
    return oct(int(value.decode()))[2:].encode()
def oct2dec(value):
    return str(int(value.decode(),base=8)).encode()

#dec-----bin
def dec2bin(value):
    return bin(int(value.decode())).encode()[2:]
def bin2dec(value):
    return str(int(value.decode(),base=2)).encode()

def bin2dec_alt(self,bitstring):
    #input a string of 1s and 0s, output an int
    return int(bitstring,2)

def dec2bin_alt(self,my_int):
    #input an int and output a string of 1s and 0s
    return "{0:b}".format(my_int)

def do_convert(fromtype,totype,value):
    if fromtype == totype:
        return value

    if fromtype == "b64":
        value = b642raw(value)
        if totype == "raw":
            return value
        value = raw2hex(value)
        if totype == "hex":
            return value
        value = hex2dec(value)
        if totype == "dec":
            return value
        if totype == "oct":
            return dec2oct(value)
        if totype == "bin":
            return dec2bin(value)

    if fromtype == "raw":
        if totype == "b64":
            return raw2b64(value)
        value = raw2hex(value)
        if totype == "hex":
            return value
        value = hex2dec(value)
        if totype == "dec":
            return value
        if totype == "oct":
            return dec2oct(value)
        if totype == "bin":
            return dec2bin(value)

    if fromtype == "hex":
        if totype in ['b64','raw']:
            value = hex2raw(value)
            if totype == 'raw':
                return value
            else:
                return raw2b64(value)
        else:
            value = hex2dec(value)
            if totype == "dec":
                return value
            if totype == "oct":
                return dec2oct(value)
            if totype == "bin":
                return dec2bin(value)

    if fromtype == "dec":
        if totype in ['bin','oct']:
            if totype == 'bin':
                return dec2bin(value)
            if totype == 'oct':
                return dec2oct(value)
        else:
            value = dec2hex(value)
            if totype == 'hex':
                return value
            value = hex2raw(value)
            if totype == 'raw':
                return value
            if totype == 'b64':
                return raw2b64(value)

    if fromtype in ['oct','bin']:
        if fromtype == 'oct':
            value = oct2dec(value)
            if totype == 'bin':
                return dec2bin(value)
        if fromtype == 'bin':
            value = bin2dec(value)
            if totype == 'oct':
                return dec2oct(value)
        if totype == 'dec':
            return value
        value = dec2hex(value)
        if totype == "hex":
            return value
        value = hex2raw(value)
        if totype == 'raw':
            return value
        if totype == 'b64':
            return raw2b64(value)

#Input byte array from raw socket
#Parse input encoding, output encoding, and string and then send to makeAnswer()
#Returns the answer string, converted
def parseResponse(r):
    r = r.decode('UTF-8')
    print(r)
    delim = "------------------------------------------------------------------------------"
    pattern = delim + "(.*?)" + delim
    substring = re.findall(pattern,r, re.DOTALL)
    substring = substring.pop()
    parts = substring.rstrip().lstrip().split("\n")
    fromENCODING = parts[0][0:3]
    toENCODING = parts[0][:-1]
    toENCODING = toENCODING[-3:]
    message = parts[1].encode()
    #Note: all inputs are strings
    log(f"fromENCODING: {fromENCODING} | toENCODING: {toENCODING}")
    return do_convert(fromENCODING,toENCODING,message)

ex_raw = '"h;DoT>s$Ckb3X(zx%JX=x%Q&{x<^|X3-z%y]fD$KjdJUr:KMPK!%H^;gf$0z4Ja'
ex_b64 = 'Omt6WlhLOi5oWT8qdUJpOlViRlJWO0AyQXYkc2VmWG43bG9PQTFFQWBAODJSQlEwKl4xPnhrSjwuc3k7I0Epeg=='
ex_hex = '40377159394a66634a233b5c242c402e362f7b52664d4e7a2f21324f7178232776565a7b765659356b39793021303a54335a52702979382d67634e5b45494443'
ex_dec = '2842806420627373283408607419102167103973857281608354493630028156172262269878935375915440313472683104574053452565891874161321402856924690285074144380217926'
ex_oct = '154204204562107052623423542276370743566051215244152116351373602411512441105272444553565515536471061112621323604516132430572256221011545311621062511162604662144353431066071'
ex_bin = '100100011101010110011000100001001001100011001101001011001100010100001000111001001111100010011101101000001011010101101000110001001110000100010100111111010111000110110000100010011101000010100000110010011110110100110001110010010011110111001101110101010010110110100000100001011101000110000001011111010001100110101101101011010001100010101001011000001110010101001001100101001011110010101001110010010010110111000000111101010111010111010001101011011101110111001101010000010101010111011101011011001000100101001000100111'

# allInputs = [ex_raw,ex_b64,ex_hex,ex_dec,ex_oct,ex_bin]
# convertTypes = ["raw","b64","hex","dec","oct","bin"]

# for i in range(0,6):
#     #print(f"To raw from {convertTypes[i]}: ",end='')
#     result = convertToRaw(convertTypes[i],allInputs[i])
#     #print(f"{result} - {type(result)}")
#     print(f"Originally from {convertTypes[i]}: ",end='')
#     result = convertFromRaw("bin",result)
#     print(f"{result} - {type(result)}")

# sys.exit(1)

#Logic to make the request
for i in range(0,501):    
    r = s.recv(4096)
    answer = parseResponse(r)
    log(f"\n\nFINAL ANSWER - (type {type(answer)}) - \n{answer}\n\n")
    s.send(answer + b"\n")

sys.exit(1)