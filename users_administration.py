
import hashlib

import mysql.connector
from credentional import  DB_PASSWORD, DB_ROOT_USERNAME, DB_USERS, DB_HOST, DB_PORT

USER_DB = mysql.connector.connect(
    host=DB_HOST,
    port = DB_PORT,
    user = DB_ROOT_USERNAME,
    passwd = DB_PASSWORD,
    database = DB_USERS
)

USER_TYPES = ['admin', 'regular','s']

def add_user(username, password, user_type):#could raise NameError
    
    if user_type not in USER_TYPES:
        raise NameError("No such user type!")
    elif len(username)>=44:
        raise NameError("The username is too long")
    
    cursor = USER_DB.cursor(buffered=True) #to solve:       mysql.connector.errors.InternalError: Unread result found
    
    #check if username is taken
    cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
    selected_username = cursor.fetchone()
    if selected_username is not None:
        raise NameError("Username already taken!")
    
    salted_hash = hashlib.sha512((password+username+"BestSexInTheWorld").encode('UTF-8')).hexdigest()
    
    cursor.execute("INSERT INTO users (username, hash, type) VALUES (%s, %s, %s)", (username, salted_hash, user_type))
    
    USER_DB.commit()

def remove_user(username):
    cursor = USER_DB.cursor(buffered=True)
    
    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    
    USER_DB.commit()
    
def admin_validation(username, password):
    cursor = USER_DB.cursor(buffered=True)
    
    salted_hash = hashlib.sha512((password+username+"BestSexInTheWorld").encode('UTF-8')).hexdigest()
    
    cursor.execute("SELECT type FROM users WHERE username=%s AND hash=%s", (username, salted_hash))
    
    user_type = cursor.fetchone()
    
    if user_type is None:
        raise NameError("Wrong username or password!")
    
    return user_type[0]
