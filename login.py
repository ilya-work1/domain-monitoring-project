
users_list = [{'username':'danbd','password':'Dan123456'}, {'username':'ilyash','password':'Ilya123456'},{'username':'matanel','password':'Matan123456'}]

username = input('Username')
password = input('Password')


def check_login(username, password):
   for user_dict in users_list:
       #check user and password compatibility
           if username.upper() == user_dict.get('username').upper():
              if password == user_dict.get('password'):
                 print('you logged in')
                 return True
              else:
                 print('Wrong username or password')
                 return False 
              
   print('Wrong username or password')
   return False

def check_username_avaliability(username):
   for user_dict in users_list:
         if user_dict.get('username').upper() == username.upper():
            print('this user is not avaliable')
            return False

   return True


def registration(username, password):
   if check_username_avaliability(username):
      users_list.append({'username':username.lower(),'password':password})
   print(users_list)



registration(username, password)