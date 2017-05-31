from flask import Flask, render_template, request, redirect,\
  url_for, jsonify, flash, make_response
from flask import session as login_session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func, select
from database_setup import Base, User, Artist, ArtWork

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import requests
import json

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']

engine = create_engine('sqlite:///artistworkwithuser.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create an http response
def makeResponse(message, code):
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response


# Create a user in the database
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one()
    return user.id


# Return the id for a logged in user
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Create a random string for login state and render the login screen
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Autenticate user with google
@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    if request.method == 'POST':
        # Validate state token
        if request.args.get('state') != login_session['state']:
            return makeResponse('Invalid state parameter', 401)
        # Get authorization code
        code = request.data
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            return makeResponse('Failed to upgrade the authorization \
                code.', 401)

        # Check that access token is valid
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?' +
               'access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        if result.get('error') is not None:
            return makeResponse(result.get('error'), 50)

        # Verfiy that the access token is used for the intended user
        gplus_id = credentials.id_token['sub']

        if result['user_id'] != gplus_id:
            return makeResponse("Token's user ID doesn't match \
                                given user ID", 401)

        # Verify that the access token is valid for this app
        if result['issued_to'] != CLIENT_ID:
            return makeResponse("Token's client ID does not match apps", 401)

        stored_credentials = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')

        if stored_credentials is not None and gplus_id == stored_gplus_id:
            return makeResponse('Current user is already connected', 200)

        # Store the access token in the session for later use
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = params = {'access_token': credentials.access_token,
                           'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)
        data = answer.json()
        login_session['username'] = data['name']
        login_session['email'] = data['email']
        user_id = getUserID(login_session['email'])

        if not user_id:
            user_id = createUser(login_session)

        login_session['user_id'] = user_id
        return 'Login Successful'
    else:
        return redirect(url_for('showLogin'))


# Logout user using google
@app.route('/gdisconnect', methods=['GET', 'POST'])
def gdisconnect():
    if request.method == "POST":
        access_token = login_session.get('access_token')
        if access_token is None:
            return makeResponse('Current User is not connected', 401)

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
              % access_token
        h = httplib2.Http()
        result, content = h.request(url, 'GET')
        error = json.loads(content)

        if result['status'] == '200' or error['error'] == 'invalid_token':
            # if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['user_id']
            # return makeResponse('Successfully disconnected', 200)
            return redirect(url_for("showLogin"))
        else:
            return makeResponse('Failed to revoke token for given user', 400)
    else:
        return render_template('logout.html')


# Home page - displays a list of artists
@app.route('/')
@app.route('/artists/')
def showArtists():
    user = login_session.get('username')
    items = session.query(Artist).all()
    work = session.query(ArtWork).order_by(func.random()).first()

    # This ensures the page still renders even if no art works have
    # been saved to the database
    if work:
        return render_template('artists.html', items=items,
                               image=work.image_link, title=work.title,
                               user=user)
    else:
        return render_template('artists.html', items=items,
                               user=user)


# Search for an artist
@app.route('/artists/search/', methods=['GET', 'POST'])
def search():
    artist = session.query(Artist).filter(Artist.name.ilike(
      request.form['name'])).first()
    if artist:
        return redirect(url_for("showArtistDetails",
                                idOfArtist=artist.id,
                                nameOfArtist=artist.name))
    else:
        flash("No artist found for " + request.form['name'])
        return redirect(url_for("showArtists"))


# Add a new artist
@app.route('/artists/add_artist/', methods=['GET', 'POST'])
def addArtist():
    user = login_session.get('username')
    # Only a logged in user can add an artist
    if 'username' not in login_session:
        flash("You need to login to add an artist")
        return redirect('/login')

    if request.method == 'POST':
        # Make sure an entry for artist does not already exist before
        # creating
        exisitingArtist = session.query(Artist).filter(Artist.name.ilike(
          request.form['artist_name'])).first()
        if not exisitingArtist:
            newArtist = Artist(name=request.form['artist_name'],
                               creator_id=login_session['user_id'])
            session.add(newArtist)
            session.commit()
            return redirect(url_for('showArtists'))
        else:
            flash("This artist already exists")
            return redirect(url_for('showArtistDetails',
                            idOfArtist=exisitingArtist.id,
                            nameOfArtist=exisitingArtist.name, user=user))
    else:
        return render_template('add_artist.html', user=user)


# Delete a particular artist
@app.route('/artists/<int:idOfArtist>/<string:nameOfArtist>/delete_artist',
           methods=['GET', 'POST'])
def deleteArtist(idOfArtist, nameOfArtist):
    user = login_session.get('username')
    artist = session.query(Artist).filter_by(id=idOfArtist).one()

    if request.method == 'POST':
        session.delete(artist)
        session.commit()
        return redirect(url_for('showArtists'))
    else:
        return render_template('delete_artist.html', id=idOfArtist,
                               name=artist.name, creator_id=artist.creator_id,
                               user_id=login_session['user_id'], user=user)


# Edit a particular artist
@app.route('/artists/<int:idOfArtist>/<string:nameOfArtist>/edit_artist',
           methods=['GET', 'POST'])
def editArtist(idOfArtist, nameOfArtist):
    user = login_session.get('username')
    artist = session.query(Artist).filter_by(id=idOfArtist).one()

    if request.method == 'POST':
        artist.name = request.form['name']
        session.add(artist)
        session.commit()
        items = session.query(ArtWork).filter_by(artist_id=idOfArtist)
        return redirect(url_for('showArtistDetails',
                                idOfArtist=idOfArtist,
                                nameOfArtist=nameOfArtist,
                                user=user))
    else:
        return render_template('edit_artist.html', id=idOfArtist,
                               name=artist.name, creator_id=artist.creator_id,
                               user_id=login_session['user_id'],
                               user=user)


# Show all art works associated with particular artist
@app.route('/artists/<int:idOfArtist>/<string:nameOfArtist>/',
           methods=['GET', 'POST'])
def showArtistDetails(idOfArtist, nameOfArtist):
    user = login_session.get('username')
    print user
    artistFromDB = session.query(Artist).filter_by(id=idOfArtist).one()
    items = session.query(ArtWork).filter_by(artist_id=idOfArtist)

    # If user is not logged in only show page with no add,
    # delete or edit options.
    # If user is logged in add, edit or delete options are only shown for items
    # that user created
    if 'username' not in login_session:
        return render_template('public_art_works.html', items=items,
                               name=nameOfArtist, id=idOfArtist, user=user)
    else:
        return render_template('art_works.html', items=items,
                               name=nameOfArtist, id=idOfArtist,
                               user_id=login_session['user_id'],
                               creator_id=artistFromDB.creator_id, user=user)


# Add a new work for a particular artist
@app.route('/artists/<int:idOfArtist>/<string:nameOfArtist>/add_work/',
           methods=['GET', 'POST'])
def addArtWork(idOfArtist, nameOfArtist):
    user = login_session.get('username')
    # Only a logged in user can add an art work
    if 'username' not in login_session:
        flash("You need to login to add an art work")
        return redirect('/login')

    if request.method == 'POST':
        newArt = ArtWork(title=request.form['title'],
                         year=request.form['year'],
                         image_link=request.form['image'],
                         artist_id=idOfArtist,
                         creator_id=login_session['user_id'])
        session.add(newArt)
        session.commit()
        return redirect(url_for('showArtistDetails', idOfArtist=idOfArtist,
                                nameOfArtist=nameOfArtist, user=user))
    else:
        artistFromDB = session.query(Artist).filter_by(id=idOfArtist).one()
        return render_template('add_art_work.html', name=artistFromDB.name,
                               id=idOfArtist, user=user)


# Delete a work by a particular artist
@app.route('/artists/<int:idOfArt>/delete_work/', methods=['GET', 'POST'])
def deleteArtWork(idOfArt):
    user = login_session.get('username')
    art = session.query(ArtWork).filter_by(id=idOfArt).one()
    artist = session.query(Artist).filter_by(id=art.artist_id).one()

    if request.method == 'POST':
        session.delete(art)
        session.commit()
        return redirect(url_for('showArtistDetails',
                                idOfArtist=art.artist_id,
                                nameOfArtist=artist.name,
                                user=user))
    else:
        return render_template('delete_art.html', title=art.title,
                               id=idOfArt, name=artist.name,
                               idOfArtist=art.artist_id,
                               creator_id=art.creator_id,
                               user_id=login_session['user_id'], user=user)


# Edit an entry about an art work
@app.route('/artists/<int:idOfArt>/edit_work/', methods=['GET', 'POST'])
def editArtWork(idOfArt):
    user = login_session.get('username')
    art = session.query(ArtWork).filter_by(id=idOfArt).one()
    artist = session.query(Artist).filter_by(id=art.artist_id).one()

    if request.method == 'POST':
        art.title = request.form['title']
        art.year = request.form['year']
        art.image_link = request.form['image']
        session.add(art)
        session.commit()
        return redirect(url_for('showArtistDetails',
                                idOfArtist=art.artist_id,
                                nameOfArtist=artist.name,
                                user=user))
    else:
        return render_template('edit_work.html', title=art.title,
                               id=idOfArt, year=art.year, image=art.image_link,
                               creator_id=art.creator_id,
                               user_id=login_session['user_id'],
                               idOfArtist=art.artist_id,
                               nameOfArtist=artist.name,
                               user=user)


# JSON API endpoint for a list of works by a specific artist
@app.route('/artists/<int:idOfArtist>/art_works/JSON')
def artWorksJSON(idOfArtist):
    items = session.query(ArtWork).filter_by(artist_id=idOfArtist).all()
    return jsonify(ArtistWorks=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
