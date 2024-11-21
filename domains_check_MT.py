import requests
import ssl
import socket
from datetime import datetime, timezone
import json
import concurrent.futures
from queue import Queue
from DataManagement import add_domains, update_domains

urls_queue = Queue()
analyzed_urls_queue = Queue()

# Function to check the status of a URL
def check_url():
    while not urls_queue.empty():
        url_entry = urls_queue.get()
        url = url_entry['url']
        result = {'url': url, 'status_code': 'FAILED', 'ssl_status': 'unknown',
                  'expiration_date': 'unknown', 'issuer': 'unknown','last_checked':'unknown'}
        try:
            ssl_status, expiry_date, issuer_name = check_certificate(url)
            response = requests.get(f'http://{url}', timeout=5)  # Increased timeout
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if response.status_code == 200:
                result.update({
                    'status_code': 'OK',
                    'ssl_status': ssl_status,
                    'expiration_date': expiry_date,
                    'issuer': issuer_name,
                    'last_checked': current_time

                })
        except requests.exceptions.RequestException as e:
            print(f"HTTP Error with {url}: {e}")
        finally:
            analyzed_urls_queue.put(result)
            urls_queue.task_done()

# Function to check the SSL certificate of a URL
def check_certificate(url):
    try:
        hostname = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        issuer = dict(x[0] for x in cert['issuer'])
        return ('valid', expiry_date.strftime("%Y-%m-%d %H:%M:%S"), issuer.get('commonName', 'unknown'))
    except Exception as e:
        print(f"SSL Error with {url}: {e}")
        return ('failed', 'unknown', 'unknown')

# Function to check the status of a list of URLs or a single URL for a given user in a multithreaded way
def check_url_mt(domains, username):
    if not isinstance(domains, list) or not all(isinstance(d, (str, dict)) for d in domains):
        raise ValueError("Invalid input: domains must be a list of URLs or dictionaries with 'url' keys.")

    for domain in domains:
        if isinstance(domain, dict) and 'url' in domain:
            urls_queue.put(domain)
        else:
            urls_queue.put({"url": domain})

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for _ in range(20):
            executor.submit(check_url)

    urls_queue.join()

    results = []
    while not analyzed_urls_queue.empty():
        results.append(analyzed_urls_queue.get())
        analyzed_urls_queue.task_done()

    try:
        if update_domains(results, username):  
            print(f"Domains updated for {username}")
        else:
            print(f"Error updating domains for {username}")
    except Exception as e:
        print(f"Error updating domains for {username}: {e}")


    return results

