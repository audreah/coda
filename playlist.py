'''
Authors: Danya Gao, Audrea Huang
Gets information about playlists from the coda_db database
'''

import cs304dbi as dbi

'''
Given a connection object and playlist id, gets the name, 
genre, and creator of that playlist
'''
def get_playlist_info(conn,pid):
    curs = dbi.dict_cursor(conn)
    sql = '''select playlist_name, playlist_genre, user_name, playlist_id, created_by
            from coda_playlist 
            inner join coda_user on 
                (coda_user.user_id = coda_playlist.created_by)
            where playlist_id = %s'''
    curs.execute(sql,[pid])
    return curs.fetchone()

'''                                                                             
Returns the playlists whose names are similar to the user's query
if the query does not return one direct result.
:param conn: connection to database
:param query: playlist name that the user specifies     
'''
def get_similar_playlists(conn,query):
    curs = dbi.dict_cursor(conn)                                              
    userInput = '%' + query + '%'
    curs.execute('''select playlist_id, playlist_name from coda_playlist         
        where playlist_name COLLATE UTF8_GENERAL_CI LIKE %s''', [userInput])
    return curs.fetchall()

'''
Given a connection object and playlist id, gets the songs 
in that playlist
'''
def get_playlist_songs(conn,pid):
    curs = dbi.dict_cursor(conn)
    sql = '''select song_title, song_id 
            from coda_song 
                inner join coda_playlist_songs using (song_id)
            where playlist_id = %s'''
    curs.execute(sql,[pid])
    return curs.fetchall()

'''
Given a connection object, a playlist name, and a user id,
check if the user already has a playlist with that name
'''
def check_unique_playlist_name(conn,pName, uid):
    curs = dbi.cursor(conn)
    sql = '''select count(playlist_name)
            from coda_playlist 
            where playlist_name = %s and created_by = %s'''
    curs.execute(sql,[pName,uid])
    res = curs.fetchall()
    if res[0][0] == 0:
        return True
    return False


def updatePlaylist(conn,pid,newName,newGenre):
    curs = dbi.cursor(conn)
    sql = '''update coda_playlist
            set playlist_name = %s, playlist_genre = %s
            where playlist_id = %s'''
    curs.execute(sql,[newName,newGenre,pid])
    conn.commit()

'''
Gets all the playlists of a given genre to organize the explore page.
:param genre: one genre of interest
:param conn: connection to database
:returns: all the song ids grouped by genre
'''
def playlists_by_genre(conn, genre):
    curs = dbi.dict_cursor(conn)
    curs.execute('''select playlist_id, playlist_name from coda_playlist
        where playlist_genre = %s''', [genre])
    genreDictList = curs.fetchall()
    return genreDictList

'''
(temporary) Get all the playlists in the db so we can add songs to them.

:param conn: connection to db
:returns: the names and ids of all playlists
'''
def get_playlists(conn):
    curs = dbi.dict_cursor(conn)
    curs.execute('select playlist_id, playlist_name from coda_playlist')
    playlistDictList = curs.fetchall()
    return playlistDictList
