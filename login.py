import json
import os


def initialize_users_file():
    """
    Creates users.json if it doesn't exist
    This should be at the top of login.py, after imports
    """
    if not os.path.exists('users.json'):
        default_structure = {
            "users": []
        }
        with open('users.json', 'w') as f:
            json.dump(default_structure, f, indent=4)


def check_login(username, password):
    """function for checking login credentials"""
    initialize_users_file()

    try:
        with open('users.json', 'r') as f:
            users_file = json.load(f)

        users_file = users_file.get('users')
        for user_dict in users_file:
            if username.upper() == user_dict.get('username').upper():
                if password == user_dict.get('password'):
                    return True
                else:
                    return False
                    
        return False
            
    except Exception as e:
        print(f"Error in check_login: {str(e)}")
        return False
       
           
        

def check_username_avaliability(username):
    initialize_users_file()
    """
    Check if the username is free before new registration"""
    with open('users.json', 'r')as f:
        users_file=json.load(f)

    users_file=users_file.get('users')

    for user_dict in users_file:
        if user_dict.get('username').upper() == username.upper():
            print('this user is not available')
            return False

    return True


def registration(username, password, full_name=None, is_google_user=False, profile_picture=None):
    initialize_users_file()
    """
    function for register new username with additional user info
    """
    if check_username_avaliability(username):
        NewUser = {
            'username': username.lower(),
            'password': password,
            'full_name': full_name,
            'is_google_user': is_google_user,
            'profile_picture': profile_picture
        }

        with open('users.json', 'r') as f:
            users_file = json.load(f)

        users_file['users'].append(NewUser)

        with open('users.json', 'w') as f:
            json.dump(users_file, f, indent=4)