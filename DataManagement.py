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