import requests
import ssl
import socket
from datetime import datetime, timezone
import json
import concurrent.futures
from queue import Queue
import time



# function that recieves JSON of urls and returns JSON of the status of the urls & SSL status and expiration date

def check_url(url):
    result = {'url': url, 'status_code': 'FAILED', 'ssl_status': 'unknown',
              'expiration_date': 'unknown', 'issuer': 'unknown'}  # Default to FAILED
    try:
        # print(f"Checking URL: {url}")
        ssl_status, expiry_date, issuer_name = check_certificate(url)
        response = requests.get(f'http://{url}', timeout=1)
        if response.status_code == 200:
            result['status_code'] = 'OK'
            result['ssl_status'] = ssl_status
            result['expiration_date'] = expiry_date
            result['issuer'] = issuer_name
        # print(f"Result for {url}: {result}")
    except requests.exceptions.RequestException as e:
        # print(f"HTTP Error for {url}: {e}")
        result['status_code'] = 'FAILED'
    return result


# function that generates a report of the status of the urls & SSL status and expiration date -- called from check_url function

def check_certificate(url):
    try:
        hostname = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z")

        # Convert expiry_date to timezone-aware
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)

        issuer = dict(x[0] for x in cert['issuer'])
        issuer_name = issuer.get('commonName', 'unknown')

        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")

        # Use timezone-aware datetime for comparison
        if expiry_date < datetime.now(timezone.utc):
            return 'expired', expiry_date_formatted, issuer_name
        else:
            return 'valid', expiry_date_formatted, issuer_name
    except Exception as e:
        print(f"Error with {url}: {e}")
        return 'failed', 'unknown', 'unknown'



    #a function that performs the check_url multi-threaded
def check_url_mt(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as liveness_threads_pool:
        # Submit URL check tasks
        futures = [liveness_threads_pool.submit(check_url, url) for url in urls]    
        # Generate report after tasks complete
        results = [future.result() for future in futures]
    with open('report.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)   
    return results


if __name__ == '__main__':
    urls = ['www.google.com', 'www.facebook.com', 'www.youtube.com']
    check_url_mt(urls)