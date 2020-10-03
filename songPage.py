'''
Authors: Audrea Huang
Version: Fall T1 2020 | 30 Sept 2020
'''

import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.

'''
Get information about a song to display on the song's page.
:param conn: connection to database
:param sid: unique song id
:returns: the song's title, genre, artist, release year, album,
    and the user that uploaded it
'''
def get_song(conn, sid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id, song_title, genre, user_name,
        artist_name, release_year, album_title from coda_song
        join coda_album using(album_id)
        join coda_artist using(artist_id)
        join coda_user on coda_user.user_id = coda_song.added_by
        where song_id = %s''', [sid])
    return curs.fetchone()

'''
Gets the songs whose names are similar to the user's query
if the query does not return an exact match.
:param conn: connection to database
:param text: the user's query
:returns: all of the songs similar to the user's specification
'''
def get_similar_songs(conn, text):
    curs = dbi.dict_cursor(conn)
    userInput = '%' + text + '%'
    curs.execute('''select song_id, song_title from coda_song 
        where song_title COLLATE UTF8_GENERAL_CI LIKE %s''', [userInput])
    return curs.fetchall()

'''
Gets all the genres (for both songs and playlists).
:param conn: connection to database
:returns: all of the genres in the database
'''
def get_genres(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select distinct genre from coda_song union (
            select distinct playlist_genre from coda_playlist)''')
    genreDictList = curs.fetchall()
    return [genreDict['genre'] for genreDict in genreDictList]

'''
Gets all the songs of a given genre to organize the explore page.
:param genre: one genre of interest
:param conn: connection to database
:returns: all the song ids, titles, artists, and albums grouped by genre
'''
def songs_by_genre(conn, genre):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id, song_title, 
        artist_name, album_title from coda_song
        join coda_album using(album_id)
        join coda_artist using(artist_id)
        where coda_song.genre = %s''', [genre])
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

    countrySongs = songs_by_genre(conn, 'Country')
    print(countrySongs)
    