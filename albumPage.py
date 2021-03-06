'''
Authors: Audrea Huang
Version: Fall T1 2020 | 17 Oct 2020
Extract information from coda_db relevant to albums
'''

import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.

def get_album(conn, aid):
    ''' 
    Extracts the relevant album title, release year, and artist name
    for the specified album.

    :param conn: connection to database
    :param aid: a unique id from the album table
    :returns: a dictionary with the album's id, title, release year,
        and artist's id and name
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select album_id, album_title, artist_name,
        release_year, artist_id from coda_album
        join coda_artist using(artist_id)
        where album_id = %s''', [aid])
    return curs.fetchone()

def multiple_albums(conn, aid_list):
    ''' 
    Get a list of all the albums with ids in the provided list.
    This prevents us from needing to execute queries in a loop.

    :param conn: connection to database
    :param aid_list: int[] with ids for specified albums
    :returns: a list of dictionaries with album information for
        the requested albums
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select album_id, album_title, artist_name,
        release_year, artist_id from coda_album
        join coda_artist using(artist_id)
        where album_id in %s''', [aid_list])
    return curs.fetchall()

def get_songs(conn, aid):
    ''' 
    Get the songs on this album.

    :param conn: connection to database
    :param aid: a unique id from the album table
    :returns: a list of dictionaries for song ids and titles on the album
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id, song_title from coda_song
        where album_id = %s''', [aid])
    return curs.fetchall()

def get_similar_albums(conn, text):
    ''' 
    Get a list of all the albums with names similar to the user's search.

    :param conn: connection to database
    :param text: string with user's input to indicate person of interest
    '''
    curs = dbi.dict_cursor(conn)
    userInput = '%' + text + '%'
    curs.execute('''select album_id, album_title from coda_album 
        where album_title LIKE %s''', [userInput])
    return curs.fetchall()

# ==========================================================
# This starts the ball rolling, *if* the file is run as a
# script, rather than just being imported.    

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('coda_db')
    conn = dbi.connect()
