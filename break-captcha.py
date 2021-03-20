#!/usr/bin/python3
import requests
from PIL import Image
from pytesseract import image_to_string
import sys

for i in range(0,100):
	host = "http://tasks.aeroctf.com:40000"
	captchEndpoint = "/gen.php"
	url = host + captchEndpoint
	proxies = {"http":"http://192.168.0.19:8080","https":"http://192.168.0.19:8080"}
	response = requests.get(url,proxies=proxies)
	imagefile = open("/tmp/test.png",'wb')
	imagefile.write(response.content)
	guess = image_to_string(Image.open('/tmp/test.png'),config="-c tessedit_char_whitelist=0123456789ABCDEF psm=12")
	print(f"Captcha Guess: {guess}")


# data={"captha":guess}
# guessEndpoint = "/reg.php"
# url = host + guessEndpoint
# response = requests.post(url,proxies=proxies,data=data)
# print(response.text)

# Look for Captcha X of 200

