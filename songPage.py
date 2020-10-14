'''
Authors: Audrea Huang
Version: Fall T1 2020 | 30 Sept 2020
'''

import cs304dbi as dbi
import re

# ==========================================================
# The functions that do most of the work.

def get_song(conn, sid):
    '''
    Get information about a song to display on the song's page.
    :param conn: connection to database
    :param sid: unique song id as an integer
    :returns: one dictionary with the song's title, genre, artist, 
        release year, album, and the user that uploaded it
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_title, genre, display_name,
        artist_name, release_year, album_title, song_id,
        artist_id, album_id, user_id
        from coda_song
        join coda_album using(album_id)
        join coda_artist using(artist_id)
        join coda_user on coda_user.user_id = coda_song.added_by
        where song_id = %s''', [sid])
    return curs.fetchone()

def get_similar_songs(conn, text):
    '''
    Gets the songs whose names are similar to the user's query
    if the query does not return an exact match.
    :param conn: connection to database
    :param text: the user's query as a string
    :returns: all of the songs similar to the user's specification
    '''
    curs = dbi.dict_cursor(conn)
    userInput = '%' + text + '%'
    curs.execute('''select song_id, song_title from coda_song 
        where song_title COLLATE UTF8_GENERAL_CI LIKE %s''', [userInput])
    return curs.fetchall()

def get_genres(conn):
    '''
    Gets all the genres (for both songs and playlists).
    :param conn: connection to database
    :returns: a list of all the genres in the database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct genre from coda_song union (
            select distinct playlist_genre from coda_playlist)''')
    genreDictList = curs.fetchall()
    genresDB = [genreDict['genre'] for genreDict in genreDictList]

    # collect distinct genre names
    genres = []
    for genre in genresDB:
        # some songs/playlists have multiple genres, separated by | or ,
        # separate genres and strip any leading/trailing whitespace
        genres += [oneGenre.strip().lower() 
            for oneGenre in re.split('\||,', genre)
            if oneGenre.strip().lower() not in genres]

    return sorted(genres)

def songs_by_genre(conn, genre):
    '''
    Gets all the songs of a given genre to organize the explore page.
    :param genre: the name of one genre of interest as a string
    :param conn: connection to database
    :returns: a list of dictionaries, where each dictionary has the 
        song id, title, artist, and album for a song in that genre
    '''
    curs = dbi.dict_cursor(conn)
    genre = '%' + genre + '%'
    curs.execute('''select song_id, song_title, 
        artist_name, artist_id, 
        album_title, album_id from coda_song
        join coda_album using(album_id)
        join coda_artist using(artist_id)
        where coda_song.genre like %s''', [genre])
    genreDictList = curs.fetchall()
    return genreDictList

# ==========================================================
# This starts the ball rolling, *if* the file is run as a
# script, rather than just being imported.    

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('coda_db')
    conn = dbi.connect()
    # songInfo = get_song(conn, 1)

    # genres = get_genres(conn)
    # print(genres)

    countrySongs = songs_by_genre(conn, 'Christmas')
    print(countrySongs)
    