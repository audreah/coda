# Liz Huang, Audrea Huang, Danya Gao
# Coda Project

import cs304dbi as dbi;

# ==========================================================
# The functions that do the queries for retrieving artists.

def search_artist(conn, text):
    '''
    Retrieves all artist names that are similar to input text.

    :param conn: connection to database
    :param text: user search input as a string
    :returns: a list of dictionaries with the relevant artist information
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_name like %s''',
        ['%' + text + '%'])
    return curs.fetchall()

def get_artist_albums(conn, artist_id):
    '''
    Retrieves all albums of a specific artist.

    :param conn: connection to database
    :param artist_id: unique artist id as an integer
    :returns: a list of dictionaries containing album information
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_album where artist_id = %s''', 
        [artist_id])
    return curs.fetchall()

def get_album_song(conn, album_id):
    '''
    Retrieves all songs that are in a particular album.

    :param conn: connection to database
    :param album_id: unique album id as an integer
    :returns: a list of dictionaries containing song information
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_song where album_id = %s''', [album_id])
    return curs.fetchall()

def get_artist(conn, artist_id):
    '''
    Retrieves a specific artist.

    :param conn: connection to database
    :param artist_id: unique artist id as an integer
    :returns: a single dictionary containing the artist's information
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select * from coda_artist where artist_id = %s''', 
        [artist_id])
    return curs.fetchone()
