#!/usr/bin/python3
#Cary Hooper @nopantrootdance


#showcase parallelism patterns in Python3

import requests, sys, datetime, math
import concurrent.futures

from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple
from functools import partial
from pprint import pprint

timer_instance_count = 0

class Timer:
    name = ""
    timers = []
    start = None
    end = None
    elapsed = None
    
    def __init__(self, name=""):
        Timer.timers.append(self)
        self.name = f"{len(Timer.timers)}:{name}"

          
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

    def __enter__(self, *args, **kwargs):
        self.start = datetime.datetime.now()
        print(f"Start Task - {self.name}")

    def __exit__(self, *args, **kwargs):
        self.end = datetime.datetime.now()
        self.elapsed = self.end - self.start
        print(f"Left Timer - Task {self.name} completed in {self.elapsed}")

    @staticmethod
    def collect_timer_reports():
        return "Timer Report:\n" + "\n".join([i.report() for i in Timer.timers])

    def report(self):
        return f"""
#####
Name: {self.name}
Start: {self.start}
End: {self.end}
Elapsed: {self.elapsed}
#####"""


class CallbackThreadPoolExecutor(ThreadPoolExecutor):

    def __init__(self, *args, **kwargs):
        callback = kwargs.pop("callback")
        if callback:
            self.callback = callback
        super().__init__(*args, **kwargs)

    def submit(self, *args, **kwargs):
        task = super().submit(*args, **kwargs)
        task.add_done_callback(self.callback)

#========================================================
# Utility Functions
#========================================================

def chunks(this_iterable, num_chunks):
    #https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """Yield successive n-sized chunks from this_iterable."""
    this_iterable = list(this_iterable)
    chunk_size = math.ceil(len(this_iterable) / num_chunks)
    if chunk_size == 0:
        chunk_size = 1
    for i in range(0,len(this_iterable), chunk_size):
        yield this_iterable[i: i + chunk_size]
    
def load_urls(path):
    #Populate set of top 100 URLs to visit from file.
    with open(path,"r") as f:
        return {line.strip() for line in f.readlines()}

# Core function
def do_http_request(url):
    try:
        response = requests.get(url,timeout=(10,30))
        print(f"Status Code {response.status_code}: {url} - response length {len(response.text)} bytes.")
        return url, "Success"
    except Exception as e:
        print(f"HTTP Error in do_http_request to {url}.: {e}")
        return url, "Failure"

def http_worker(url_set):
    for i in url_set:
        do_http_request(i)

def http_worker_multithreaded(url_set, threads):
    with Timer("Multithreaded Worker"):
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

#========================================================
# Worker functions
#========================================================
def single_thread(urls):
    with Timer("Single Threaded"):
        for url in urls:
            do_http_request(url)

#Multithreaded using as_completed
def multithreaded(task, urls, num_threads=8):
    with Timer("ThreadPoolExecutor - as completed"):
        with concurrent.futures.ThreadPoolExecutor(num_threads) as executor:
            future_to_url = {executor.submit(task, url): url for url in url_set}

            #As completed handles mapping tasks to threads.
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success_string = future.result()
                    print(f"{url}? {success_string}")
                except Exception as e:
                    print(f"Unknown Error ({url}): {e}")

# Multithreading using callbacks
def future_callback(future):            
    try:
        url, success_string = future.result()
        print(f"{url}? {success_string}")
    except Exception as e:
        print(f"Unknown Error ({future}): {e}")

def multithread_callback(task, urls, num_threads=8):
    with Timer("ThreadPoolExecutor - Callback"):
        with CallbackThreadPoolExecutor(num_threads, callback=future_callback) as executor:
            [executor.submit(task, url) for url in url_set]

#Multiprocessing
def multi_process(task, url_chunks, num_processes=4):
    with Timer("ProcessPoolExecutor"):
        #https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
        with concurrent.futures.ProcessPoolExecutor(num_processes) as executor:
            future_to_url = {executor.submit(task, chunk): chunk for chunk in url_chunks}

            #As completed handles mapping tasks to threads.
            for future in concurrent.futures.as_completed(future_to_url):
                url_chunk = future_to_url[future]            
                try:
                    success_string = future.result()
                    # print(f"{url}? {success_string}")
                except Exception as e:
                    print(f"Unknown Error ({url}): {e}")

#Multiprocessing with multiplethreading
def multi_processthread(task, url_chunks, num_threads=4, num_processes=4):
    with Timer("ProcessPool, Nested Threads"):
        with concurrent.futures.ProcessPoolExecutor(num_processes) as proc_executor:
            future_to_chunk = {proc_executor.submit(task, chunk, num_threads): chunk for chunk in url_chunks}

            #As completed handles mapping tasks to threads.
            for future in concurrent.futures.as_completed(future_to_chunk):
                url_chunk = future_to_chunk[future]
                try:
                    success_string = future.result()
                    print(f"Completed {url_chunk}")
                except Exception as e:
                    print(f"Unknown Error ({url_chunk}): {e}")

# Do the thing!
if __name__ == "__main__":
    with Timer("Test Series"):
        chunk_size = 8
        url_set = load_urls("urls.txt")
        url_chunks = chunks(url_set, chunk_size)
        
        test_sets = [
                    #  partial(single_thread, url_set),
                     partial(multithreaded, do_http_request, url_set),
                     partial(multithread_callback, do_http_request, url_set),
                    #  partial(multi_process, http_worker, url_chunks),
                    #  partial(multi_processthread, http_worker_multithreaded, url_chunks),
                    ]

        [f() for f in test_sets] # BURN BABY BURN
    
    # Collect all timer results and print.
    print(Timer.collect_timer_reports())

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