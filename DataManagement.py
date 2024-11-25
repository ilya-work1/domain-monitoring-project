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
    
def remove_domain(domain_to_remove, username):
    domains = load_domains(username)
    domain_found=False
    
    for i in range(len(domains)):
        if domains[i]['url'] == domain_to_remove:
            del domains[i]
            domain_found=True
            break

    if domain_found:
        with open(f'{username}_domains.json', 'w') as f:
            json.dump({"domains": domains}, f, indent=4)
        return True
    else:     
        return False

    

def update_domains(domains, username):
    try:
        # Load current domains
        current_domains = load_domains(username)
        
        # Update or add new domains
        for domain in domains:
            # Check if domain already exists
            existing_domain = next((d for d in current_domains if d['url'] == domain['url']), None)
            
            if existing_domain:
                # Update existing domain
                existing_domain.update(domain)
            else:
                # Add new domain
                current_domains.append(domain)
        
        # Write updated domains back to file
        with open(f'{username}_domains.json', 'w') as f:
            json.dump({"domains": current_domains}, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error updating domains: {e}")
        return False
    

# schedular data management

def load_user_tasks(username):
    """Charge les tâches planifiées d'un utilisateur depuis un fichier JSON."""
    filename = f"{username}.json"
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return {"tasks": []}

def save_user_tasks(username, tasks):
    """Sauvegarde les tâches planifiées d'un utilisateur dans un fichier JSON."""
    filename = f"{username}.json"
    with open(filename, "w") as file:
        json.dump({"tasks": tasks}, file, indent=4)

def update_user_task(username, new_task):
    """Ajoute ou met à jour une tâche existante pour un utilisateur."""
    tasks_data = load_user_tasks(username)
    tasks = tasks_data.get("tasks", [])
    for task in tasks:
        if task["job_id"] == new_task["job_id"]:
            task.update(new_task)
            break
    else:
        tasks.append(new_task)
    save_user_tasks(username, tasks)

def delete_user_task(username, job_id):
    """Supprime une tâche planifiée d'un utilisateur."""
    tasks_data = load_user_tasks(username)
    tasks = tasks_data.get("tasks", [])
    tasks = [task for task in tasks if task["job_id"] != job_id]
    save_user_tasks(username, tasks)