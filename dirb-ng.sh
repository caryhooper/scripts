#!/bin/bash
#This is a wrapper for dirb.  Because I am tired of enumeration
echo -e "dirb wrapper (input a directory of wordlists)"
echo -e "by Cary Hooper @nopantrootdance"
echo -e ""

if [ $# != 2 ]
then
	echo -e "\tusage: ./dirb-ng.sh /path/to/wordlist/directory"
	exit
fi

#Fixing trailing slash
function addslash(){
	if [ "${1: -1}" = "/" ]; then
		export directory="$1"
		echo "directory is $1"
	else
		export directory="${1}/"
		echo "directory is ${1}/"
	fi
}

export url="$1"
addslash $2
echo -e "Using wordlists from: $directory"

function dir_cmd(){
	#Not the cleanest way of handling output, but it works.
	dirb $1 $2 -r -S -w -X '.html','.php','','.bak','.txt','~' | tr -d '-' | egrep -v "GENERATED|WORDLIST_FILES|START_TIME|DOWNLOADED|END_TIME" > /tmp/dirbtmp.txt
	export OLDIFS=$IFS
	export IFS=$'\n'
	set -f
	for i in $(cat /tmp/dirbtmp.txt 2>/dev/null); 
	do
		grep -qxF "$i" /tmp/dirbout.txt || echo -e "$i" >> /tmp/dirbout.txt
	done
	export IFS=OLDIFS
	rm /tmp/dirbtmp.txt 2>/dev/null
}

#For loop - iterates over everything in the directory.
function do_dir(){
	addslash $1

	for thing in $(find ${directory} -type f)
	do
		#Check if file
		if [ -f "$thing" ] ; then
			echo -e "\tRunning dirb with $thing"
			dir_cmd $url $thing
		#Check if file
		else
			echo -e "$thing is not a file."
		fi
	done
}

do_dir $directory
echo -e "Program has completed."

echo -e "----------- RESULTS ------------"
cat /tmp/dirbout.txt
rm /tmp/dirbout.txt
