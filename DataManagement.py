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
        username = username
        current_domains = load_domains(username)
        
        # Merge new domains into current_domains
        for new_domain in domains:
            # Check if domain already exists
            existing = next((d for d in current_domains if d['url'] == new_domain['url']), None)
            if existing:
                # Update existing domain's details
                existing.update(new_domain)
            else:
                # Add new domain
                current_domains.append(new_domain)

        # Write updated domains back to file
        with open(f'{username}_domains.json', 'w') as f:
            json.dump({"domains": current_domains}, f, indent=4)
        return True
    except Exception as e:
        print(f"Error updating domains for {username}: {e}")
        return False