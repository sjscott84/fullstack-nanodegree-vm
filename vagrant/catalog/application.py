from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Artist, ArtWork

engine = create_engine('sqlite:///artistwork.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/artists/')
def showArtists():
  items = session.query(Artist).all()
  return render_template('artists.html', items = items)

@app.route('/')
@app.route('/artists/add_artist/', methods=['GET', 'POST'])
def addArtist():
  #items = session.query(Artist).all()
  if request.method == 'POST':
    #checkArtist = session.query(Artist).filter_by(request.form['artist_name'] = Artist.name)
    #if not checkArtist:
    newArtist = Artist(name = request.form['artist_name'])
    session.add(newArtist)
    session.commit()
    return redirect(url_for('showArtists'))
  else:
    return render_template('add_artist.html')

@app.route('/')
@app.route('/artists/<int:idOfArtist>/', methods=['GET', 'POST'])
def showArtistDetails(idOfArtist):
  artistFromDB = session.query(Artist).filter_by(id = idOfArtist).one()
  items = session.query(ArtWork).filter_by(artist_id = idOfArtist)
  return render_template('art_works.html', items = items, name = artistFromDB.name, id = idOfArtist)

@app.route('/')
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

@app.route('/')
@app.route('/artists/<int:idOfArt>/delete_work/', methods=['GET', 'POST'])
def deleteArtWork(idOfArt):
  art = session.query(ArtWork).filter_by(id = idOfArt).one()
  if request.method == 'POST':
    session.delete(art)
    session.commit()
    return redirect(url_for('showArtistDetails', idOfArtist = art.artist_id))
  else:
    return render_template('delete_art.html', title = art.title, id = idOfArt)

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)