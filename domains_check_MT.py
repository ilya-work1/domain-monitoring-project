import requests
import ssl
import socket
from datetime import datetime, timezone
import json
import concurrent.futures
from queue import Queue
import time
from config import logger


# function that recieves JSON of urls and returns JSON of the status of the urls & SSL status and expiration date

def check_url(url):
    """Check single URL status and SSL"""
    logger.debug(f"Checking URL: {url}")
    result = {
        'url': url, 
        'status_code': 'FAILED', 
        'ssl_status': 'unknown',
        'expiration_date': 'unknown', 
        'issuer': 'unknown'
    }
    
    try:
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
    
    return result

def check_certificate(url):
    """Check SSL certificate details"""
    logger.debug(f"Checking SSL certificate for: {url}")
    try:
        hostname = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        expiry_date_str = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date_str, "%b %d %H:%M:%S %Y %Z")
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
        issuer = dict(x[0] for x in cert['issuer'])
        issuer_name = issuer.get('commonName', 'unknown')
        expiry_date_formatted = expiry_date.strftime("%Y-%m-%d %H:%M:%S")

        if expiry_date < datetime.now(timezone.utc):
            logger.warning(f"SSL certificate expired for {url}")
            return 'expired', expiry_date_formatted, issuer_name
        else:
            logger.info(f"Valid SSL certificate found for {url}")
            return 'valid', expiry_date_formatted, issuer_name
            
    except Exception as e:
        logger.error(f"SSL check error for {url}: {str(e)}")
        return 'failed', 'unknown', 'unknown'

def check_url_mt(urls):
    """Multi-threaded URL checker"""
    logger.info(f"Starting multi-threaded check for {len(urls)} URLs")
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as liveness_threads_pool:
            futures = [liveness_threads_pool.submit(check_url, url) for url in urls]    
            results = [future.result() for future in futures]
        
        with open('report.json', 'w') as outfile:
            json.dump(results, outfile, indent=4)
            
        logger.info(f"Completed checking {len(urls)} URLs")
        return results
    except Exception as e:
        logger.error(f"Error in multi-threaded check: {str(e)}", exc_info=True)
        return []

if __name__ == '__main__':
    urls = ['www.google.com', 'www.facebook.com', 'www.youtube.com']
    check_url_mt(urls)