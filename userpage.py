# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that searches for user and their information.

def search_user(conn, text):
    """
    Searches in database where the user name is similar to input text.

    :param conn: connection to database
    :param text: user input text from search bar
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where display_name like %s''', 
                    ['%' + text + '%'])
    return curs.fetchall()

def get_user_id(conn, user_id):
    """
    Retrieves information of a user given their unique user id.

    :param conn: connection to database
    :param user_id: integer representing unique user id
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id = %s''', [user_id])
    return curs.fetchone()

def get_friends(conn, user_id):
    """
    Retrieves users that a specific user is following on coda.

    :param conn: connection to database
    :param user_id: integer representing unique user id
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id in
    (select friend_two from coda_friend where friend_one = %s)''', [user_id])
    return curs.fetchall()

def get_user_playlists(conn, user_id):
    """
    Retrieves all playlists of a user, given their unique user id.

    :param conn: connection to database
    :param user_id: integer representing unique user id
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where created_by = %s''', [user_id])
    return curs.fetchall()

def get_playlist(conn, playlist_id):
    """
    Retrieves information of a playlist given its unique playlist id.

    :param conn: connection to database
    :param playlist_id: integer representing unique playlist id
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where playlist_id = %s''', [playlist_id])
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
    values (%s, (select artist_id from coda_artist where artist_name = %s))''', 
        [album_title, artist_name])
    conn.commit()

def add_song(conn, song_title, genre, album_title):
    ''' When session/log in is working add user_id '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_song(song_title,genre,album_id)
    values (%s, %s, 
    (select album_id from coda_album where album_title = %s))''',
    [song_title, genre, album_title])
    conn.commit()

def get_artistId(conn, artist_name):
    """
    Retrieves artist id if artist already exists in database.

    :param conn: connection to database
    :param artist_name: text input of artist name
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select artist_id from coda_artist where artist_name = %s''', 
        [artist_name])
    return curs.fetchone()

def check_artist(conn, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_name = %s''', 
        [artist_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if no artist with the name exist in database'''
        return True
    return False

def check_song(conn, song_title, album_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id from coda_song where song_title = %s 
        and album_id = 
        (select album_id from coda_album where album_title = %s))''',
        [song_title, album_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if song does not already exist in database'''
        return True
    return False

def check_album(conn, album_title, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select album_id from coda_album where album_title = %s 
        and artist_id = 
        (select artist_id from coda_artist where artist_name = %s)''',
        [album_title, artist_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if album does not exist in database'''
        return True
    return False