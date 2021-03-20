#!/usr/bin/python3

import binascii
import sys

filename = sys.argv[1]

with open(filename, 'rb') as file:
	content = file.read()
print(binascii.hexlify(content))