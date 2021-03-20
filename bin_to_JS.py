#!/usr/bin/python3
#bin2JS created to assist with AWAE payload standardization.
#Cary Hooper 16JUL2020

import binascii
import sys

if len(sys.argv) != 2:
	print("[!] Error: requires one argument")
	print("Usage: ./bin2py /path/to/file.bin")
	sys.exit()

filename = sys.argv[1]
with open(filename, 'rb') as file:
	content = file.read()
	print(f"Length: {len(content)}")
hexfile = binascii.hexlify(content)

init = 0
print("\n[*] JavaScript")
for i in range(len(hexfile)):
	if i % 32 == 0:
		if init == 0:
			print("var buf  = \"",end="")
			init = 1
		else:
			print("\";\nbuf += \"",end="")
	if i % 2 == 0:
		print("\\x%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
print("\";\n")

print("[*] HEX")
for i in range(len(hexfile)):	
	if i % 2 == 0:
		print("%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
print("\n")
