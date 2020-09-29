from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
app = Flask(__name__)

# one or the other of these. Defaults to MySQL (PyMySQL)
# change comment characters to switch to SQLite

import pymysql
import cs304dbi as dbi
import userpage
import random

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
    else:
        flash('No Results Found For "' + value + '"')
        return render_template("search.html")

@app.route('/user/<user_id>')
def user(user_id):
    conn = dbi.connect()
    user = userpage.get_user_id(conn, user_id)
    friendsList = userpage.get_friends(conn, user_id)
    playlists = userpage.get_user_playlists(conn, user_id)
    return (render_template("user.html", user= user, friendsList = friendsList, playlists = playlists))

@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    conn = dbi.connect()
    playlist = userpage.get_playlist(conn, playlist_id)
    return (render_template("playlist.html", playlist = playlist))

@app.before_first_request
def init_db():
    dbi.cache_cnf()
    dbi.use('coda_db') # or whatever db

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
