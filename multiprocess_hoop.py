import concurrent.futures
import python_parallelism_showcase as hoop


threads = hoop.threads
processes = hoop.processes
url_chunks = hoop.url_chunks


#https://www.tutorialspoint.com/concurrency_in_python/concurrency_in_python_pool_of_threads.htm
with concurrent.futures.ProcessPoolExecutor(processes) as proc_executor:
	future_to_url = {proc_executor.submit(hoop.http_worker_multithreaded, chunk, threads): chunk for chunk in url_chunks}

	#As completed handles mapping tasks to threads.
	for future in concurrent.futures.as_completed(future_to_url):
		url_chunk = future_to_url[future]
		
		try:
			success_string = future.result()
			print(f"Completed {url_chunk}")
		except Exception as e:
			print(f"Unknown Error ({url}): {e}")
