import os
import json
from flask import jsonify

def load_domains(username):
    try:
        if not os.path.exists(f'{username}_domains.json'):
            with open(f'{username}_domains.json', 'w') as f:
                json.dump({"domains":[]}, f)

        with open(f'{username}_domains.json', 'r') as f:
            data = json.load(f)
        return data.get("domains")
    except Exception as e:
        return jsonify({'message': 'An error occurred while checking domains.', 'error': str(e)}), 500
    

def add_domains(domains, username):
    try:
        current_domains=load_domains(username)
        current_domains.append(domains)
        return True
    except Exception as e:
        return jsonify({'message': 'An error occurred while adding domains.', 'error': str(e)})
    

def update_domains(domains, username):
    try:
        current_domains=load_domains(username)
        for domain in domains:
            for current_domain in current_domains:
                if current_domain.get("url")==domain.get("url"):
                    current_domain['status_code']=domain.get('status_code')
                    current_domain['ssl_status']=domain.get('ssl_status')
                    current_domain['expiration_date']=domain.get('expiration_date')
                    current_domain['issuer']=domain.get('issuer')
                    current_domain['last_checked']=domain.get('last_checked')

                else:
                    current_domains.append(domain)
    except Exception as e:
        return jsonify({'message': 'An error occurred while adding domains.', 'error': str(e)})