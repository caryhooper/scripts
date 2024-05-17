import sys,zlib,re,warnings
warnings.filterwarnings("ignore")

#python .\dc.py /path/to/file.pdf
path = sys.argv[1]
file = open(path,'rb')
pdf = file.read()
stream = re.compile(rb'.*?FlateDecode.*?stream(.*?)endstream', re.S)
objects = stream.findall(pdf)
#Most times, the object was stored as the last object.
count = 0 
while len(objects) > 0:
	last = objects.pop()
	mydata = zlib.decompress(last.strip(b'\r\n'))
	print(str(mydata, errors='replace'))

	sys.exit(0)  #Remove this if the object isn't the last one.