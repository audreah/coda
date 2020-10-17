'''
Authors: Danya Gao
Gets album images from the coda_db database
'''

import cs304dbi as dbi

def get_image_by_album(conn,aid):
    '''
    Get the image associated with an album

    :param conn: connection to db
    :param aid: the album id
    :returns: the image information for that album 
    '''
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute('''select album_id,album_title,filename
                    from picfile inner join coda_album using (album_id)
                    where album_id = %s''',[aid])
    if numrows == 0:
        return False
    return curs.fetchone()

if __name__ == '__main__':
    dbi.cache_cnf()   # defaults to ~/.my.cnf
    dbi.use('coda_db')
    conn = dbi.connect()
    print(get_playlist_song_ids(conn, 3))
