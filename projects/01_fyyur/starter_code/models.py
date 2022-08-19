#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Show id: {self.id}, artist_id: {self.artist_id}, venue_id: {self.venue_id}, start_time: {self.start_time}>'

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String,)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  # added genres
  genres = db.Column(db.String)

  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String)
  seeking_talent = db.Column(db.Boolean,nullable=False,default=False)
  seeking_description = db.Column(db.String)
  
  # Specify the relationship on the parent model for Show
  shows = db.relationship('Show', backref='venue')

  def __repr__(self):
    return f'<Venue id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # DONE: implement any missing fields, as a database migration using Flask-Migrate
  website_link = db.Column(db.String)
  seeking_venue = db.Column(db.Boolean,nullable=False,default=False)
  seeking_description = db.Column(db.String)
  
  # Specifies the relationship on the parent model for Show
  shows = db.relationship('Show', backref='artist')

  def __repr__(self):
    return f'<Artist id: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}>'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.