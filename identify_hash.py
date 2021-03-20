#Given a sha256 hash and some seed info, determine if the hash is predictable.

from hashlib import sha256,sha1
from itertools import permutations, combinations
import sys

this_hash = b"5a3c239d3adaca9860f3ef32e914137bfc4af5fc47f9862fc41e1e6a2e25a557"
this_hash = b"0c8e9f7965efab3367f3cb47d2cdfbff89a408ca"

delims = ["",".",",","|"," "]

seed_info = list()
seed_info.append('cary.hooper')
seed_info.append('cary.hooper@bofa.com')
seed_info.append('1615493476') #signup date
seed_info.append('2440') #user_id
seed_info.append('ipsw9sny') #app_id

def do_sha1(message):
	m = sha1()
	try:
		message = message.encode()
	except:
		pass
	m.update(message)
	this_hash = m.digest()
	return this_hash

def do_sha256(message):
	m = sha256()
	try:
		message = message.encode()
	except:
		pass
	m.update(message)
	this_hash = m.digest()
	return this_hash

def check_hash(check_hash):
	if this_hash == check_hash:
		print("Match!")
		return True
	else:
		return False

def find_permutations(this_list,length):
	perm = permutations(this_list,length)
	return list(perm)

def find_combinations(this_list,length):
	comb = combinations(this_list,length)
	return list(comb)

for num_elements in range(1,len(seed_info) + 1):

	print(f"Checking combinations of {num_elements} elements")
	combs = find_combinations(seed_info,num_elements)

	for comb in combs:
		for num_sub_elements in range(num_elements,len(comb)+1):
			perms = find_permutations(comb,num_sub_elements)
			for perm in perms:
				if len(perm) > 1:	
					for delim in delims:
						seed_string = delim.join(perm)
						#print(seed_string)
						sha1_hash = do_sha1(seed_string)
						if check_hash(sha1_hash):
							print(f"Success! sha1({seed_string}) results in {sha1_hash}")
							sys.exit(0)
				else:
					seed_string = perm[0]
					sha1_hash = do_sha1(seed_string)
					if check_hash(sha1_hash):
						print(f"Success! sha1({seed_string}) results in {sha1_hash}")
						sys.exit(0)

print("Program Complete with no matches.")



