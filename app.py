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

import random, playlist, albumPage, songPage, userpage, artistPage
import imageupload, insertimagefiles

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# file upload
app.config['UPLOADS'] = 'static'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

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
    conn = dbi.connect()
    username = session['CAS_USERNAME']
    # store uid in session
    session['uid'] = userpage.get_userid_from_username(conn,username)
    user_id = session['uid']
    
    # if user does not yet exist in database
    start_transaction(conn)
    if (userpage.check_username(conn, username)):
        userpage.add_user(conn, username)
    commit_transaction(conn)
    return redirect( url_for('explore') )

@app.route('/')
def index():
    """ Prompts the user to login. """
    return render_template('login.html', page_title='login to coda')

@app.route('/after_logout/')
def after_logout():
    flash('successfully logged out!')
    return redirect( url_for('index') )

def start_transaction(conn):
    ''' 
    Begin the transaction to ensure thread safety 
    :param conn: connection to database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('start transaction')

def commit_transaction(conn):
    ''' 
    End the transaction
    :param conn: connection to database
    '''
    curs = dbi.dict_cursor(conn)
    curs.execute('commit')

@app.route('/explore/')
def explore():
    """ 
    This is the home page, listing out the genres currently existing
    in our database and allowing the user to search for a song, album,
    playlist, artist, or user. 
    """
    conn = dbi.connect()

    # acquire session information
    print('Session keys: ',list(session.keys()))
    for k in list(session.keys()):
        print(k,' => ',session[k])
    if '_CAS_TOKEN' in session:
        token = session['_CAS_TOKEN']
    if 'CAS_USERNAME' in session:
        is_logged_in = True
        username = session['CAS_USERNAME']
        print(('CAS_USERNAME is: ',username))
    else:
        is_logged_in = False
        username = None
        print('CAS_USERNAME is not in the session')
    
    # extract genres from the database to display
    genres = songPage.get_genres(conn) 

    if 'CAS_USERNAME' in session:
        is_logged_in = True
        return render_template('main.html',page_title='home | coda',
            genres=genres, username=username)
    else:
        return render_template('login.html')

@app.route('/playlist/<int:pid>', methods=["GET", "POST"]) 
def playlistPage(pid):
    '''
    playlistPage follows the logic outlined below in order to reduce the amount
    of information we need to extract from the database and limit function
    calls.

    1. Verify that the user is logged in, redirecting to the login page if not
    2. Extract information for the specified playlist
    3. If that playlist is not found, render template for the Not Found page
    4. If the logged-in user wants to delete their own playlist, delete it and
        redirect to their user page
    5. If a playlist is found for the GET request, display the name, genre, 
        and creator for a playlist, along with all the songs that have been 
        added to the playlist
    6. If the user is logged in, they can update their playlist.

    :param pid: unique playlist id
    :returns: 
        the login page if the user is not logged in
        the not found page if no playlist exists with that id
        that playlist's page if a match exists
        profile page of the user who created that playlist if they delete it
    '''
    # restrict access if not logged in
    if 'CAS_USERNAME' not in session:
        flash('Please log in to access playlist information')
        return redirect(url_for("explore"))
    
    conn = dbi.connect()

    # no playlist found
    playlistInfo = playlist.get_playlist_info(conn,pid)
    if playlistInfo == None:
        return render_template('notFound.html',
            type='No playlist', page_title="Playlist Not Found")
        
    # playlist found, so extract relevant information
    uid = playlistInfo['created_by']
    oldName = playlistInfo["playlist_name"]
    submitType = request.form.get('submit')

    # user deletes their own playlist
    if (request.method == "POST" and submitType == 'delete'):
        playlist.deletePlaylist(conn,pid)
        flash(oldName + ' deleted successfully')
        return redirect(url_for('user', uid = uid))
    
    # display playlist information
    nestedSongs = playlist.get_playlist_songs(conn,pid)
    createdby = userpage.get_user_from_id(conn, uid)

    if (request.method == "GET"):
        return render_template('playlist.html', 
                    playlistInfo=playlistInfo, 
                    songs=nestedSongs, 
                    page_title=playlistInfo['playlist_name'],
                    createdby = createdby)

    # user updates playlist
    newName = request.form.get('playlist-name')
    newGenre = request.form.get('playlist-genre')

    pUser = playlistInfo["display_name"]
    pid = playlistInfo["playlist_id"]

    # update the playlist if the name is not being changed
    if oldName == newName:
        playlist.updatePlaylist(conn,pid,newName,newGenre)
        # get newly updated information
        playlistInfo = playlist.get_playlist_info(conn,pid)
        flash(newName + '  was updated successfully')
            
        return render_template('playlist.html', 
                    createdby = createdby,
                    playlistInfo=playlistInfo, 
                    songs=nestedSongs, 
                    page_title=playlistInfo['playlist_name'])
    else:
        # user is changing the name, but there cannot be multiple 
        # playlists with the same name
        start_transaction(conn) # ensure thread safety

        # update the playlist if no other playlist exists with that new name
        if playlist.check_unique_playlist_name(conn, newName, uid):
            playlist.updatePlaylist(conn,pid,newName,newGenre)
            playlistInfo = playlist.get_playlist_info(conn,pid)
            commit_transaction(conn) # complete transaction
            flash(newName + '  was updated successfully')
            
            return render_template('playlist.html', 
                    createdby = createdby,
                    playlistInfo=playlistInfo, 
                    songs=nestedSongs, 
                    page_title=playlistInfo['playlist_name'])

        else:
            # conflicting playlist names
            commit_transaction(conn) # complete transaction
            flash('Error: You already have a playlist with this name')

            return render_template('playlist.html', 
                    createdby = createdby,
                    playlistInfo=playlistInfo, 
                    songs=nestedSongs, 
                    page_title=playlistInfo['playlist_name'])

@app.route('/user/<int:uid>', methods=["GET", "POST"])
def user(uid):
    '''
    Displays a user's name, friends, and playlists.
    Allows logged-in user to follow a friend.
    :param uid: unique id for a user
    :returns: the user's profile page
    '''
    conn = dbi.connect()
    if (request.method == 'GET'):
        if 'CAS_USERNAME' in session:
            # information for the user whose page we are visiting
            user = userpage.get_user_from_id(conn, uid)
            friendsList = userpage.get_friends(conn, uid)
            playlists = userpage.get_user_playlists(conn, uid)
            return render_template("user.html", user= user, 
                page_title = user['display_name'],
                friendsList = friendsList, playlists = playlists)
        else:
            flash('Please log in to access profile page')
            return redirect(url_for("explore"))

    else: # POST to follow friend
        friendId = request.form.get('friend')
        currentUser = request.form.get('currentUser')
        userpage.add_follow(conn,friendId,currentUser)
        currentInfo = userpage.get_user_from_id(conn,currentUser)
        return jsonify({'currentUser':currentInfo['display_name']})

@app.route('/user/<int:uid>/edit/', methods=["GET", "POST"])
def editUsername(uid):
    '''
    Edits a user's name.
    :param uid: unique id for a user
    :returns: the form to edit own username with the GET request
        the current user's profile page with the POST request
    '''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('editUsername.html', page_title='Edit Username')
    else:
        newName = request.form.get('user-name')
        userpage.update_username(conn, uid, newName)
        flash('Your user profile has been updated!')
        return redirect(url_for("user", uid = uid))

@app.route('/add_song/', methods=["GET", "POST"])
def addSongs():
    '''
    Allows user to add songs to coda database
    :returns: form to add songs if logged in
        otherwise, prompts user to log in
    '''
    # not logged in
    if 'CAS_USERNAME' not in session:
        flash("You need to be logged in to add to the database!")
        return redirect(url_for("explore"))

    # logged in
    if request.method == 'GET':
        return render_template('addSongs.html', page_title="Add Song")
    
    else: 
        uid = session['uid']

        # get user-supplied information
        artistName = request.form.get('artist-name')
        albumName = request.form.get('album-name')
        songName = request.form.get('song-name')
        genre = request.form.get('genre')
        year = request.form.get('year')
        
        conn = dbi.connect()

        start_transaction(conn)
        # If the artist is not already in the database, this song cannot conflict 
        # with any existing data, so add the artist, album, and song
        if userpage.check_artist(conn, artistName):
            userpage.add_artist(conn, artistName)
            userpage.add_album(conn, albumName, artistName, year)
            userpage.add_song(conn, songName, genre, albumName, uid)
            sid = userpage.get_song_id(conn, songName, albumName, 
                artistName)['song_id']
            flash(songName + ' has been added to coda database!')
            commit_transaction(conn)
            return redirect(url_for("song", sid = sid))
        
        # Artist already exists in the database, so check for conflicting
        # song titles within the same album, if that album exists
        
        # If album is not in database, add the album and song
        if userpage.check_album(conn, albumName, artistName):
            userpage.add_album(conn, albumName, artistName, year)
            # Since album and artist are not in databases, song is not in database
            userpage.add_song(conn, songName, genre, albumName, uid)
            sid = userpage.get_song_id(conn, songName, albumName, artistName)['song_id']
            flash(songName + ' has been added to coda database!')
            commit_transaction(conn)
            return redirect(url_for("song", sid = sid))

        # Artist and album are already in database,
        # so we can just check for the song

        # returns true if song is not in database
        if userpage.check_song(conn, songName, albumName):
            
            # If a release year was not previously supplied for this song's 
            # album but the form now specifies one, update the release year
            # for that album

            if not userpage.check_album_year(conn, albumName, 
                artistName)['release_year']:
                userpage.update_release(conn, year, albumName, artistName)
            
            # in either case, add the song
            userpage.add_song(conn, songName, genre, albumName, uid)
            sid = userpage.get_song_id(conn, songName, albumName, 
                artistName)['song_id']
            commit_transaction(conn)
            flash(songName + " has been added to coda database!")
            return redirect(url_for("song", sid = sid))

        # song already in database
        else:
            sid = userpage.get_song_id(conn, songName, albumName, 
                artistName)['song_id']
            flash('Song is already in the coda database!')
            commit_transaction(conn)
            return redirect(url_for("song", sid = sid))

@app.route('/artist/<int:aid>')
def artist(aid):
    '''
    Displays an artist's page, including their albums and songs.
    :param aid: unique id for an artist
    :returns: the artist's profile page
    '''
    conn = dbi.connect()
    if 'CAS_USERNAME' in session:
        artist = artistPage.get_artist(conn, aid)
        albumList = artistPage.get_artist_albums(conn, aid)
        return (render_template("artist.html", artist = artist, 
            albumList = albumList, page_title = artist['artist_name']))
    else:
        flash("Please log in to view artist information")
        return redirect(url_for("explore"))

@app.route('/album/<int:aid>', methods=["GET", "POST"])
def album(aid):
    ''' 
    This is the route for album lookups. It renders a template 
    with information about the artist and songs in it.

    :param pid: a unique album id from the coda_album table
    :returns: not found page if album does not exist in the database
            the desired album's individual page otherwise
    '''
    if 'CAS_USERNAME' not in session:
        flash("Please log in to view album information")
        return redirect(url_for("explore"))

    conn = dbi.connect()
    albumInfo = albumPage.get_album(conn, aid)
    songs = albumPage.get_songs(conn, aid)

    if request.method == 'GET':
        is_logged_in = True
        image_url = imageupload.get_image_by_album(conn,albumInfo['album_id'])
        if albumInfo == None: # album not found
            return render_template('notFound.html',
                type='No album', page_title="Album Not Found",
                user_id=user_id)
        
        # album found
        return render_template('album.html', 
            albumDescription=albumInfo,
            songs=songs,
            page_title='Album | ' + albumInfo['album_title'],
            album_image=image_url)

    else: #upload an image
        try:
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format('album'+str(aid),ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)

            insertimagefiles.insert_picfile(conn,pathname,filename,aid)
            image_url = imageupload.get_image_by_album(conn,albumInfo['album_id'])
            flash('Upload successful')
            return render_template('album.html', 
                albumDescription=albumInfo,
                songs=songs,
                page_title='Album | ' + albumInfo['album_title'],
                album_image=image_url)

        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('album.html',src='',nm='',albumDescription=albumInfo)

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

    if song_info == None: # song not found
        return render_template('notFound.html',
            type='No song', page_title="Song Not Found")

    else: # song found
        if 'uid' in session:
            uid = session['uid']

            userPlaylists = playlist.get_all_playlists_by_user(conn,uid)

            # display playlist info, partitioning the user's playlists into
            # ones with and without the specified song
            if request.method == 'GET': 
                # if user has not created any playlists, link to create page
                if len(userPlaylists) == 0: 
                    return render_template('song.html', 
                        song=song_info, 
                        sid = sid, playlists = False,
                        page_title='Song | ' + song_info['song_title'])
                        
                else: 
                    # separate the playlists the song is in from ones it's not in
                    uid = session['uid']
                    pAlreadyIn = playlist.get_playlists_with_song(conn,uid,sid)
                    pNotIn = playlist.get_playlists_without_song(conn,uid,sid)
                    return render_template('song.html', 
                        song=song_info, 
                        sid = sid, playlists = True,
                        pAlreadyIn = pAlreadyIn, pNotIn = pNotIn,
                        page_title='Song | ' + song_info['song_title'])
                
            else: # forms to add song to a playlist, or create a playlist
                if request.form.get('create-playlist'): 
                    return redirect(url_for('createPlaylist'))
                else:
                    pid = request.form.get("playlist-id")
                    start_transaction(conn)
                    currentSongs = playlist.get_playlist_song_ids(conn,pid)
                    # check if song already exists in playlist
                    if sid in currentSongs: 
                        flash(song_info['song_title'] + ' already exists in ' + 
                            playlist.get_playlist_info(conn,pid)['playlist_name'])
                        commit_transaction(conn)
                        return redirect(url_for('song', sid=sid))
                    else:
                        playlist.addSongToPlaylist(conn,pid,sid)
                        commit_transaction(conn)
                        return redirect(url_for('playlistPage', pid=pid))
        else:
            flash('Log in to view song and add to playlists!')
            return redirect(url_for('explore'))

@app.route('/playlist/create', methods = ['GET','POST'])
def createPlaylist():
    '''
    Returns rendered insert template if get method, or if
    post method, creates a playlist and flashes a link to 
    the new playlist
    '''
    conn = dbi.connect()
    if 'uid' in session:
        user_id = session['uid']

        if request.method == 'GET':
            return render_template('createPlaylist.html', 
                page_title="Create Playlist")
                                    
        else: #inserting movie action, making sure input is valid
            pName = request.form.get('playlist-name')
            pGenre = request.form.get('playlist-genre') 

            #check if the playlist name already exists
            start_transaction(conn) # ensure thread safety
            if playlist.check_unique_playlist_name(conn, pName, user_id):
                playlist.createPlaylist(conn,pName,pGenre, user_id)
                pid = userpage.get_playlist(conn, pName, user_id)['playlist_id']
                flash(pName + ' has been created!')
                commit_transaction(conn) # complete transaction
                return redirect(url_for('playlistPage', pid = pid))
                
            else: #if playlist name by that user already in database
                commit_transaction(conn) # complete transaction
                flash('''This playlist name already exists in database, 
                    try a different name!''')
                return redirect(url_for('createPlaylist'))
    else:
        flash('Please log in to create playlist!')
        return redirect(url_for('explore'))

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
        return render_template("user.html", user = userMatches[0],
            page_title = userMatches[0]['display_name'])

    # one playlist matches
    elif (len(playlistMatches) == 1 and not songMatches and not artistMatches
        and not albumMatches and not playlistMatches):
        return render_template("playlist.html", playlistInfo=playlistMatches,
            page_title = playlistMatches['playlist_name'])

    # one artist matches
    elif (len(artistMatches) == 1 and not songMatches and not userMatches
        and not albumMatches and not playlistMatches):
        artist = artistMatches[0]
        artistAlbums = artistPage.get_artist_albums(conn, artist['artist_id'])
        return render_template("artist.html", artist=artist, 
            albumList=artistAlbums, page_title=artist['artist_name'])

    # multiple matches
    else:
        # get the ids for each album that matches the query
        albums = []
        album_list = [albumDict['album_id'] for albumDict in albumMatches]
        if len(album_list) > 0:
            # only execute if there exist album ids for which to extract info
            albums = albumPage.multiple_albums(conn, album_list)

        # extract information for each matching song
        songs = []
        sid_list = [songDict['song_id'] for songDict in songMatches]
        if len(sid_list) > 0:
            songs = songPage.multiple_songs(conn, sid_list)

        # extract information for each matching user
        users = []
        uid_list = [userDict['user_id'] for userDict in userMatches]
        if len(uid_list) > 0:
            users = userpage.multiple_users(conn, uid_list)
        
        # extract information for each matching playlist
        playlists = []
        pid_list = [playlistDict['playlist_id'] for playlistDict
            in playlistMatches]
        if len(pid_list) > 0:
            playlists = playlist.multiple_playlists(conn, pid_list)

        # extract information for each matching artist
        artists = []
        artist_list = [artistDict['artist_id'] for artistDict in artistMatches]
        if len(artist_list) > 0:
            artists = artistPage.multiple_artists(conn, artist_list)

        return render_template('multiple.html', 
            albums=albums, songs=songs, users=users,
            playlists=playlists, artists=artists, name=query, 
            page_title="Multiple Results Found")


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
