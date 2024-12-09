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
    """Check single URL status and SSL"""
    while not urls_queue.empty():
        url = urls_queue.get()
         
        logger.info(f"Starting check for URL: {url}")
        result = {
            'url': url, 
            'status_code': 'FAILED', 
            'ssl_status': 'unknown',
            'expiration_date': 'unknown', 
            'issuer': 'unknown'
        }

        try:
            url =  url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
            ssl_status, expiry_date, issuer_name = check_certificate(url)
            response = requests.get(f'http://{url}', timeout=1)
            if response.status_code == 200:
                result.update({
                    'status_code': 'OK',
                    'ssl_status': ssl_status,
                    'expiration_date': expiry_date,
                    'issuer': issuer_name
                })
                logger.info(f"URL check successful for {url}")
            else:
                logger.warning(f"URL check failed for {url} with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error checking {url}: {str(e)}", exc_info=True)
        finally:
            analyzed_urls_queue.put(result)
            logger.debug(f"Added result to analyzed queue: {result}")
            urls_queue.task_done()



def check_certificate(url):
    logger.debug(f"Checking SSL certificate for: {url}")
    try:

        hostname = url

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443),timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        issuer = dict(x[0] for x in cert['issuer'])
        logger.info(f"SSL certificate valid for {url}: expires {expiry_date}")
        return ('valid', expiry_date.strftime("%Y-%m-%d %H:%M:%S"), issuer.get('commonName', 'unknown'))
    except Exception as e:
        return ('failed', 'unknown', 'unknown')



def check_url_mt(domains, username):
    logger.info(f"Starting multi-threaded check for {len(domains)} domains for user: {username}")
    
    for domain in domains:
        if isinstance(domain, dict) and 'url' in domain:
            urls_queue.put(domain['url'])
        else:
            urls_queue.put(domain)

    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
        logger.info("Starting 20 threads for URL processing")
        for _ in range(80):
            executor.submit(check_url)

    urls_queue.join()
    logger.info("All URLs processed")

    results = []
    while not analyzed_urls_queue.empty():
        result = analyzed_urls_queue.get()
        logger.debug(f"Processed result: {result}")
        results.append(result)
        analyzed_urls_queue.task_done()

    # Update domains with results
    update_domains(results, username)
    
    # Summary logging
    success_count = sum(1 for res in results if res['status_code'] == 'OK')
    failure_count = len(results) - success_count
    logger.info(f"Summary for {username}: {success_count} successful checks, {failure_count} failed checks.")

    logger.info(f"Results: {results}")
    return results


if __name__ == '__main__':
    urls = ['www.google.com', 'www.facebook.com', 'www.youtube.com']
    username = 'example_user'
    check_url_mt(urls, username)
