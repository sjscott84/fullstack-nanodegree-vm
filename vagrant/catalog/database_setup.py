import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

Base = declarative_base()


# Creates a table of users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False)


# Creates a table of artists
class Artist(Base):
    __tablename__ = 'artist'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)


#Creates a table of artworks
class ArtWork(Base):
    __tablename__ = 'art_work'

    title = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    year = Column(String(250))
    image_link = Column(String(250))
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship(Artist, backref=backref('art_work'), cascade="all, delete")
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

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
  'sqlite:///artistworkwithuser.db')

Base.metadata.create_all(engine)
