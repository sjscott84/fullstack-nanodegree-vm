from flask import Flask, render_template, request, redirect, url_for, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Artist, ArtWork

engine = create_engine('sqlite:///artistwork.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#main page - displays a list of artists
@app.route('/')
@app.route('/artists/')
def showArtists():
  items = session.query(Artist).all()
  return render_template('artists.html', items = items)

# Add a new artist
@app.route('/artists/add_artist/', methods=['GET', 'POST'])
def addArtist():
  if request.method == 'POST':
    #TODO = make sure artist does not already exist
    newArtist = Artist(name = request.form['artist_name'])
    session.add(newArtist)
    session.commit()
    return redirect(url_for('showArtists'))
  else:
    return render_template('add_artist.html')

# Delete a particular artist
@app.route('/artists/<int:idOfArtist>/delete_artist', methods=['GET', 'POST'])
def deleteArtist(idOfArtist):
  artist = session.query(Artist).filter_by(id = idOfArtist).one()
  artist_works = session.query(ArtWork).filter_by(artist_id = idOfArtist).all()
  if request.method == 'POST':
    for art in artist_works:
      session.delete(art)
    session.delete(artist)
    session.commit()
    return redirect(url_for('showArtists'))
  else:
    return render_template('delete_artist.html', id = idOfArtist, name = artist.name)

# Edit a particular artist
@app.route('/artists/<int:idOfArtist>/edit_artist', methods=['GET', 'POST'])
def editArtist(idOfArtist):
  artist = session.query(Artist).filter_by(id = idOfArtist).one()
  if request.method == 'POST':
    artist.name = request.form['name']
    session.add(artist)
    session.commit()
    return redirect(url_for('showArtists'))
  else:
    return render_template('edit_artist.html', id = idOfArtist, name = artist.name)

# Show all art works associated with particular artist
@app.route('/artists/<int:idOfArtist>/', methods=['GET', 'POST'])
def showArtistDetails(idOfArtist):
  artistFromDB = session.query(Artist).filter_by(id = idOfArtist).one()
  items = session.query(ArtWork).filter_by(artist_id = idOfArtist)
  return render_template('art_works.html', items = items, name = artistFromDB.name, id = idOfArtist)


# Add a new work for a particular artist
@app.route('/artists/<int:idOfArtist>/add_work/', methods=['GET', 'POST'])
def addArtWork(idOfArtist):
  if request.method == 'POST':
    newArt = ArtWork(title = request.form['title'], year = request.form['year'], 
      image_link = request.form['image'], artist_id = idOfArtist)
    session.add(newArt)
    session.commit()
    return redirect(url_for('showArtistDetails', idOfArtist = idOfArtist))
  else:
    artistFromDB = session.query(Artist).filter_by(id = idOfArtist).one()
    return render_template('add_art_work.html', name = artistFromDB.name, id = idOfArtist)


# Delete a work by a particular artist
@app.route('/artists/<int:idOfArt>/delete_work/', methods=['GET', 'POST'])
def deleteArtWork(idOfArt):
  art = session.query(ArtWork).filter_by(id = idOfArt).one()
  if request.method == 'POST':
    session.delete(art)
    session.commit()
    return redirect(url_for('showArtistDetails', idOfArtist = art.artist_id))
  else:
    return render_template('delete_art.html', title = art.title, id = idOfArt)


# Edit an entry about a peice of work
@app.route('/artists/<int:idOfArt>/edit_work/', methods=['GET', 'POST'])
def editArtWork(idOfArt):
  art = session.query(ArtWork).filter_by(id = idOfArt).one()
  if request.method == 'POST':
    art.title = request.form['title']
    art.year = request.form['year']
    art.image_link = request.form['image']
    session.add(art)
    session.commit()
    return redirect(url_for('showArtistDetails', idOfArtist = art.artist_id))
  else:
    return render_template('edit_work.html', title = art.title, id = idOfArt, year = art.year, image = art.image_link)

@app.route('/artists/<int:idOfArtist>/art_works/JSON')
def restaurantMenuJSON(idOfArtist):
    items = session.query(ArtWork).filter_by(
        artist_id=idOfArtist).all()
    return jsonify(ArtistWorks=[i.serialize for i in items])

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)