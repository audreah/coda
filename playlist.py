'''
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


def updatePlaylist(conn,pName,pid):
    curs = dbi.cursor(conn)
    sql = '''update coda_playlist
            set playlist_name = %s 
            where playlist_id = %s'''
    curs.execute(sql,[pName,pid])
    conn.commit()

