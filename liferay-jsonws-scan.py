#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import warnings
import time
import sys
from requests.auth import HTTPBasicAuth
warnings.filterwarnings("ignore")


def do_get(params):
	baseurl = "https://example.myliferayhost.com/api/jsonws"
	proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}
	#proxies = {}
	try:
		response = requests.get(baseurl, verify=False, proxies=proxies, params=params,timeout=20,auth=HTTPBasicAuth('user','password'))
		html = BeautifulSoup(response.text, "html.parser")
		if html.title == "Burp Suite Professional":
			return do_get(params)
		else:
			return response.text
	except Exception as e:
		print(f"Error: {e}")
		time.sleep(1)
		return do_get(params)

content = do_get({})
#print(content)
soup = BeautifulSoup(content, "html.parser")
#Find all a with class of "lfr-panel-title"
results = soup.find_all('a',{'class':'lfr-api-service-result'})
for method in results:
	#<a class="method-name lfr-api-service-result" data-metaData="UserGroupRole" href="?signature=/usergrouprole/add-user-group-roles-3-userId-groupId-roleIds">add-user-group-roles</a>
	#print(method.find_all('span')[0].text)
	href = method['href']
	href = href[1:]
	parameters = href.split('=')
	params = {parameters[0]:parameters[1]}
	print(params)

	methodcontent = do_get(params)
	methodsoup = BeautifulSoup(methodcontent,"html.parser")
	methodresults = methodsoup.find_all('div',{'class':'lfr-api-parameters'})

	for apiParamGroup in methodresults:
	#<div class="lfr-api-parameters lfr-api-section">
		if apiParamGroup.find('h3').text == "Parameters":
			#if the div contains: <h3>Parameters</h3>
			# print(apiParamGroup)
			# print(type(apiParamGroup))
			#print(f"apiParamGroup: {apiParamGroup} of type {type(apiParamGroup)}")
			apiParamSpans = apiParamGroup.find_all('span')
			#print(f"apiParamSpans: {apiParamSpans} of type {type(apiParamSpans)}")

			newline = 0
			for span in apiParamSpans:
				#print(span)
				if newline == 0:
					print(f"{span.text} - ", end='')
					newline = 1
				else:
					print(f"{span.text}")
					newline = 0

