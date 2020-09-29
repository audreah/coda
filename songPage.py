'''
Authors: Audrea Huang
Version: Fall T1 2020 | 28 Sept 2022
'''

import cs304dbi as dbi

# ==========================================================
# The functions that do most of the work.

def get_song(conn, sid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select song_id, song_title, genre, user_name,
        artist_name, release_year, album_title from coda_song
        join coda_album using(album_id)
        join coda_artist using(artist_id)
        join coda_user on coda_user.user_id = coda_song.added_by
        where song_id = %s''', [sid])
    return curs.fetchone()

def get_similar_songs(conn, text):
    curs = dbi.dict_cursor(conn)
    userInput = '%' + text + '%'
    curs.execute('''select song_id, song_title from coda_song 
        where song_title COLLATE UTF8_GENERAL_CI LIKE %s''', [userInput])
    return curs.fetchall()

# ==========================================================
# This starts the ball rolling, *if* the file is run as a
# script, rather than just being imported.    

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('coda_db')
    conn = dbi.connect()
    songInfo = get_song(conn, 1)