#!/usr/bin/env python3
import htmllistparse
import requests
import os
#TODO - make platform agnostic

storage_path = "/plex"
url = "http://192.168.0.12:8888"

print(f"Syncing {storage_path} with {url}")

def download_file(download_string,storage_path):
	#Given a file URL and a local directory, download the file
	print(f"Downloading {download_string} and saving to {storage_path}")
	#Stream the HTTP Request with stream=True
	with requests.get(f"{download_string}", stream=True) as response:
		#Returns a error if an error occurs any step of the way
		response.raise_for_status()
		print(f"Downloading file {download_string} with HTTP code {response.status_code}...")
		#Extract the filename from the argument
		filename = download_string.split('/')[-1]
		#Open and write the bytes to a file, one chunk at a time
		with open(f"{storage_path}/{filename}",'wb') as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
			#Close the file to prevent nasty (hard-to-debug) filesystem errors
			file.close()
	print(f"Download complete: {filename}")


def download_directory(url,storage_path):
	#Given a url and a local directory, list and download the contents of an entire directory.
	#Change directory to the storage directory.
	os.chdir(storage_path)
	#Get a list of all files in the local directory
	#https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
	_, _, local_filenames = next(os.walk(storage_path))
	#Get remote directory listing via HTTP (uses 3rd party module htmllistparse)
	cwd, listing = htmllistparse.fetch_listing(url, timeout=30)
	#Filter listing for executable scripts.  Uses a feature in Python called list comprehension
	listing = [i for i in listing if not ('.py' in i.name or '.sh' in i.name )]
	print(f"Listing: {listing}")
	#Iterate through all served files/directories to determine what is a file and what is a directory
	for thing in listing:
		#Determine if object is directory with / in name
		if '/' in thing.name:
			directory = thing.name
			directorypath = f"{storage_path}/{directory}"
			directory_noslash = directory.replace(os.path.sep,'')
			newurl = f"{url}/{directory_noslash}"
			#Check if directory exists locally
			if not os.path.isdir(directorypath):
				#If not, create directory
				os.mkdir(directorypath)
			#Recursively call this function until no more directories are found.
			download_directory(newurl,directorypath)
			#When complete, change back to original directory to reset the recursive "chdir"s
			os.chdir(storage_path)
		else:
			#Else... item is a file to download
			file = thing.name
			#Check if we've downloaded a file already.  If so, skip it!
			if file not in local_filenames:
				download_string = f"{url}/{file}"
				#Call download_file to download the single file chunk by chunk.
				download_file(download_string,storage_path)


#Initial call to download_directory (recursive function)
download_directory(url,storage_path)
print("Sync complete.")
