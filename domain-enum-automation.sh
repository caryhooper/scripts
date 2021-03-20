#!/bin/bash
#Three arguments: domain controller IP, valid domain username, valid password
#Automating routine enumeration tasks.
#Depends on enum-automation.sh
echo Initial Domain Enumeration Script
echo by Cary Hooper @nopantrootdance
#TODO:
#  scan for hosts not in the domain

#Check for 3 args
if [ $# != 3 ]
then
	echo "usage: ./domain-enum-automation.sh <dc-ip> <username> <password>"
	exit
fi
#Handle Args
dcip=$1
echo Determining domain name...
domain=$(nmap -p 389 -sV -Pn $dcip | grep 389 | cut -d '(' -f2 | cut -d ',' -f1 | awk '{print $2}' | cut -d '.' -f1 )
echo "\t Domain: $domain"
username=$2
password=$3

#Function to check + install ldapdomaindump
install_ldapdomaindump(){
	type ldapdomaindump >/dev/null 2>&1
	if [ $? != 0 ]
	then
		echo "[!] ldapdomaindump not found... installing"
		sudo pip install ldap3 dnspython ldapdomaindump
}

#Create domain info directory if it doesn't exist
if [ ! -d $domain ]
then
	echo Creating output directory...
	mkdir $domain
fi

#Dump domain data into greppable format.  Do things with the files
echo "Checking if ldapdomaindump is installed"
install_ldapdomaindump
echo "Launching: ldapdomaindump ldap://$dcip -u \"$domain\\$username\" -p \"$password\""
ldapdomaindump ldap://$dcip -u "$domain\\$username" -p "$password" -o $domain

computers=$(cat $domain/domain_computers.grep  | grep -v sAMAccountName | awk '{print $1}' | wc -l)
echo Computers in $domain:
for computer in computers
do
	echo "\t$computer"
done
echo ----------------
users=$(cat $domain/domain_users.grep  | grep -v sAMAccountName | awk '{print $1}')
echo Users in $domain:
for user in users
do
	echo "\t$user"
done

#Find IPs & Hostnames  to make directories
cat $domain/domain_computers.grep | awk '{print $3}' | grep -v dNS | xargs dig a @$dcip | grep $domain | egrep -v "^;" | awk '{print $1"-"$5}' | cut -d '.' -f1,4-7 | sed  's/\.-/-/g' | tr [[:lower:]] [[:upper:]] | xargs mkdir

#Once directories are made, loop through and invoke enum-automation.sh on each.
#Single threaded on purpose.  Add "&" to the end if bandwidth allows
#Shaving enumpath with 1337 bash parameter expansion
export enumpath=${0%/*}"/enum-automation.sh"
#echo Enumpath is $enumpath

#For each host, scan + enumerate
for dir in $(ls | grep $(echo $dcip | cut -d '.' -f1-3))
do
	ip=$(echo $dir | cut -d '-' -f2)
	hostname=$(echo $dir | cut -d '-' -f1)
	echo $ip >> $domain/ips.txt
	echo $hostname >> $domain/hosts.txt
	cd $dir
	mkdir loot
	echo Scanning $hostname at $ip
	$enumpath $ip | egrep -v "Initial Host|nopantrootdance" 
	cd ../
	echo Finished scanning $hostname at $ip
	echo ----------------
done
