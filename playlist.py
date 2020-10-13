'''
Authors: Danya Gao, Audrea Huang
Gets information about playlists from the coda_db database
'''

import cs304dbi as dbi

def get_playlist_info(conn,pid):
    """
    Given a connection object and playlist id, gets the name, 
    genre, and creator of that playlist

    :param conn: connection to database
    :param pid: integer indicating unique playlist id
    :returns: a single dictionary containing the playlist's name, genre, id,
        and the id and name of the user who created it
    """
    curs = dbi.dict_cursor(conn)
    sql = '''select playlist_name, playlist_genre, display_name, playlist_id, 
            created_by from coda_playlist 
            inner join coda_user on 
                (coda_user.user_id = coda_playlist.created_by)
            where playlist_id = %s'''
    curs.execute(sql,[pid])
    return curs.fetchone()

def get_all_playlists_by_user(conn,username):
    """
    Given a connection object and a uid, return all playlists in the database created by 
    that user
    """
    curs = dbi.dict_cursor(conn)
    sql = '''select * from coda_playlist
            where created_by = (select user_id from coda_user where username = %s)'''
    curs.execute(sql,[username])
    return curs.fetchall()

def get_similar_playlists(conn,query):
    """                                                                         
    Returns the playlists whose names are similar to the user's query
    if the query does not return one direct result.

    :param conn: connection to database
    :param query: string indicating playlist name that the user specifies     
    """
    curs = dbi.dict_cursor(conn)                                              
    userInput = '%' + query + '%'
    curs.execute('''select playlist_id, playlist_name from coda_playlist         
        where playlist_name LIKE %s''', [userInput])
    return curs.fetchall()

def get_playlist_songs(conn,pid):
    """
    Given a connection object and integer playlist id, gets the songs 
    in that playlist
    """
    curs = dbi.dict_cursor(conn)
    sql = '''select song_title, song_id 
            from coda_song 
                inner join coda_playlist_songs using (song_id)
            where playlist_id = %s'''
    curs.execute(sql,[pid])
    return curs.fetchall()

def check_unique_playlist_name(conn,pName, username):
    """
    Given a connection object, a playlist name, and a user id,
    checks if the user already has a playlist with that name
    """
    curs = dbi.cursor(conn)
    sql = '''select count(playlist_name)
            from coda_playlist 
            where playlist_name = %s and created_by = (select user_id from coda_user where username = %s)'''
    curs.execute(sql,[pName,username])
    res = curs.fetchall()
    if res[0][0] == 0:
        return True
    return False

def updatePlaylist(conn,pid,newName,newGenre):
    """
    Given a connection object, a playlist id, a new name,
    and a new genre, update the playlist

    :param conn: connection to database
    :param pid: integer representing unique playlist it
    :param newName: string for new playlist name
    :param newGenre: string for new genre name for this playlist
    """
    curs = dbi.cursor(conn)
    sql = '''update coda_playlist
            set playlist_name = %s, playlist_genre = %s
            where playlist_id = %s'''
    curs.execute(sql,[newName,newGenre,pid])
    conn.commit()

def createPlaylist(conn,name,genre,user):
    """
    Given a connection object, a playlist name, genre,
    and a user id, create a playlist

    :param conn: database connection
    :param name: string with playlist name
    :param genre: string with genre name
    :param user: CAS session user name
    """
    curs = dbi.cursor(conn)
    sql = '''insert into coda_playlist
                        (playlist_name,playlist_genre,created_by)
             values (%s,%s,(select user_id from coda_user where username = %s))'''
    curs.execute(sql,[name,genre,user])
    conn.commit()

def deletePlaylist(conn,pid):
    """
    Given a connection object and a playlist id, 
    delete the playlist

    :param conn: database connection
    :param pid: integer for playlist id
    """
    curs = dbi.cursor(conn)
    sql = '''delete from coda_playlist
                    where playlist_id = %s'''
    curs.execute(sql,[pid])
    conn.commit()

def addSongToPlaylist(conn,pid,sid):
    ''' 
    Given a connection object, a song id, and a playlist id, 
    add that song to the playlist

    :param conn: database connection
    :param pid: integer for playlist id
    :param sid: integer for song id
    '''
    curs = dbi.cursor(conn)
    sql = '''insert into coda_playlist_songs(playlist_id,song_id)
            values (%s,%s)'''
    curs.execute(sql,[pid,sid])
    conn.commit()

def playlists_by_genre(conn, genre):
    """  
    Gets all the playlists of a given genre to organize the explore page.
    :param genre: one genre of interest
    :param conn: connection to database
    :returns: all the song ids grouped by genre
    """
    curs = dbi.dict_cursor(conn)
    curs.execute('''select playlist_id, playlist_name from coda_playlist
        where playlist_genre = %s''', [genre])
    genreDictList = curs.fetchall()
    return genreDictList

'''
Get all the playlists by a user that contain a specific song

:param conn: connection to db
:param uid: a user id
:param sid: a song id
:returns: the playlists that contain a song by that user 
'''
def get_playlists_with_song(conn,uid,sid):
    curs = dbi.dict_cursor(conn)
    sql = ('''select playlist_id, playlist_name from coda_playlist 
                    inner join coda_playlist_songs 
                    using (playlist_id) 
                    where created_by = %s and song_id = %s''')
    curs.execute(sql,[uid,sid])
    playlistDictList = curs.fetchall()
    return playlistDictList

'''
Get all the playlists by a user that don't contain a specific song

:param conn: connection to db
:param uid: a user id
:param sid: a song id
:returns: the playlists that contain a song by that user 
'''
def get_playlists_without_song(conn,uid,sid):
    curs = dbi.dict_cursor(conn)
    sql = ('''select playlist_id, playlist_name
            from coda_playlist
            where created_by = %s 
            and playlist_id not in (
                select playlist_id
                from coda_playlist_songs
                where song_id = %s);''')
    curs.execute(sql,[uid,sid])
    playlistDictList = curs.fetchall()
    return playlistDictList
