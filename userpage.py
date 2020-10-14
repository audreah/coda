# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that searches for user and their information.

def search_user(conn, text):
    """
    Searches in database where the user display name is similar to input text.

    Parameters
    ----------
    conn: connection to database
    text, string
        user input text from search bar
    
    Returns
    -------
    A list of dictionaries containing user information for display names
    similar to the user's query
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where display_name like %s''', 
                    ['%' + text + '%'])
    return curs.fetchall()

def get_user_from_id(conn, user_id):
    '''
    Retrieves user information given an id.
    :param conn: connection to database
    :param user_id: int | unique id for user
    :returns: a dictionary with that user's information
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id = %s''', [user_id])
    return curs.fetchone()

def get_userid_from_username(conn, username):
    '''
    Retrieves user id where the username is specific to CAS log in.
    :param conn: connection to database
    :param username: str | CAS log in user name (wellesley user name)
    :returns: int | user id
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select user_id from coda_user where username = %s''', 
        [username])
    return curs.fetchone()['user_id']

def check_username(conn, username):
    '''
    Checks if user with username exist in our database.
    :param conn: connection to databases
    :param username: str | CAS login username
    :returns:
        True if the indicated username does not exist in the database
        False if the indicated username exists
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select count(username) from coda_user where username = %s''',
        [username])
    result = curs.fetchone()

    return result['count(username)'] == 0

def add_user(conn, username):
    '''
    Add user if user is not in our coda database. 
    At first, the display name will automatically be the same as the username,
    but the user can change this later.
    :param comm: connection to database
    :param username: str | CAS login user name (wellesley user name)
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_user(username, display_name) 
        values (%s, %s)''', [username, username])
    conn.commit()

def get_friends(conn, user_id):
    """
    Retrieves users that a specific user is following on coda.

    :param conn: connection to database
    :param user_id: int | unique user id
    :returns: a list of dictionaries with information about the friend
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id in
        (select friend_two from coda_friend where friend_one = %s)''', 
        [user_id])
    return curs.fetchall()

def get_user_playlists(conn, user_id):
    """
    Retrieves all playlists of a user, given their unique user id.

    :param conn: connection to database
    :param user_id: integer representing unique user id
    :returns: a list of dictionaries with information for playlists 
        created by the user
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where created_by = %s''',
        [user_id])
    return curs.fetchall()

def get_playlist(conn, playlist_id):
    """
    Retrieves information of a playlist given its unique playlist id.

    :param conn: connection to database
    :param playlist_id: integer representing unique playlist id
    :returns: a dictionary with the specified playlist information
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where playlist_id = %s''',
        [playlist_id])
    return curs.fetchone()

def update_username(conn, user_id, newName):
    """
    Allows user to update their own display name on web page.

    :param conn: connection to database
    :param user_id: integer representing unique user id
    :param newName: string for new display name
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''update coda_user set display_name = %s 
        where user_id = %s''', [newName, user_id])
    conn.commit()

def add_artist(conn, artist_name):
    """
    Allows user to add artist to coda database.

    :param conn: connection to database
    :param artist_name: text input of artist name
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_artist(artist_name) values (%s)''', 
        [artist_name])
    conn.commit()

def add_album(conn, album_title, artist_name):
    """
    Allows user to add album to coda database.

    :param conn: connection to database
    :param album_title: text input of album title
    :param artist_name: text input of artist name
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_album(album_title,artist_id)
        values (%s, (
            select artist_id from coda_artist where artist_name = %s
        ))''', 
        [album_title, artist_name])
    conn.commit()

def add_song(conn, song_title, genre, album_title, added_by):
    ''' 
    Adds a song to the database

    :param conn: connection to db
    :param song_title: str | title of the song to be added
    :param genre: str | genre of the song to be added
    :param album_title: str | title of the album in which this song appears
    :param added_by: int | user id of the logged-in user
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_song(song_title,genre,album_id, added_by)
        values (%s, %s, 
        (select album_id from coda_album where album_title = %s),
        (select user_id from coda_user where username = %s))''',
        [song_title, genre, album_title, added_by])
    conn.commit()

def get_artistId(conn, artist_name):
    """
    Retrieves artist id if artist already exists in database.

    :param conn: connection to database
    :param artist_name: text input of artist name
    :returns: int | id of the specified artist
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('select artist_id from coda_artist where artist_name = %s', 
        [artist_name])
    return curs.fetchone()

def check_artist(conn, artist_name):
    """
    Checks if an artist exists in the database.

    :param conn: connection to database
    :param artist_name: str | artist's name
    :returns: bool
        True if no artist with the name exists in database
        False if an artist with the name exists
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select count(artist_id) from coda_artist 
        where artist_name = %s''', [artist_name])
    result = curs.fetchone()
    return result['count(artist_id)'] == 0

def check_song(conn, song_title, album_name):
    """
    Checks if a song on the album exists in the database.

    :param conn: connection to database
    :param song_title: str | title of song
    :param album_name: str | title of album where this song appears
    :returns: bool
        True if no song with the title exists in database
        False if a song with the title exists
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select count(song_id) from coda_song where song_title = %s 
        and album_id = 
        (select album_id from coda_album where album_title = %s)''',
        [song_title, album_name])
    result = curs.fetchone()
    return result['count(song_id)'] == 0

def check_album(conn, album_title, artist_name):
    """
    Checks if an album by the artist exists in the database.

    :param conn: connection to database
    :param album_title: str | title of album
    :param artist_name: str | name of artist who released the album
    :returns: bool
        True if no album with the title exists in database
        False if an album with the title exists
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select count(album_id) from coda_album where album_title = %s 
        and artist_id = 
        (select artist_id from coda_artist where artist_name = %s)''',
        [album_title, artist_name])
    result = curs.fetchone()
    return result['count(album_id)'] == 0

def add_follow(conn,friendId,currentId):
    '''
    Allows the current user to follow another user

    :param conn: connection to database
    :param friendId: the uid of the person to be followed
    :param currentId: the uid of the person doing the following
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into coda_friend (friend_one,friend_two)
            values (%s,%s)'''
    curs.execute(sql,[currentId,friendId])
    conn.commit()
    