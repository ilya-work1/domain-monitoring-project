import requests
import json
import concurrent.futures
import ssl
import socket
import concurrent.futures
from datetime import datetime



#function that recieves JSON of url and returns JSON of the status of the urls & SSL status and expiration date

def check_url(url):

        result = {'url': url, 'status_code': 'FAILED', 'ssl_status': 'unknown',
                  'expiration_date': 'unknown'}  # Default to FAILED
        try:
            ssl_status, expiry_date = check_certificate(url)
            response = requests.get(f'http://{url}', timeout=1)
            if response.status_code == 200:
                result['status_code'] = 'OK'
                result['ssl_status'] = ssl_status
                result['expiration_date'] = expiry_date
        except requests.exceptions.RequestException:
            result['status_code'] = 'FAILED'
        finally:
            return result




#function that generates a report of the status of the urls & SSL status and expiration date -- called from check_url function
def check_certificate(url):
    try:
        # Remove "https://", "http://", "www." from the URL if present
        hostname = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        
        # Establish a secure connection to fetch the SSL certificate
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
        # Get the certificate's expiration date
        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z")
        
        # Convert expiration date to a readable string format
        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if the certificate is expired
        if expiry_date < datetime.utcnow():
            return 'expired', expiry_date_formatted
        else:
            return 'valid', expiry_date_formatted
    except Exception as e:
        return 'failed', str(e)


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
    urls = ['www.google.com', 'www.facebook.com', 'www.twitter.com', 'www.linkedin.com']
    results = check_url_mt(urls)
    print(results)



