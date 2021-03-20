#!/usr/bin/python3
#bin2powershell created to assist with binary payload standardization.
#Cary Hooper 15FEB21
#For use with:
#msfvenom -p windows/exec CMD=calc -f raw > /path/to/file.bin

import binascii
import sys

if len(sys.argv) != 2:
	print("[!] Error: requires one argument")
	print("Usage: ./bin_to_powershell.py /path/to/file.bin")
	sys.exit()

filename = sys.argv[1]
with open(filename, 'rb') as file:
	content = file.read()
hexfile = binascii.hexlify(content)

init = 0
print("\n[*] POWERSHELL\n")
print('[Byte[]] $Shellcode = \t@(',end='')
rangeList = range(len(hexfile))
for i in rangeList:
	if i % 32 == 0:
		if i != 0:
			print("\n\t\t\t",end='')
		# if init == 0:
		# 	print("$buf  = \"",end="")
		# 	init = 1
		# else:
		# 	print("\"\n$buf += \"",end="")
	if i % 2 == 0:
		if i == rangeList[-2]:
			print("0x%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
		else:
			print("0x%s%s," % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
print(")\n")

#print("[*] HEX")
#for i in range(len(hexfile)):	
#	if i % 2 == 0:
#		print("%s%s" % (chr(hexfile[i]),chr(hexfile[i+1])),end="")
#print("\n")
