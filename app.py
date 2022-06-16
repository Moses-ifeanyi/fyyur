#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from enum import unique
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy import Column, Integer, func
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_bootstrap import Bootstrap
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
import os
from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
        __tablename__ = 'venues'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        address = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        genres = db.Column(db.ARRAY(db.String), nullable=False)
        website = db.Column(db.String(120))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
        seeking_description = db.Column(db.String(2000))
        shows = db.relationship('Show', backref = "venue", lazy=True, 
                cascade="all, delete")


#     # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
        __tablename__ = 'artists'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        genres = db.Column(db.ARRAY(db.String), nullable=False)
        website = db.Column(db.String(120))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
        seeking_description = db.Column(db.String(2000))
        shows = db.relationship('Show', backref = "artist", lazy=True, 
                cascade="all, delete")


#     # TODO: implement any missing fields, as a database migration using Flask-Migrate

# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
        __tablename__ = "shows"
        id = db.Column(db.Integer, primary_key=True)
        start_time = db.Column(db.DateTime())
        venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
        artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    # if format == 'full':
    #     format = "EEEE MMMM, d, y 'at' h:mma"
    # elif format == 'medium':
    #     format = "EE MM, dd, y h:mma"
    
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = {}
    for cities in Venue.query.all():
        city = cities.city
        if city not in data:
            data[city] = {}
            data[city]['city'] = city
            data[city]['state'] = cities.state
            data[city]['venues'] = []
        venue_data = {}
        venue_data['id'] = cities.id
        venue_data['name'] = cities.name
        # upcoming_shows = db.session.query(Show).filter(Show.venue_id == row.id)\
        # .filter(Show.start_time > datetime.now()).all()
        upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).all()
        venue_data['num_upcoming_shows'] = len(upcoming_shows)
        data[city]['venues'].append(venue_data)

    return render_template('pages/venues.html', areas=data.values());


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    string_search = request.form.get('string_search', '')
    search_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{string_search}%')).all()

    response = {}
    response['count'] = len(search_results)
    response['data'] = []
    for venues in search_results:
        venue = {}
        venue['id'] = venues.id
        venue['name'] = venues.name
        # upcoming_shows = db.session.query(Show).filter(Show.venue_id == row.id)\
        # .filter(Show.start_time > datetime.now()).all()
        upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).all()
        venue['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(venue)

    return render_template('pages/search_venues.html', results=response, string_search=string_search)
    
@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # convert genre string back to array
    
    venue = Venue.query.filter_by(id=venue_id).first()
    venue_data = {}
    venue_data['id'] = venue.id
    venue_data['name'] = venue.name
    venue_data['genres'] = venue.genres
    venue_data['address'] = venue.address
    venue_data['city'] = venue.city
    venue_data['state'] = venue.state
    venue_data['phone'] = venue.phone
    venue_data['website'] = venue.website
    venue_data['facebook_link'] = venue.facebook_link
    venue_data['seeking_talent'] = venue.seeking_talent
    if venue.seeking_talent:venue_data['seeking_description'] = venue.seeking_description
    venue_data['image_link'] = venue.image_link

    # get the data of past shows and upcoming shows
    venue_data['past_shows'] = []
    venue_data['upcoming_shows'] = []

    # past_shows = Show.query.filter(Show.venue_id == venue_id)\
    #     .filter(Show.start_time < datetime.now()).order_by(desc(Show.start_time)).all()
    past_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time < datetime.now()).order_by(Show.start_time).all()

    venue_data['past_shows_count'] = len(past_shows)
    for past in past_shows:
        past_count_info = {}
        past_count_info['artist_id'] = past.artist_id
        past_count_info['artist_name'] = past.artist.name
        past_count_info['artist_image_link'] = past.artist.image_link
        past_count_info['start_time'] = past.start_time
        venue_data['past_shows'].append(past_count_info)

    # upcoming_shows = Show.query.filter(Show.venue_id == venue_id)\
    #     .filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()
    upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()

    venue_data['upcoming_shows_count'] = len(upcoming_shows)
    for upcoming in upcoming_shows:
        upcoming_count = {}
        upcoming_count['artist_id'] = upcoming.artist_id
        upcoming_count['artist_name'] = upcoming.artist.name
        upcoming_count['artist_image_link'] = upcoming.artist.image_link
        upcoming_count['start_time'] = upcoming.start_time
        upcoming_count['upcoming_shows'].append(upcoming_count)

    return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])

def create_venue_form():
    Form = VenueForm()
    return render_template('forms/new_venue.html', form=Form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm()
    if form.validate():
        try:

            newVenue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=form.genres.data,
                website=form.website_link.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data, 
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data)

            db.session.add(newVenue)
            db.session.commit()
            flash(f'Venue {form.name.data} was successfully listed!')
        except:
            db.session.rollback()
            flash(f'An error occurred. Venue {form.name.data} could not be listed.')
        finally:
            db.session.close()
    else:
      message = []
      for field, err in form.errors.items():
           message.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(message)}')
    return render_template('pages/home.html')

   
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
        flash('The venue has been removed together with all of its shows.')
        return render_template('pages/home.html')
    except ValueError:
        db.session.rollback()
        flash('It was not possible to delete this Venue')
    finally:
        db.session.close()
    return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    
    venue_result = Venue.query.get(venue_id)
    venue = {}
    venue['id'] = venue_result.id
    venue['name'] = venue_result.name
    venue['genres'] = venue_result.genres
    venue['address'] = venue_result.address
    venue['city'] = venue_result.city
    venue['state'] = venue_result.state
    venue['phone'] = venue_result.phone
    venue['website'] = venue_result.website
    venue['facebook_link'] = venue_result.facebook_link
    venue['seeking_talent'] = venue_result.seeking_talent
    venue['seeking_description'] = venue_result.seeking_description
    venue['image_link'] = venue_result.image_link

    form.name.data = venue_result.name
    form.genres.data = venue_result.genres
    form.address.data = venue_result.address
    form.city.data = venue_result.city
    form.state.data = venue_result.state
    form.phone.data = venue_result.phone
    form.website_link.data = venue_result.website
    form.facebook_link.data = venue_result.facebook_link
    form.seeking_talent.data = venue_result.seeking_talent
    form.seeking_description.data = venue_result.seeking_description
    form.image_link.data = venue_result.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
  
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = Artist.query.order_by('id').all()
    data = []
    for row in artists:
        artist_info = {}
        artist_info['id'] = row.id
        artist_info['name'] = row.name
        data.append(artist_info)

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    response = {}
    search_results = db.session.query(Artist)\
    .filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {}
    response['count'] = len(search_results)
    response['data'] = []
    for row in search_results:
        artist_info = {}
        artist_info['id'] = row.id
        artist_info['name'] = row.name
        upcoming_shows = db.session.query(Show).filter(Show.artist_id == row.id)\
        .filter(Show.start_time > datetime.now()).all()
        artist_info['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(artist_info)

    return render_template('pages/search_artists.html', results=response, 
        search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    data = {}
    data['id'] = artist.id
    data['name'] = artist.name
    data['genres'] = artist.genres
    data['city'] = artist.city
    data['state'] = artist.state
    data['phone'] = artist.phone
    data['website'] = artist.website
    data['facebook_link'] = artist.facebook_link
    data['seeking_venue'] = artist.seeking_venue
    if artist.seeking_venue:
        data['seeking_description'] = artist.seeking_description
    data['image_link'] = artist.image_link

    # get the data of past shows and upcoming shows
    data['past_shows'] = []
    data['upcoming_shows'] = []

    past_shows = Show.query.filter(Show.artist_id == artist_id)\
        .filter(Show.start_time < datetime.now()).order_by(Show.start_time).all()

    data['past_shows_count'] = len(past_shows)
    for row in past_shows:
        show_info = {}
        show_info['venue_id'] = row.venue_id
        show_info['venue_name'] = row.venue.name
        show_info['venue_image_link'] = row.venue.image_link
        show_info['start_time'] = row.start_time
        data['past_shows'].append(show_info)

    upcoming_shows = Show.query.filter(Show.artist_id == artist_id)\
        .filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()
    data['upcoming_shows_count'] = len(upcoming_shows)
    for row in upcoming_shows:
        show_info = {}
        show_info['venue_id'] = row.venue_id
        show_info['venue_name'] = row.venue.name
        show_info['venue_image_link'] = row.venue.image_link
        show_info['start_time'] = row.start_time
        data['upcoming_shows'].append(show_info)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_result = Artist.query.get(artist_id)
    artist = {}
    artist['id'] = artist_result.id
    artist['name'] = artist_result.name
    artist['genres'] = artist_result.genres
    artist['city'] = artist_result.city
    artist['state'] = artist_result.state
    artist['phone'] = artist_result.phone
    artist['website'] = artist_result.website
    artist['facebook_link'] = artist_result.facebook_link
    artist['seeking_venue'] = artist_result.seeking_venue
    artist['seeking_description'] = artist_result.seeking_description
    artist['image_link'] = artist_result.image_link

    form.name.data = artist_result.name
    form.genres.data = artist_result.genres
    form.city.data = artist_result.city
    form.state.data = artist_result.state
    form.phone.data = artist_result.phone
    form.website_link.data = artist_result.website
    form.facebook_link.data = artist_result.facebook_link
    form.seeking_venue.data = artist_result.seeking_venue
    form.seeking_description.data = artist_result.seeking_description
    form.image_link.data = artist_result.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)

    
    # TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm()
    if form.validate():
        artist = Artist.query.get(artist_id)
        try:
            artist.name=form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.genres=form.genres.data
            artist.website=form.website_link.data
            artist.image_link=form.image_link.data
            artist.facebook_link = form.facebook_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data
            db.session.commit()
            flash(f'Artist {artist.name} was successfully updated!')
        except:
            db.session.rollback()
            print(sys.exc_info())

            flash(f'An error occurred. Artist {artist.name} could not be updated.')
        finally:
            db.session.close()
    else:
      message = []
      for field, err in form.errors.items():
           message.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(message)}')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
 
    form = VenueForm()
    if form.validate():

        venue = Venue.query.get(venue_id)

        try:
            venue.name=form.name.data
            venue.address=form.address.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.phone=form.phone.data
            venue.genres=form.genres.data
            venue.website=form.website_link.data
            venue.image_link=form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            db.session.commit()
            flash(f'Venue {venue.name} was successfully updated!')
        except:
            db.session.rollback()
            flash(f'An error occurred. Venue {venue.name} could not be updated.')
        finally:
            db.session.close()
    else:
      message = []
      for field, err in form.errors.items():
           message.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(message)}')
    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
  # form = ArtistForm()
    form = ArtistForm()
    if form.validate():

        try:
            newArtist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                website=form.website_link.data,
                image_link=form.image_link.data,
                facebook_link = form.facebook_link.data, 
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data)

            db.session.add(newArtist)
            db.session.commit()
            flash(f'Artist {form.name.data} was successfully listed!')
        except:
            db.session.rollback()
            flash(f'An error occurred. Artist {form.name.data} could not be listed.')
        finally:
            db.session.close()
    else:
      message = []
      for field, err in form.errors.items():
           message.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(message)}')
    return render_template('pages/home.html')
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = Show.query.order_by('id').all()
    data = []
    for row in shows:
        show_info = {}
        show_info['venue_id'] = row.venue_id
        show_info['venue_name'] = row.venue.name
        show_info['artist_id'] = row.artist_id
        show_info['artist_name'] = row.artist.name
        show_info['artist_image_link'] = row.artist.image_link
        show_info['start_time'] = format_datetime(row.start_time)
        print(type(show_info['start_time']))
        data.append(show_info)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm()
    if form.validate():

        try:
            newShow = Show(
                venue_id=form.venue_id.data,
                artist_id=form.artist_id.data,
                start_time=form.start_time.data)
            db.session.add(newShow)
            db.session.commit()
            flash('Show was successfully listed!')
        except:
            db.session.rollback()
            print(sys.exec_info())
            flash(f'An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
      message = []
      for field, err in form.errors.items():
           message.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(message)}')

    return render_template('pages/home.html')



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
