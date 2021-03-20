import requests
from bs4 import BeautifulSoup
import sys
from PIL import Image
from pytesseract import image_to_string
import base64, string
import subprocess

url = "http://challenge01.root-me.org/programmation/ch8/"
headers = {'User-Agent' : 'Anonymous Browser, probably'}
s = requests.Session()

def try_captcha():
	response = s.get(url, headers=headers)
	#print("Got HTML document.")
	soup = BeautifulSoup(response.text, "html.parser")
	results = soup.find_all('img')
	#print(f"Found {len(results)} <img>.")

	if len(results) == 0:
		print("Error.  No images found.")
		sys.exit(1)


	img = results[0]
	image = img['src']
	b64_image = image.split(",")[1].encode()
	raw_image = base64.b64decode(b64_image)
	image_file = open("test.png",'wb')
	image_file.write(raw_image)
	image_file.close()
	#print("Saved image file.")

	charset = string.printable
	guess = image_to_string(Image.open('test.png'),config=f"-c tessedit_char_whitelist=23456789ABCDEFGHIJKLMNPQRSTUVWYZabcdefghijkmnopqrstuvwyz psm=12")
	#result = subprocess.Popen(['gocr -i test.png -C 23456789ABCDEFGHIJKLMNPQRSTUVWYZabcdefghijkmnopqrstuvwyz'], shell=True, stdout=subprocess.PIPE).communicate()[0]
	#guess = guess.decode().strip()

	print(f"Guess: {guess}")
	data = {'cametu': guess,
			'Submit': 'Try'}
	response = s.post(url,data=data, headers=headers)
	return response.text


exit = False

for i in range(0,100):
	doc = try_captcha()
	if "retente ta chance" not in doc :
		print("SUCCESS!")
		exit = True
	soup = BeautifulSoup(doc, "html.parser")
	results = soup.find_all('p')
	for i in results:
		print(i.text)
	if exit:
		sys.exit()
		

#NcBbqdnZiMBk
		