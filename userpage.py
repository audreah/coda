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