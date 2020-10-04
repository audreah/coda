# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that do the queries for retrieving artists.
'''
Retrieves all artist names that are similar to input text.

:param conn: connection to database
:param text: user search input
'''
def search_artist(conn, text):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_name like %s''',
        ['%' + text + '%'])
    return curs.fetchall()

'''
Retrieves all albums of a specific artist.

:param conn: connection to database
:param artist_id: unique artist id
'''
def get_artist_albums(conn, artist_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_album where artist_id = %s''', [artist_id])
    return curs.fetchall()

'''
Retrieves all songs that are in a particular album.

:param conn: connection to database
:param album_id: unique album id
'''
def get_album_song(conn, album_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_song where album_id = %s''', [album_id])
    return curs.fetchall()

'''
Retrieves a specific artist.

:param conn: connection to database
:param artist_id: unique artist id
'''
def get_artist(conn, artist_id):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_id = %s''', [artist_id])
    return curs.fetchone()