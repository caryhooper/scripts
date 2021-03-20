#Cary Hooper
#2021-03-15 
#Given a domain, outputs a newline-delimited list of subdomains
#available through various sources.
#Warning - some APIs have a rate limit
#Queries taken from https://github.com/dwisiswant0/awesome-oneliner-bugbounty

if [ $# -ne 2 ]
then
	echo "No domain and/or domain file supplied."
	echo "Usage: ./osint_subdomains.sh my_domain.com domains.txt"
	exit 1
fi

#RapidDNS.io
curl -s "https://rapiddns.io/subdomain/$1?full=1#result" | grep "<td><a" | cut -d '"' -f 2 | grep http | cut -d '/' -f3 | sed 's/#results//g' | sort -u | tee tmp.out
#BufferOver.run
curl -s "https://dns.bufferover.run/dns?q=.$1" |jq -r .FDNS_A[]|cut -d',' -f2|sort -u | tee tmp.out
#Riddler.io
curl -s "https://riddler.io/search/exportcsv?q=pld:$1" | grep -Po "(([\w.-]*)\.([\w]*)\.([A-z]))\w+" | sort -u | tee tmp.out
#VirusTotal
# curl -s "https://www.virustotal.com/ui/domains/$1/subdomains?limit=40" | grep -Po "((http|https):\/\/)?(([\w.-]*)\.([\w]*)\.([A-z]))\w+" | sort -u
#CertSpotter
curl -s "https://certspotter.com/api/v1/issuances?domain=$1&include_subdomains=true&expand=dns_names" | jq .[].dns_names | tr -d '[]"\n ' | tr ',' '\n' | tee tmp.out
#Archive
curl -s "http://web.archive.org/cdx/search/cdx?url=*.$1/*&output=text&fl=original&collapse=urlkey" | sed -e 's_https*://__' -e "s/\/.*//" | sort -u | tee tmp.out
#JLDC
curl -s "https://jldc.me/anubis/subdomains/$1" | grep -Po "((http|https):\/\/)?(([\w.-]*)\.([\w]*)\.([A-z]))\w+" | sort -u | tee tmp.out
#securitytrails
curl -s "https://securitytrails.com/list/apex_domain/$1" | grep -Po "((http|https):\/\/)?(([\w.-]*)\.([\w]*)\.([A-z]))\w+" | grep ".$1" | sort -u | tee tmp.out
#crt.sh
curl -s "https://crt.sh/?q=%25.$1&output=json" | jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u | tee tmp.out
#Wayback URLs
waybackurls $1 | cut -d '?' -f1 | cut -d '/' -f3 | cut -d ':' -f1 | cut -d '@' -f2| sort -u | tee tmp.out

#sort -u the entire list
cat tmp.out | sort -u > subdomains.$1.out && rm tmp.out