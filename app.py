from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import pymysql
import cs304dbi as dbi

# import cs304dbi_sqlite3 as dbi

import random, playlist, albumPage, songPage, userpage

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    return render_template('main.html',title='Hello')


@app.route('/search/')
def search():
    conn  = dbi.connect()
    value = request.args.get("searchbar")
    users = userpage.search_user(conn, value)
    print(users)
    if users:
        return render_template("search.html", users = users)

'''
Displays name, genre, and creator for a playlist, along with all the
songs that have been added to the playlist
'''
@app.route('/playlist/<int:pid>', methods=["GET", "POST"]) 
def playlistPage(pid):
    conn = dbi.connect()
    # TODO: implement search functionality to search for playlists
    playlistInfo = playlist.get_playlist_info(conn,pid)
    nestedSongs = playlist.get_playlist_songs(conn,pid)
    if playlistInfo == None: # playlist not found
        return render_template('notFound.html',
            type='No playlist', page_title="Playlist Not Found")
    else: # playlist found
        if (request.method == "GET"):
            return render_template('playlist.html', 
                            playlistInfo=playlistInfo, 
                            songs=nestedSongs, 
                            page_title=playlistInfo['playlist_name'])
        else: #update playlist
            submitType = request.form.get('submit')

            if (submitType == 'update'): 
                newName = request.form.get('playlist-name')
                newGenre = request.form.get('playlist-genre')

                oldName = playlistInfo["playlist_name"]
                pUser = playlistInfo["user_name"]
                uid = playlistInfo["created_by"]
                pid = playlistInfo["playlist_id"]

                #Check if we are changing the name of the playlsit
                if oldName == newName:
                    playlist.updatePlaylist(conn,pid,newName,newGenre)
                    playlistInfo = playlist.get_playlist_info(conn,pid)
                    flash(newName + '  was updated successfully')
                        
                    return render_template('playlist.html', 
                                playlistInfo=playlistInfo, 
                                songs=nestedSongs, 
                                page_title=playlistInfo['playlist_name'])
                else:
                    #There cannot be multiple playlists with the same name
                    if playlist.check_unique_playlist_name(conn, newName, uid):
                        playlist.updatePlaylist(conn,pid,newName,newGenre)
                        playlistInfo = playlist.get_playlist_info(conn,pid)
                        flash(newName + '  was updated successfully')
                        
                        return render_template('playlist.html', 
                                playlistInfo=playlistInfo, 
                                songs=nestedSongs, 
                                page_title=playlistInfo['playlist_name'])
                    else:
                        flash('Error: A playlist with this name already exists')

                        return render_template('playlist.html', 
                                playlistInfo=playlistInfo, 
                                songs=nestedSongs, 
                                page_title=playlistInfo['playlist_name'])


@app.route('/user/<user_id>')
def user(user_id):
    conn = dbi.connect()
    user = userpage.get_user_id(conn, user_id)
    friendsList = userpage.get_friends(conn, user_id)
    playlists = userpage.get_user_playlists(conn, user_id)
    return (render_template("user.html", user= user, friendsList = friendsList, playlists = playlists))

''' 
This is the route for album lookups. It renders a template 
with information about the artist and songs in it.

:param pid: a unique album id from the coda_album table
:returns: not found page if album does not exist in the database
          the desired album's indiviual page otherwise
'''
@app.route('/album/<int:aid>', methods=["GET", "POST"])
def album(aid):
    conn = dbi.connect()
    albumInfo = albumPage.get_album(conn, aid)
    songs = albumPage.get_songs(conn, aid)

    if albumInfo == None: # album not found
        return render_template('notFound.html',
            type='No album', page_title="Album Not Found")
    else: # album found
        return render_template('album.html', 
            albumDescription=albumInfo,
            songs=songs,
            page_title='Album | ' + albumInfo['album_title'])

''' 
This is the route for song lookups. It renders a template 
with the artist's name and the title of the album on which album it appears.

:param sid: a unique song id from the coda_song table
:returns: not found page if song does not exist in the database
          the desired page for that song otherwise
'''
@app.route('/song/<int:sid>')
def song(sid):
    conn = dbi.connect()
    song_info = songPage.get_song(conn, sid)

    if song_info == None: # song not found
        return render_template('notFound.html',
            type='No song', page_title="Song Not Found")
    else: # song found
        return render_template('song.html', 
            song=song_info,
            page_title='Song | ' + song_info['song_title'])

'''
Renders the template for the user's search.
:returns: the item's (album, song, or user) individual page if there is
          exactly one match
          otherwise, lists out all matches with links to their individual pages.
'''
@app.route('/query/', methods=['GET'])
def query():
    conn = dbi.connect()
    query = request.args['searchbar'] # query text
    albumMatches = albumPage.get_similar_albums(conn,query)
    songMatches = songPage.get_similar_songs(conn,query)
    userMatches = userpage.search_user(conn, query)

    # no matches
    if not albumMatches and not songMatches and not users:
        return render_template('notFound.html', type='Nothing',
        page_title="No matches")
    # one album matches
    elif len(albumMatches) == 1 and not songMatches and not users:
        return redirect(url_for('album', aid=albumMatches[0]['album_id']))
    # one song matches
    elif len(songMatches) == 1 and not users:
        return redirect(url_for('song', sid=songMatches[0]['song_id']))
    
    elif userMatches and not songMatches and not albumMatches:
        return render_template("search.html", users = users)

    # multiple matches
    else:
        # get the ids for each album and song that matches the query
        albums = []
        for albumDict in albumMatches:
            albumID = albumDict['album_id']
            albums.append(albumPage.get_album(conn, albumID))  

        songs = []
        for songDict in songMatches:
            songID = songDict['song_id']
            songs.append(songPage.get_song(conn, songID))

        users = []
        for userDict in userMatches:
            userID = userDict['user_id']
            users.append(userpage.get_user_id(conn, userID))

        return render_template('multiple.html', 
            albums=albums, songs=songs, users=users,
            name = query,
            page_title="Mutliple Results Found")


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('coda_db')

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
