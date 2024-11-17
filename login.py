import json

def check_login(username, password):
    """function for checking login credentials
    """
    with open('users.json', 'r')as f:
        users_file=json.load(f)

    users_file=users_file.get('users')
    for user_dict in users_file:
        # check user and password compatibility
        if username.upper() == user_dict.get('username').upper():
            if password == user_dict.get('password'):
                return True
            else:
                return False

    return False


def check_username_avaliability(username):
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


def registration(username, password):
    """
    function for register new username """
    if check_username_avaliability(username):

        NewUser={'username': username.lower(), 'password': password}

        with open('users.json', 'r')as f:
            users_file=json.load(f)

        users_file['users'].append(NewUser)

        with open('users.json', 'w')as f:
            json.dump(users_file, f)

        print(users_file)