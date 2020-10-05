# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that searches for user and their information.

def search_user(conn, text):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_name like %s''', 
                    ['%' + text + '%'])
    return curs.fetchall()

def get_user_id(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id = %s''', [user_id])
    return curs.fetchone()

def get_friends(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_user where user_id = 
    (select friend_two from coda_friend where friend_one = %s)''', [user_id])
    return curs.fetchall()

def get_user_playlists(conn, user_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where created_by = %s''', [user_id])
    return curs.fetchall()

def get_playlist(conn, playlist_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_playlist where playlist_id = %s''', [playlist_id])
    return curs.fetchone()
