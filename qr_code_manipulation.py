import requests
from bs4 import BeautifulSoup
import base64
from qrtools import QR
from PIL import Image

url = 'http://challenge01.root-me.org/programmation/ch7/'
s = requests.Session()
#Get web page with requests.get
response = s.get(url)

#Use bs4 to find base64 image.  Convert to PNG format.
soup = BeautifulSoup(response.text,'html.parser')
results = soup.find_all('img')
img_b64 = results[0]['src']
img_b64 = img_b64.split(',')[1].encode()
img_raw = base64.b64decode(img_b64)
#Write PNG to file
file = open('qr.png','wb')
file.write(img_raw)
file.close()

#Open with Pillow
img = Image.open('qr.png')
img = img.convert('P')
print(f"Image size {img.size[0]}px x {img.size[1]}px.")

#Draws a 10x10 pixel in the image.
def draw_pixel(y,x,img,scale):
	for y_val in range(y,y+scale):
		for x_val in range(x,x+scale):
			#use 0 for black
			img.putpixel((y_val,x_val),0)
	return img

#Draws a <length> 10x10 pixel line beginning at y,x
def draw_line(y,x,img,length,horizontal,scale):
	if horizontal:
		for x_val in range(x,x + (length *scale),scale):
			img = draw_pixel(y,x_val,img)
	else:
		for y_val in range(y,y + (length * scale),scale):
			img = draw_pixel(y_val,x,img)

	return img

def draw_box(y,x,img,scale):
	#Where y,x is the starting coordinate
	#7-pixel lines
	length = 7
	img = draw_line(y,x,img,length,True)
	img = draw_line(y,x+((length-1)*scale),img,length,False)
	img = draw_line(y+((length-1)*scale),x,img,length,True)
	img = draw_line(y,x,img,length,False)

	length = 3
	img = draw_line(y+(2*scale),x+(2*scale),img,length,True)
	img = draw_line(y+(3*scale),x+(2*scale),img,length,True)
	img = draw_line(y+(4*scale),x+(2*scale),img,length,True)
	# img = draw_line(y+(2*scale),x+(2*scale),img,length,True)
	return img

#Convert to B/W
img = img.convert('1')
scale = 10

#Draw QR timing patterns
img = draw_box(1*scale,1*scale,img)
img = draw_box(scale * 22,1*scale,img)
img = draw_box(1*scale,22*scale,img)

#Save image with new drawings
img.save('qr2.png')

#Decode the QR Code with qrtools
code = QR(filename='qr2.png')
if code.decode():
	print(code.data)
else:
	print("Code not decoded.")
	sys.exit(1)

#for root-me the flag is the 4th part of the string
code = code.data.split(" ")[3]
print(code)

#Send answer and recieve response
data = {'metu': code}
response = s.post(url,data=data)
print(response.text)