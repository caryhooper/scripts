import googlesearch
import urllib.parse

#Microsoft v Google

def get_domain(url):
	parsed_url = urllib.parse.urlparse(url)
	domain = parsed_url.netloc
	return domain


all_domains = set()
base_domain = "microsoft.com"
query = f"\"{base_domain}\""

def build_query(all_domains):
	for domain in all_domains:
		query += f" -\"{domain}\""
	print(f"Query changed to {query}")
	return query

def do_searches(query,all_domains):
	count = 10
	new_domain_found = False

	for i in range(0,count):
		print(f"Google query: {query}")
		#results = googlesearch.search(query, num=10, stop=10, pause=2)
		results = get_google_results(query)
		for j in results:
			print(j)
			domain = get_domain(j)
			if domain not in all_domains:
				all_domains.add(domain)
				new_domain_found = True
				print(f"Found new domain {domain}")
		if new_domain_found:
			return all_domains
	return all_domains


for i in range(0,100):
	
	new_domains_set = do_searches(query,all_domains)
	if new_domains_set == all_domains:
		break
	else:
		build_query(new_domains_set)

	all_domains = new_domains_set

