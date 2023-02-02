import mysql.connector
from credentional import DB_PASSWORD, DB_ROOT_USERNAME, DB_YOUTUBE, DB_HOST, DB_PORT 

EVIL_DB = mysql.connector.connect(
    host=DB_HOST,
    user = DB_ROOT_USERNAME,
    passwd = DB_PASSWORD,
    database = DB_YOUTUBE,
    port = DB_PORT
)

def get_connector():
    return EVIL_DB

def add_channel_to_db(owner_id: int, youtube_id: str):
    cursor = EVIL_DB.cursor(buffered=True)
    
    
    cursor.execute("SELECT id FROM channels WHERE youtube_id=%s", (youtube_id,))
    # if cursor.fetchone() is None:
    #     cursor.execute("INSERT INTO channels (youtube_id) VALUES (%s)", (youtube_id,))
    #     cursor.execute("SELECT id FROM channels WHERE youtube_id=%s", (youtube_id,))
    
    try:
        channel_id = cursor.fetchone()[0]
    except Exception as e:
        cursor.execute("INSERT INTO channels (youtube_id) VALUES (%s)", (youtube_id,))
        cursor.execute("SELECT id FROM channels WHERE youtube_id=%s", (youtube_id,))
        channel_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO owner_channels (owner_id, channel_id) VALUES (%s, %s)", (owner_id, channel_id))
    
    EVIL_DB.commit()


def change_comment(owner_id: int, comment: str):
    cursor = EVIL_DB.cursor(buffered=True)
    
    cursor.execute("UPDATE owners SET comment=%s WHERE id=%s", (comment, owner_id))
    
    EVIL_DB.commit()
    
def add_owner_to_db(name: str,comment: str, youtube_id = None):
    cursor = EVIL_DB.cursor(buffered=True)
    
    cursor.execute("SELECT name FROM owners WHERE name=%s", (name,))
    # if cursor.fetchone() is not None:
    #     raise NameError("Evil person already in database!(somebody have the same name)")
    
    # else:
    #     cursor.execute("INSERT INTO owners (name, comment) VALUES (%s, %s)", (name, comment))
    #     EVIL_DB.commit()
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO owners (name, comment) VALUES (%s, %s)", (name, comment))
        EVIL_DB.commit()
    
    if youtube_id is not None:
        cursor.execute("SELECT id FROM owners WHERE name=%s", (name,))
        owner_id = cursor.fetchone()[0]
        add_channel_to_db(owner_id, youtube_id)

def is_owner_in_db_by_name(name: str):
    cursor = EVIL_DB.cursor(buffered=True)
    cursor.execute("SELECT name FROM owners WHERE name=%s", (name,))
    return cursor.fetchone() is not None

def is_channel_in_db_by_youtube_id(youtube_id: str):
    cursor = EVIL_DB.cursor(buffered=True)
    cursor.execute("SELECT youtube_id FROM channels WHERE youtube_id=%s", (youtube_id,))
    if cursor.fetchone() is None:
        return False
    return True
    return (cursor.fetchone() is not None)


def remove_youtuber(owner_id: int):
    cursor = EVIL_DB.cursor(buffered=True)
    
    cursor.execute("SELECT channel_id FROM owner_channels WHERE owner_id=%s",(owner_id,))
    try:
        channel_id = cursor.fetchone()[0]
    except Exception as e:
        raise NameError("There is no such owner_id in database!")
    cursor.execute("DELETE FROM owner_channels WHERE owner_id=%s", (owner_id,))
    cursor.execute("DELETE FROM owners WHERE id=%s", (owner_id,))
    cursor.execute("DELETE FROM channels WHERE id=%s", (channel_id,))
    
    
    EVIL_DB.commit()
    
def remove_channel_from_db(youtube_id: str):
    cursor = EVIL_DB.cursor(buffered=True)
    # print(youtube_id)
    cursor.execute("SELECT id FROM channels WHERE youtube_id=%s", (youtube_id,))
    # if cursor.fetchone() is None:
    #     raise NameError("There is no such channel in database!")
    # print(cursor.fetchone())
    try:
        channel_id = cursor.fetchone()[0]
    except Exception as e:
        raise NameError("There is no such channel in database!")
    cursor.execute("DELETE FROM owner_channels WHERE channel_id=%s", (channel_id,))
    cursor.execute("DELETE FROM channels WHERE youtube_id=%s", (youtube_id,))
    
    EVIL_DB.commit()
    
# remove_channel_from_db("UCjK0F1DopxQ5U0sCwOlXwOg")

def get_channel_id(youtube_id: str):
    # cursor = EVIL_DB.cursor(buffered=True)
    cursor = EVIL_DB.cursor()
    
    cursor.execute("SELECT id FROM channels WHERE youtube_id = '%s'"%youtube_id)
    # EVIL_DB.commit()
    # print(cursor)
    # print(cursor.fetchone())
    
    tup = cursor.fetchone()
    if tup is None:
        raise NameError("There is no such channel in database!")
    
    channel_id = tup[0]
    
    return channel_id

# print(get_channel_id('UCjK0F1DopxQ5U0sCwOlXwOg'))#UCjK0F1DopxQ5U0sCwOlXwOg

def remove_youtuber_and_all_his_channels(owner_id):
    cursor = EVIL_DB.cursor(buffered=True)
    cursor.execute("SELECT channel_id FROM owner_channels WHERE owner_id=%s", (owner_id,))
    
    channel_ids = []
    for channel_id in cursor:
        channel_ids.append(channel_id[0])
    if len(channel_ids) == 0:
        raise NameError("There is no such owner_id in database!")
    for channel_id in channel_ids:
        cursor.execute("DELETE FROM owner_channels WHERE channel_id=%s", (channel_id,))
        cursor.execute("DELETE FROM channels WHERE id=%s", (channel_id,))
    cursor.execute("DELETE FROM owners WHERE id=%s", (owner_id,))
    EVIL_DB.commit()
    
def get_owner_id(name: str):
    cursor = EVIL_DB.cursor(buffered=True)
    
    cursor.execute("SELECT id FROM owners WHERE name=%s", (name,))
    # if cursor.fetchone() is None:
    #     raise NameError("There is no such owner in database!")
    try:
        owner_id = cursor.fetchone()[0]
    except TypeError:
        raise NameError("There is no such owner in database!")
    
    return owner_id


def get_channel_info(channel_id):#only valid input
    cursor = EVIL_DB.cursor()
    cursor.execute("SELECT owner_id FROM owner_channels WHERE channel_id=%s", (channel_id,))
    owner_id = cursor.fetchone()[0]
    name, comment = get_owner_info(owner_id)
    
    return name, comment

def get_owner_info(owner_id):#only valid input
    cursor = EVIL_DB.cursor()
    
    cursor.execute("SELECT name, comment FROM owners WHERE id=%s", (owner_id,))
    name, comment = cursor.fetchone()
    return name, comment

