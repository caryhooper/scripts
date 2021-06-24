#!/bin/bash

#Inputs argument as hostname or IP
#Automating routine enumeration tasks.
echo Initial Host Enumeration Script
echo by Cary Hooper @nopantrootdance
#TODO
#can we extract hostname from nmap scan? 
#support for openSSL certificate parsing
#smtp checks - is login allowed? can we VRFY users?
#UDP nmap scan... at least top 5 UDP services
#tftp checks - any files available to download?  can we write files?
#snmp checks - 1) brute top 5-10 community strings... if found, do snmpwalk.
#dns checks (TCP and UDP) - zone transfer, name lookups to find hostname.

if [ $# != 1 ]
then
	echo "usage: ./enum.sh <IP or hostname>"
	exit
fi
target=$1
#Make output directory if it doesn't exist.
if [ ! -d nmap ]
then
	mkdir nmap > /dev/null 2>&1
fi
#Do the nmap scan
echo -e "\t[*] Beginning nmap scan of target."
nmap -p- -oA nmap/$target -Pn -T5 -sV -v0 $target --host-timeout 99999m > /dev/null 2>&1

#----------------------------------------------------------------------
#Check for http(s)
httpPorts=()
count=$(cat nmap/$target.nmap | egrep " http | ssl/http | https " | grep -v "incorrect results at " | egrep -v "593|598[56]|470{2}[0-9]|491{2}[0-9]" | wc -l)
if [ $count -ne 0 ]
then
	httpflag=1
	echo "[!] Detected HTTP/HTTPS"
	query=$(cat nmap/$target.nmap | egrep " http | ssl/http | https " | grep -v "incorrect results at ")
	while read -r line; do
		port=$(echo -n "$line" | cut -d '/' -f1)
		echo "[!] Port $port is a web service"
		httpPorts+=("$port")

	done <<< $(echo "$query")
else
	httpflag=0
	echo httpflag is $httpflag
fi

#Do http enumeration things.
#using ( ) subshell notation to suppress output
for port in ${httpPorts[@]}; do 
	#Nikto
	echo -e "\t[*] Starting nikto against port $port"
	( nikto -h http://$target:$port -o nikto.$target.$port.txt > /dev/null 2>&1 & )
	#Dirbuster
	echo -e "\t[*] Starting dirb against port $port"
	( dirb http://$target:$port -o dirb.$target.$port.txt > /dev/null 2>&1 & )
done
#----------------------------------------------------------------------
#Check for ftp
ftpPorts=()
count=$(cat nmap/$target.nmap | egrep " ftp " | wc -l)
if [ $count -ne 0 ]
then
	ftpflag=1
	echo "[!] Detected FTP"
	query=$(cat nmap/$target.nmap | egrep " ftp " )
	while read -r line; do
		port=$(echo -n "$line" | cut -d '/' -f1)
		echo "[!] Port $port is hosting an ftp service"
		ftpPorts+=("$port")

	done <<< "$query"
else
	ftpflag=0
	#echo ftpflag is $ftpflag
fi
#Do ftp enumeration things
#Test for anonymous logon and anonymous write
echo h00p > ftptest.txt
for port in ${ftpPorts[@]}; do
	#Anonymous ftp login
	if [[ $(echo -e "USER anonymous\r\nPASS anonymous\r\n" | nc -nv $target $port | grep "230") =~ ^230.*$ ]]
	then 
		echo "[*] Anonymous login allowed on port $port"
	fi
	if [[ $(echo -e "USER anonymous\r\nPASS anonymous\r\nSTOR ftptest.txt\r\n\cc" | nc -nv $target $port | grep "150") =~ ^150.*$ ]]
	then 
		echo "[*] Anonymous write allowed on port $port"
	fi
	echo -e "USER anonymous\r\nPASS anonymous\r\nSTOR ftptest.txt\r\n\cc" | nc -nv $target $port | grep "150"
	ps -aef | grep "nc -nv 192" | grep -v grep | awk '{print $2}' | xargs kill
done #Save output of this into file.
rm ftptest.txt
#----------------------------------------------------------------------
#Check for smb
#if smbmap isn't installed, install it.
install_smbmap () {
	type smbmap >/dev/null 2>&1
	if [ $? != 0 ]
	then
		echo "[!] smbmap not found... installing"
		git clone https://github.com/ShawnDEvans/smbmap /opt/smbmap
		pip install -r /opt/smbmap/requirements.txt
		ln -s /opt/smbmap/smbmap.py /usr/bin/smbmap
	fi
}

#if enum4linux isn't installed, install it
install_enum4linux () {
	type enum4linux >/dev/null 2>&1
	if [ $? != 0 ]
	then
		echo "[!] enum4linux not found... installing"
		git clone https://github.com/portcullislabs/enum4linux /opt/enum4linx
		ln -s /opt/enum4linux/enum4linux.pl /usr/bin/enum4linux
	fi
}


#checks for open SMB services and enumerates them
smbPorts=()
count=$(cat nmap/$target.nmap | egrep " netbios-ssn " | grep -v "139" | wc -l)
if [ $count -ne 0 ]
then
	install_smbmap
	install_enum4linux
	smbflag=1
	echo "[!] Detected SMB"
	query=$(cat nmap/$target.nmap | egrep " netbios-ssn | microsoft-ds? " )
	while read -r line; do
		port=$(echo -n "$line" | cut -d '/' -f1)
		echo "[!] Port $port is hosting an SMB service"
		smbPorts+=("$port")
		echo smbPorts[@]

	done <<< "$query"
else
	smbflag=0
fi
#Do smb enumeration things
for port in ${smbPorts[@]}; do
	#Run smbmap
	smbmap -H $target -P $port 2>&1 > smbmap.txt
	#Run enum4linux
	enum4linux $target 2>&1 > enum4linux.txt
done

#----------------------------------------------------------------------
echo -e "[*] Starting nmap NSE scan"
nmap -p- -A -oA nmap/$target-NSE -Pn -T5 -sV -v0 $target --host-timeout 99999m > /dev/null 2>&1

echo -e "[*] Starting nmap UDP scan"
nmap -p 53,69,161 -sUV -oA nmap/$target-UDP -Pn -T5 -v0 $target --host-timeout 99999m > /dev/null 2>&1

#Examine https certificate
#echo | openssl s_client -showcerts -servername 192.168.0.116 -connect 192.168.0.116:443 2>/dev/null | openssl x509 -inform pem -noout -text

cat nmap/$target.nmap | grep open
echo -e '\nProgram Complete\n'

#Iterate over newline-separated variable
# 	while read -r line; do
# 		echo "... $line ..."
# 	done <<< "$query"

# #Iterate over array
# 		for i in ${httpPorts[@]}; do 
# 			echo $i;
# 		done