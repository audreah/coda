'''
Authors: Audrea Huang
Version: Fall T1 2020 | 28 Sept 2022
'''

import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.

''' 
Extracts the relevant name, birthdate, and id for the
specified person.

:param conn: connection to database
:param pid: a unique id from the person table
'''
def get_album(conn, aid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select album_id, album_title,artist_name,release_year from coda_album
        join coda_artist using(artist_id)
        where album_id = %s''', [aid])
    return curs.fetchone()

''' 
Get the songs on this album.

:param conn: connection to database
:param pid: a unique id from the person table
:returns: a list of dictionaries for songs on the album
'''
def get_songs(conn, aid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id, song_title from coda_song
        where album_id = %s''', [aid])
    return curs.fetchall()

''' 
Get a list of all the albums with names similar to the user's search.

:param conn: connection to movie database
:param text: user's input to indicate person of interest
'''
def get_similar_albums(conn, text):
    curs = dbi.dict_cursor(conn)
    userInput = '%' + text + '%'
    curs.execute('''select album_id, album_title from coda_album 
        where album_title COLLATE UTF8_GENERAL_CI LIKE %s''', [userInput])
    return curs.fetchall()

# ==========================================================
# This starts the ball rolling, *if* the file is run as a
# script, rather than just being imported.    

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('coda_db')
    conn = dbi.connect()
