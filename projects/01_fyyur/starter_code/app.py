#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from os import name
from models import db, Venue, Show, Artist
from ast import Num
from distutils.log import error
from email.policy import default
from hashlib import new
from heapq import merge
from itertools import count
from lib2to3.pygram import pattern_symbols
# import json
from re import S
from sre_parse import State
import sys
from tempfile import tempdir
from unittest import skip
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import Column
from forms import *
import datetime
import collections
collections.Callable = collections.abc.Callable

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# DONE: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Venues.
#----------------------------------------------------------------------------#

#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  try:
    new_venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
    )
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
  #   # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
    return render_template('pages/home.html')

#  Read Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  data = []

  city_state = db.session.query(Venue.city,Venue.state).distinct(Venue.city,Venue.state).all()
  

  for i in city_state:
    venues = db.session.query(Venue.id,Venue.name, Venue.city, Venue.state).filter(Venue.city == i.city and Venue.state == i.state)

    show_city_venue = {
      'city': i.city,
      'state': i.state,
      'venues': list(venues)
    }
    data.append(show_city_venue)
    
  return render_template('pages/venues.html', areas=data);

#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  search_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    'count': len(search_result),
    'data': search_result,
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Read Venue with venue_id
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)

  total_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).all()
  
  upcoming_shows = []
  past_shows = []

  for show in total_shows:
    if show.start_time > datetime.datetime.now():
      upcoming_shows.append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time,
      })
    else:
      past_shows.append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time,
      })

  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': [venue.genres],
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website_link': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),

  }
  return render_template('pages/show_venue.html', venue=data)

#  Update Venues
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
  
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('Venue was not successfully edited!')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))
  
#  Delete Venue
#  ----------------------------------------------------------------  
@app.route('/venues/<venue_id>/delete/', methods=['GET'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('You have successfully deleted ' + venue.name )
  except:
    db.session.rollback()
    flash('Error deleting ' + venue.name )
  finally:
    db.session.close()
  return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#----------------------------------------------------------------------------#
# Artist.
#----------------------------------------------------------------------------#

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    form = ArtistForm(request.form)
    new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
    )
    db.session.add(new_artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    # return redirect(url_for('artists'))
  return render_template('pages/home.html')

#  Read Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name)
  return render_template('pages/artists.html', artists=artists)

#  Read Artists with artist_id
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

  upcoming_shows = []
  past_shows = []

  total_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).all()
  for show in total_shows:
    if show.start_time > datetime.datetime.now():
      upcoming_shows.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': str(show.start_time),
      })
    else:
      past_shows.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': str(show.start_time),
      })

  data = {
    'id': artist.id,
    'name': artist.name,
    'generes': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website_link': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Delete Artist
#  ----------------------------------------------------------------  
@app.route('/artists/<artist_id>/delete/', methods=['GET'])
def delete_artist(artist_id):
  # Done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    artist = Artist.query.get(artist_id)
    db.session.delete(artist)
    db.session.commit()
    flash('You have successfully deleted ' + artist.name )
  except:
    db.session.rollback()
    flash('Error deleting ' + artist.name )
  finally:
    db.session.close()
  return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Search Artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term','')
  search_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    'count': len(search_result),
    'data': search_result,
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
  
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] +  ' was not successfully edited!')
    print(sys.exc_info)

  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#----------------------------------------------------------------------------#
# Shows.
#----------------------------------------------------------------------------#

#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  try:
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(new_show)
    db.session.commit()
    flash('You have successfully created a show.')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Read Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.

  data = []
  all_shows = Show.query.all()

  for show in all_shows:
    data.append({
      'venue_id': show.venue.id,
      'venue_name': show.venue.name,
      'artist_id': show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time,
    })
    
  return render_template('pages/shows.html', shows=data)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
