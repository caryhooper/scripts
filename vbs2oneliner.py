#!/usr/bin/env python3
#Cary Hooper 7/26/20
#Created during AWAE study.
import argparse,os,base64

#Argparse to parse one positional argument
parser = argparse.ArgumentParser()
parser.add_argument("vbsfile",help="/path/to/file.vbs")
parser.add_argument("-b","--base64",action="store_true",help="also output base64 of oneliner")
args = parser.parse_args()

filepath = os.path.abspath(args.vbsfile)
#Grab path from provided vbsfile.  We'll write the new file in the same location with "oneliner" in the filename.
newfilepath = filepath.rsplit(".",1)[0] + ".oneliner." + filepath.rsplit(".",1)[1]; 
print(newfilepath)
f = open(filepath,'r')
new = open(newfilepath,'w')
for line in f.readlines():
	line = line.rstrip().lstrip()
	#print(line)
	try:
		if line[0] == "'":
			#Line starts with ', then it is a comment... remove.
			continue
		if line[-2:] == " _":
			#line ends with a _, then don't add a :
			new.write(line[:-2] + " ")
			
		else:
			#Otherwise, add a ":"
			new.write(line + ":")
	except:
		print()

f.close()
new.close()
if args.base64:
	new = open(newfilepath,'rb')
	contents = new.read()
	b64contents = base64.b64encode(contents).decode()
	print(b64contents)
	print("")

print(f"File successfully written to {newfilepath}")