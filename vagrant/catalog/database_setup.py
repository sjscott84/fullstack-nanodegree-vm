import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Artist(Base):

  __tablename__ = 'artist'
  name = Column(String(80), nullable = False)
  id = Column(Integer, primary_key = True)


class ArtWork(Base):

  __tablename__ = 'art_work'

  title = Column(String(80), nullable = False)
  id = Column(Integer, primary_key = True)
  year = Column(String(250))
  image_link = Column(String(250))
  artist_id = Column(Integer, ForeignKey('artist.id'))
  artist = relationship(Artist)

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
        'title': self.title,
        'id': self.id,
        'year': self.year,
        'image_link': self.image_link,
    }


engine = create_engine(
  'sqlite:///artistwork.db')

Base.metadata.create_all(engine)
