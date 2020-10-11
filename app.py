'''
Authors: Danya Gao, Audrea Huang, Liz Huang
File description: main driver application
'''

from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import pymysql
import cs304dbi as dbi

# import cs304dbi_sqlite3 as dbi

import random, playlist, albumPage, songPage, userpage, re, artistPage

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# set up CAS
from flask_cas import CAS

CAS(app)

app.config['CAS_SERVER'] = 'https://login.wellesley.edu:443'
app.config['CAS_LOGIN_ROUTE'] = '/module.php/casserver/cas.php/login'
app.config['CAS_LOGOUT_ROUTE'] = '/module.php/casserver/cas.php/logout'
app.config['CAS_VALIDATE_ROUTE'] = '/module.php/casserver/serviceValidate.php'
app.config['CAS_AFTER_LOGIN'] = 'logged_in'
app.config['CAS_AFTER_LOGOUT'] = 'after_logout'

@app.route('/logged_in/')
def logged_in():
    """ Redirects to the explore page if logged in. """
    flash('successfully logged in!')
    return redirect( url_for('explore') )

@app.route('/')
def index():
    """ Prompts the user to login. """
    return render_template('login.html')

@app.route('/after_logout/')
def after_logout():
    flash('successfully logged out!')
    return redirect( url_for('index') )

@app.route('/explore/')
def explore():
    """ 
    This is the home page, listing out the genres currently existing
    in our database and allowing the user to search for a song, album,
    playlist, artist, or user. 
    """

    # acquire session information
    print('Session keys: ',list(session.keys()))
    for k in list(session.keys()):
        print(k,' => ',session[k])
    if '_CAS_TOKEN' in session:
        token = session['_CAS_TOKEN']
    if 'CAS_ATTRIBUTES' in session:
        attribs = session['CAS_ATTRIBUTES']
        print('CAS_attributes: ')
        for k in attribs:
            print('\t',k,' => ',attribs[k])
    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')
    
    # extract genre information from the database to display
    conn = dbi.connect()
    # might have multiple genres for one song
    genresDB = songPage.get_genres(conn) 
    genres = []
    for genre in genresDB:
        # separate genres and strip any leading/trailing whitespace
        genres += [oneGenre.strip().lower() 
            for oneGenre in re.split('\||,', genre)
            if oneGenre.strip().lower() not in genres]
    return render_template('main.html',title='Home',genres=sorted(genres),
                           username=username,
                           is_logged_in=is_logged_in,
                           cas_attributes = session.get('CAS_ATTRIBUTES'))

@app.route('/playlist/<int:pid>', methods=["GET", "POST"]) 
def playlistPage(pid):
    '''
    Displays name, genre, and creator for a playlist, along with all the
    songs that have been added to the playlist.

    Takes a unique playlist id as a parameter and returns that playlist's
    page if found, the not found page if no playlist exists with that id,
    or the profile page of the user who created that playlist if it is
    deleted.
    '''
    conn = dbi.connect()
    playlistInfo = playlist.get_playlist_info(conn,pid)
    nestedSongs = playlist.get_playlist_songs(conn,pid)

    if playlistInfo == None: # playlist not found
        return render_template('notFound.html',
            type='No playlist', page_title="Playlist Not Found")
    
    # playlist found
    if (request.method == "GET"):
        return render_template('playlist.html', 
                        playlistInfo=playlistInfo, 
                        songs=nestedSongs, 
                        page_title=playlistInfo['playlist_name'])
    else: #POST request
        submitType = request.form.get('submit')
        oldName = playlistInfo["playlist_name"]
        uid = playlistInfo["created_by"]

        if (submitType == 'update'): #update playlist
            newName = request.form.get('playlist-name')
            newGenre = request.form.get('playlist-genre')

            pUser = playlistInfo["user_name"]
            pid = playlistInfo["playlist_id"]

            # Check if we are changing the name of the playlsit
            if oldName == newName:
                playlist.updatePlaylist(conn,pid,newName,newGenre)
                playlistInfo = playlist.get_playlist_info(conn,pid)
                flash(newName + '  was updated successfully')
                    
                return render_template('playlist.html', 
                            playlistInfo=playlistInfo, 
                            songs=nestedSongs, 
                            page_title=playlistInfo['playlist_name'])
            else:
                # There cannot be multiple playlists with the same name
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
                    
        else: #delete playlist
            playlist.deletePlaylist(conn,pid)
            flash(oldName + ' deleted successfully')
            return redirect(url_for('user', uid = uid))

@app.route('/user/<int:uid>')
def user(uid):
    '''
    Displays a user's name, friends, and playlists.
    :param uid: unique id for a user
    :returns: the user's profile page
    '''
    conn = dbi.connect()
    user = userpage.get_user_id(conn, uid)
    friendsList = userpage.get_friends(conn, uid)
    playlists = userpage.get_user_playlists(conn, uid)

    return render_template("user.html", user= user, 
        friendsList = friendsList, playlists = playlists)

@app.route('/user/<int:uid>/edit/', methods=["GET", "POST"])
def editUsername(uid):
    '''
    Edits a user's name.
    :param uid: unique id for a user
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('editUsername.html')
    else:
        newName = request.form.get('user-name')
        userpage.update_username(conn, uid, newName)
        flash('Your user profile has been updated!')
        return redirect(url_for("user", uid = uid))

@app.route('/add_song/', methods=["GET", "POST"])
def addSongs():
    '''
    Allows user to add songs to coda database
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('addSongs.html')
    else:
        artistName = request.form.get('artist-name')
        albumName = request.form.get('album-name')
        songName = request.form.get('song-name')
        genre = request.form.get('genre')

        # checks if artist already in database, returns true if not in database
        if (userpage.check_artist(conn, artistName)):
            userpage.add_artist(conn, artistName)
            userpage.add_album(conn, albumName, artistName)
            userpage.add_song(conn, songName, genre, albumName)
            flash(songName + ' has been added to coda database!')
            return redirect(url_for("addSongs"))
        #artist already in database
        else:
            #returns true if album is not in database
            if(userpage.check_album(conn, albumName, artistName)):
                userpage.add_album(conn, albumName)

                #returns true if song is not in database
                if(userpage.check_song(conn, songName, albumName)):
                    userpage.add_song(conn, songName, genre, albumName)
                    flash(songName + ' has been added to coda database!')
                    return redirect(url_for("addSongs"))
                else:
                    flash('Song is already in database!')
                    return redirect(url_for("addSongs"))

            #if artist and album already in database
            else:
                userpage.add_song(conn, songName, genre, albumName)
                flash(songName + " has been added to coda database!")
                return redirect(url_for("addSongs"))

@app.route('/artist/<int:aid>')
def artist(aid):
    '''
    Displays an artist's page, including their albums and songs.
    :param aid: unique id for an artist
    :returns: the artist's profile page
    '''
    conn = dbi.connect()
    artist = artistPage.get_artist(conn, aid)
    albumList = artistPage.get_artist_albums(conn, aid)
    return (render_template("artist.html", artist = artist, 
        albumList = albumList))

@app.route('/album/<int:aid>', methods=["GET", "POST"])
def album(aid):
    ''' 
    This is the route for album lookups. It renders a template 
    with information about the artist and songs in it.

    :param pid: a unique album id from the coda_album table
    :returns: not found page if album does not exist in the database
            the desired album's indiviual page otherwise
    '''
    conn = dbi.connect()
    albumInfo = albumPage.get_album(conn, aid)
    songs = albumPage.get_songs(conn, aid)

    if albumInfo == None: # album not found
        return render_template('notFound.html',
            type='No album', page_title="Album Not Found")
    
    # album found
    return render_template('album.html', 
        albumDescription=albumInfo,
        songs=songs,
        page_title='Album | ' + albumInfo['album_title'])

@app.route('/song/<int:sid>', methods = ['GET','POST'])
def song(sid):
    ''' 
    Returns information about the artist's name and the 
    title of the album on which it appears if get request, 
    if post request, add song to a playlist, and redirect to 
    that playlist page

    :param sid: a unique song id from the coda_song table
    :returns: not found page if song does not exist in the database
            the desired page for that song otherwise
    '''
    conn = dbi.connect()
    song_info = songPage.get_song(conn, sid)
    playlists = playlist.get_playlists(conn)

    if song_info == None: # song not found
        return render_template('notFound.html',
            type='No song', page_title="Song Not Found")

    else: # song found
        if request.method == 'GET': #display playlist info
            allPlaylists = playlist.get_all_playlists(conn)
            return render_template('song.html', 
                song=song_info, 
                sid = sid, playlists = allPlaylists,
                page_title='Song | ' + song_info['song_title'])
        else: #add song to playlist
            pid = request.form.get("playlist-id")
            currentSongs = playlist.get_playlist_songs(conn,pid)
            currentSongIds = [elt['song_id'] for elt in currentSongs]
            if sid in currentSongIds: #check if song exists in playlist already
                flash(song_info['song_title'] + ' already exists in ' + 
                    playlist.get_playlist_info(conn,pid)['playlist_name'])
                return redirect(url_for('song',sid = sid))
            else:
                playlist.addSongToPlaylist(conn,pid,sid)
                return redirect(url_for('playlistPage', pid = pid))

@app.route('/playlist/create', methods = ['GET','POST'])
def createPlaylist():
    '''Returns rendered insert template if get method, or if
    post method, creates a playlist and flashes a link to 
    the new playlist'''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('createPlaylist.html')
                                
    else: #inserting movie action, making sure input is valid
        pName = request.form.get('playlist-name')
        pGenre = request.form.get('playlist-genre')

        #replace with logged in user once authentication added
        pUser = request.form.get('playlist-user') 

        #check if the playlist name already exists
        if playlist.check_unique_playlist_name(conn, pName, pUser):
            playlist.createPlaylist(conn,pName,pGenre,pUser)
            flash(pName + ' has been created!')
            return redirect(url_for('createPlaylist'))
            
        else: #if playlist name by that user already in database
            flash('''This playlist name already exists in database, 
                try a different name!''')
            return redirect(url_for('createPlaylist'))

@app.route('/genre/<string:genreName>')
def genre(genreName):
    ''' 
    Returns a template displaying playlists and songs that fit
    under the given genre.

    :param genreName: playlist or song genre
    :returns: not found page if genre does not exist in the database
            all the playlists and songs with that genre
    '''
    conn = dbi.connect()
    playlists = playlist.playlists_by_genre(conn, genreName)
    songs = songPage.songs_by_genre(conn, genreName)

    if playlists == None and songs == None: # genre not found
        return render_template('notFound.html',
            type='No genre', page_title="Genre Not Found")
    
    return render_template('genre.html',
            page_title=genreName, genre=genreName.title(),
            playlists=playlists, songs=songs)

@app.route('/query/', methods=['GET'])
def query():
    '''
    Renders the template for the user's search.
    :returns: the individual page for an item (album, song, playlist, 
        user, or artist) if there is exactly one match
        otherwise, lists out all matches with links to their individual pages.
    '''
    conn = dbi.connect()
    query = request.args['searchbar'] # query text
    albumMatches = albumPage.get_similar_albums(conn, query)
    songMatches = songPage.get_similar_songs(conn, query)
    userMatches = userpage.search_user(conn, query)
    playlistMatches = playlist.get_similar_playlists(conn, query)
    artistMatches = artistPage.search_artist(conn, query)

    # no matches
    if (not albumMatches and not songMatches and not artistMatches
        and not userMatches and not playlistMatches):
        return render_template('notFound.html', type='Nothing',
        page_title="No matches")

    # one album matches
    elif (len(albumMatches) == 1 and not songMatches and not artistMatches
        and not userMatches and not playlistMatches):
        return redirect(url_for('album', aid=albumMatches[0]['album_id']))

    # one song matches
    elif (len(songMatches) == 1 and not albumMatches and not artistMatches
        and not userMatches and not playlistMatches):
        return redirect(url_for('song', sid=songMatches[0]['song_id']))

    # one user matches
    elif (len(userMatches) == 1 and not songMatches and not albumMatches 
        and not playlistMatches and not artistMatches):
        return render_template("search.html", users = userMatches)

    # one playlist matches
    elif (len(playlistMatches) == 1 and not songMatches and not artistMatches
        and not albumMatches and not playlistMatches):
        return render_template("playlist.html", 
            playlistInfo=playlistMatches)

    # one artist matches
    elif (len(artistMatches) == 1 and not songMatches and not userMatches
        and not albumMatches and not playlistMatches):
        artist = artistMatches[0]
        artistAlbums = artistPage.get_artist_albums(conn, artist['artist_id'])
        return render_template("artist.html", 
            artist=artist, albumList=artistAlbums)

    # multiple matches
    else:
        # get the ids for each album and song that matches the query
        albums = []
        for albumDict in albumMatches:
            albumID = albumDict['album_id']
            albums.append(albumPage.get_album(conn, albumID))  

        # extract information for each matching song
        songs = []
        for songDict in songMatches:
            songID = songDict['song_id']
            songs.append(songPage.get_song(conn, songID))

        # extract information for each matching user
        users = []
        for userDict in userMatches:
            userID = userDict['user_id']
            users.append(userpage.get_user_id(conn, userID))

        # extract information for each matching playlist
        playlists = []
        for playlistDict in playlistMatches:
            playlistID = playlistDict['playlist_id']
            playlists.append(playlist.get_playlist_info(conn, playlistID))

        # extract information for each matching artist
        artists = []
        for artistDict in artistMatches:
            artistID = artistDict['artist_id']
            artists.append(artistPage.get_artist(conn, artistID))

        return render_template('multiple.html', 
            albums=albums, songs=songs, users=users,
            playlists=playlists, name = query, artists=artists,
            page_title="Mutliple Results Found")


@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('coda_db')

if __name__ == '__main__':
    import sys, os
    if len(sys.argv) > 1:
        port=int(sys.argv[1])
        if not(1943 <= port <= 1952):
            print('For CAS, choose a port from 1943 to 1952')
            sys.exit()
    else:
        port=os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)
