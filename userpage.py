# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that searches for user and their information.

"""
    Searches in database where the user name is similar to input text.

    :param conn: connection to database
    :param text: user input text from search bar
"""
def search_user(conn, text):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_name like %s''', 
                    ['%' + text + '%'])
    return curs.fetchall()

"""
    Retrieves information of a user given their unique user id.

    :param conn: connection to database
    :param user_id: integer representing unique user id
"""
def get_user_id(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id = %s''', [user_id])
    return curs.fetchone()

"""
    Retrieves users that a specific user is following on coda.

    :param conn: connection to database
    :param user_id: integer representing unique user id
"""
def get_friends(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id in
    (select friend_two from coda_friend where friend_one = %s)''', [user_id])
    return curs.fetchall()

"""
    Retrieves all playlists of a user, given their unique user id.

    :param conn: connection to database
    :param user_id: integer representing unique user id
"""
def get_user_playlists(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where created_by = %s''', [user_id])
    return curs.fetchall()

"""
    Retrieves information of a playlist given it's unique playlist id.

    :param conn: connection to database
    :param playlist_id: integer representing unique playlist id
"""
def get_playlist(conn, playlist_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where playlist_id = %s''', [playlist_id])
    return curs.fetchone()

"""
    Allows user to update their own user name on web page.

    :param conn: connection to database
    :param usesr_id: integer representing unique user id
    :param newName: string for new user name
"""
def update_username(conn, user_id, newName):
    curs = dbi.dict_cursor(conn)
    curs.execute('''update coda_user set user_name = %s 
    where user_id = %s''', [newName, user_id])
    conn.commit()

"""
    Allows user to add artist to coda database.

    :param conn: connection to database
    :param artist_name: text input of artist name
"""
def add_artist(conn, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_artist(artist_name) values (%s)''', [artist_name])
    conn.commit()

"""
    Allows user to add album to coda database.

    :param conn: connection to database
    :param album_title: text input of album title
    :param artist_name: text input of artist name
"""
def add_album(conn, album_title, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_album(album_title,artist_id)
    values (%s, (select artist_id from coda_artist where artist_name = %s))''', [album_title, artist_name])
    conn.commit()

'''when session/log in is working add user_id'''
def add_song(conn, song_title, genre, album_title, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''insert into coda_song(song_title,genre,album_id,added_by)
    values (%s, %s, 
    (select album_id from coda_album where album_title = %s 
    and artist_id = (select artist_id from coda_artist where artist_name = %s)));''',
    [song_title, genre, album_title, artist_name])
    conn.commit()

"""
    Retrieves artist id if artist already exists in database.

    :param conn: connection to database
    :param artist_name: text input of artist name
"""
def get_artistId(conn, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select artist_id from coda_artist where artist_name = %s''', [artist_name])
    return curs.fetchone()

def check_artist(conn, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_name = %s''', [artist_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if no artist with the name exist in database'''
        return True
    return False

def check_song(conn, song_title, album_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id from coda_song where song_title = %s and album_id = 
    (select album_id from coda_album where album_title = %s))''',
    [song_title, album_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if song does not already exist in database'''
        return True
    return False

def check_album(conn, album_title, artist_name):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select album_id from coda_album where album_title = %s and artist_id = 
    (select artist_id from coda_artist where artist_name = %s)''',
    [album_title, artist_name])
    result = curs.fetchone()
    if result == 0:
        '''returns true if album does not exist in database'''
        return True
    return False