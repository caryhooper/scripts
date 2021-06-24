#!/usr/bin/python3
#Cary Hooper @nopantrootdance


#showcase parallelism patterns in Python3
import requests, sys, datetime, math
begin = datetime.datetime.now()

#Note: this import is important!
import concurrent.futures




#Populate set of top 100 URLs to visit from file.
url_set = set()
with open("/tmp/top100.txt","r") as file:
	[url_set.add(line.strip()) for line in file.readlines()]

# for url in url_set:
# 	print(url)

# sys.exit()

global url_chunks
global processes
global threads


#Define our worker function
def do_http_request(url):
	try:
		response = requests.get(url,timeout=(10,30))
		print(f"Status Code {response.status_code}: {url} - response length {len(response.text)} bytes.")
		return "Success"
	except Exception as e:
		print(f"HTTP Error in do_http_request to {url}.: {e}")
		return "Failure"

# for url in url_set:
# 	do_http_request(url)

# sys.exit(0)




# threads = 8

# #https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
# with concurrent.futures.ThreadPoolExecutor(threads) as executor:
# 	#Not important
# 	future_to_url = {executor.submit(do_http_request, url): url for url in url_set}

# 	#As completed handles mapping tasks to threads.
# 	for future in concurrent.futures.as_completed(future_to_url):
# 		url = future_to_url[future]
		
# 		try:
# 			success_string = future.result()
# 			print(f"{url}? {success_string}")
# 		except Exception as e:
# 			print(f"Unknown Error ({url}): {e}")



# sys.exit(0)


















def chunks(this_iterable, num_chunks):
	#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
	"""Yield successive n-sized chunks from this_iterable."""
	this_iterable = list(this_iterable)
	chunk_size = math.ceil(len(this_iterable) / num_chunks)
	if chunk_size == 0:
		chunk_size = 1
	for i in range(0,len(this_iterable), chunk_size):
		yield this_iterable[i: i + chunk_size]

def http_worker(url_list):
	for url in url_list:
		do_http_request(url)


processes = 8
url_chunks = chunks(url_set,processes)


# for chunk in url_chunks:
# 	print(chunk)

# sys.exit(0)

# #https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
# with concurrent.futures.ProcessPoolExecutor(processes) as executor:
# 	future_to_url = {executor.submit(http_worker, chunk): chunk for chunk in url_chunks}

# 	#As completed handles mapping tasks to threads.
# 	for future in concurrent.futures.as_completed(future_to_url):
# 		url_chunk = future_to_url[future]
		
# 		try:
# 			success_string = future.result()
# 			# print(f"{url}? {success_string}")
# 		except Exception as e:
# 			print(f"Unknown Error ({url}): {e}")


# sys.exit(0)



















threads = 8
processes = 8

def http_worker_multithreaded(url_set, threads):

	#https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
	with concurrent.futures.ThreadPoolExecutor(threads) as thread_executor:
		future_to_url = {thread_executor.submit(do_http_request, url): url for url in url_set}

		#As completed handles mapping tasks to threads.
		for future in concurrent.futures.as_completed(future_to_url):
			url = future_to_url[future]
			
			try:
				success_string = future.result()
				print(f"{url}? {success_string}")
			except Exception as e:
				print(f"Unknown Error ({url}): {e}")


#https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
with concurrent.futures.ProcessPoolExecutor(processes) as proc_executor:
	future_to_url = {proc_executor.submit(http_worker_multithreaded, chunk, threads): chunk for chunk in url_chunks}

	#As completed handles mapping tasks to threads.
	for future in concurrent.futures.as_completed(future_to_url):
		url_chunk = future_to_url[future]
		
		try:
			success_string = future.result()
			print(f"Completed {url_chunk}")
		except Exception as e:
			print(f"Unknown Error ({url}): {e}")



end = datetime.datetime.now()
diff = end - begin
print(f"Program completed in {diff.total_seconds()}")