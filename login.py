users_list = [{'username': 'danbd', 'password': 'Dan123456'}, {'username': 'ilyash', 'password': 'Ilya123456'},
              {'username': 'matanel', 'password': 'Matan123456'}]


def check_login(username, password):
    """function for checking login credentials
    """
    for user_dict in users_list:
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
    for user_dict in users_list:
        if user_dict.get('username').upper() == username.upper():
            print('this user is not available')
            return False

    return True


def registration(username, password):
    """
    function for register new username """
    if check_username_avaliability(username):
        users_list.append({'username': username.lower(), 'password': password})
    print(users_list)
