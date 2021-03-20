#!/usr/bin/python3
#bin2perl created to assist with OSCE payload standardization.
#Cary Hooper 17NOV18
#For use with:
#msfvenom -p windows/exec CMD=calc -f raw > /path/to/file.bin

import binascii
import sys

if len(sys.argv) != 2:
	print("[!] Error: requires one argument")
	print("Usage: ./bin2perl /path/to/file.bin")
	sys.exit()

filename = sys.argv[1]
with open(filename, 'rb') as file:
	content = file.read()
hexfile = binascii.hexlify(content)

init = 0
print("\n[*] PERL")
for i in range(len(hexfile)):
	if i % 32 == 0:
		if init == 0:
			print("$buf  = \"",end="")
			init = 1
		else:
			print("\";\n$buf .= \"",end="")
	if i % 2 == 0:
		print("\\x%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
print("\";\n")

print("[*] HEX")
for i in range(len(hexfile)):	
	if i % 2 == 0:
		print("%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
print("\n")