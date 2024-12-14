import requests
import ssl
import socket
from datetime import datetime, timezone
import json
import concurrent.futures
from queue import Queue
import time
from config import logger
from DataManagement import update_domains

##Global Queue
urls_queue = Queue()
analyzed_urls_queue = Queue()

# function that recieves JSON of urls and returns JSON of the status of the urls & SSL status and expiration date
def check_url():
    while not urls_queue.empty():
        url = urls_queue.get()
        result = {
            'url': url, 
            'status_code': 'FAILED', 
            'ssl_status': 'unknown',
            'expiration_date': 'unknown', 
            'issuer': 'unknown'
        }

        try:
            url = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            
            # Create two futures for concurrent execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                ssl_future = executor.submit(check_certificate, url)
                http_future = executor.submit(
                    requests.get, 
                    f'http://{url}', 
                    timeout=0.5  # Reduced timeout
                )

                # Get results with timeout
                ssl_status, expiry_date, issuer_name = ssl_future.result(timeout=3)
                http_response = http_future.result(timeout=3)

                if http_response.status_code == 200:
                    result.update({
                        'status_code': 'OK',
                        'ssl_status': ssl_status,
                        'expiration_date': expiry_date,
                        'issuer': issuer_name
                    })

        except Exception as e:
            logger.error(f"Error checking {url}: {str(e)}")
        finally:
            analyzed_urls_queue.put(result)
            urls_queue.task_done()

def check_certificate(url):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((url, 443), timeout=2) as sock:  # Reduced timeout
            with context.wrap_socket(sock, server_hostname=url) as ssock:
                cert = ssock.getpeercert()

        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        issuer = dict(x[0] for x in cert['issuer'])
        return ('valid', expiry_date.strftime("%Y-%m-%d %H:%M:%S"), issuer.get('commonName', 'unknown'))
    except Exception as e:
        return ('failed', 'unknown', 'unknown')


def check_url_mt(domains, username):
    logger.info(f"Starting optimized check for {len(domains)} domains for user: {username}")
    
    # Clear queues before starting new batch
    while not urls_queue.empty():
        urls_queue.get()
    while not analyzed_urls_queue.empty():
        analyzed_urls_queue.get()
    
    # Add domains to queue
    for domain in domains:
        if isinstance(domain, dict) and 'url' in domain:
            urls_queue.put(domain['url'])
        else:
            urls_queue.put(domain)
    
    expected_count = urls_queue.qsize()
    logger.info(f"Added {expected_count} domains to queue")
    
    max_workers = min(500, len(domains) * 2)
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        logger.info(f"Starting {max_workers} threads for URL processing")
        futures = []
        for _ in range(max_workers):
            futures.append(executor.submit(check_url))
        
        # Wait with timeout
        done, not_done = concurrent.futures.wait(
            futures, 
            timeout=30,  # Overall timeout
            return_when=concurrent.futures.ALL_COMPLETED
        )
        
        if not_done:
            logger.warning(f"{len(not_done)} threads did not complete")
    
    # Collect results
    while not analyzed_urls_queue.empty():
        result = analyzed_urls_queue.get()
        results.append(result)
        analyzed_urls_queue.task_done()
    
    logger.info(f"Expected {expected_count} results, got {len(results)}")
    
    if len(results) < expected_count:
        logger.warning(f"Lost {expected_count - len(results)} checks")
    
    update_domains(results, username)
    return results

if __name__ == '__main__':
    urls = ['www.google.com', 'www.facebook.com', 'www.youtube.com']
    username = 'example_user'
    check_url_mt(urls, username)
