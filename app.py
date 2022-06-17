#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from enum import unique
import dateutil.parser
import babel
from flask import(
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
from sqlalchemy import Column, Integer, func
import logging
from flask_bootstrap import Bootstrap
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
import sys
import os
from config import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)  # Just initiate it here.
migrate = Migrate(app, db)
app.config['WTF_CSRF_ENABLED'] = False




# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# models in models.py
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
    realVenue = {}
    for cities in Venue.query.all():
        city = cities.city
        if city not in realVenue :
            realVenue [city] = {}
            realVenue [city]['city'] = city
            realVenue [city]['state'] = cities.state
            realVenue [city]['venues'] = []
        venueData = {}
        venueData['id'] = cities.id
        venueData['name'] = cities.name
        upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).all()
        venueData['num_upcoming_shows'] = len(upcoming_shows)
        realVenue[city]['venues'].append(venueData)

    return render_template('pages/venues.html', areas=realVenue.values());


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    string_search = request.form.get('search_term', '')
    search_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{string_search}%')).all()

    response = {}
    response['count'] = len(search_results)
    response['data'] = []
    for venues in search_results:
        venueInfo = {}
        venueInfo['id'] = venues.id
        venueInfo['name'] = venues.name
        upcoming_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).all()
        venueInfo['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(venueInfo)

    return render_template('pages/search_venues.html', results=response, search_term=string_search)
    
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

    past_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).filter(Show.start_time < datetime.now()).order_by(Show.start_time).all()

    venue_data['past_shows_count'] = len(past_shows)
    for past in past_shows:
        past_count_info = {}
        past_count_info['artist_id'] = past.artist_id
        past_count_info['artist_name'] = past.artist.name
        past_count_info['artist_image_link'] = past.artist.image_link
        past_count_info['start_time'] = past.start_time
        venue_data['past_shows'].append(past_count_info)

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
    Form = VenueForm(request.form)
    return render_template('forms/new_venue.html', form=Form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    if form.validate():
        try:

            create_venue = Venue(
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

            db.session.add(create_venue)
            db.session.commit()
            flash(f'Venue listing... successfully!')
        except:
            db.session.rollback()
            flash(f'An error occurred. could not be listed.')
        finally:
            db.session.close()
    else:
      display = []
      for field, ERR in form.errors.items():
           display.append(f"{field} {'|'.join(ERR)}")
      flash(f'Errors {str(display)}')
    return render_template('pages/home.html')

   
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    
    try:
        delete_venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(delete_venue)
        db.session.commit()
        flash('Venue has been deleting... deleted!.')
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
    
    edited_form = Venue.query.get(venue_id)
    venue = {}
    venue['id'] = edited_form.id
    venue['name'] = edited_form.name
    venue['genres'] = edited_form.genres
    venue['address'] = edited_form.address
    venue['city'] = edited_form.city
    venue['state'] = edited_form.state
    venue['phone'] = edited_form.phone
    venue['website'] = edited_form.website
    venue['facebook_link'] = edited_form.facebook_link
    venue['seeking_talent'] = edited_form.seeking_talent
    venue['seeking_description'] = edited_form.seeking_description
    venue['image_link'] = edited_form.image_link

    form.name.data = edited_form.name
    form.genres.data = edited_form.genres
    form.address.data = edited_form.address
    form.city.data = edited_form.city
    form.state.data = edited_form.state
    form.phone.data = edited_form.phone
    form.website_link.data = edited_form.website
    form.facebook_link.data = edited_form.facebook_link
    form.seeking_talent.data = edited_form.seeking_talent
    form.seeking_description.data = edited_form.seeking_description
    form.image_link.data = edited_form.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
  
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists_query= Artist.query.order_by('id').all()
    data = []
    for artist in artists_query:
        artist_data = {}
        artist_data['id'] = artist.id
        artist_data['name'] = artist.name
        data.append(artist_data)

    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_search = request.form.get('search_term', '')
    response = {}
    artist_found = db.session.query(Artist).filter(Artist.name.ilike(f'%{artist_search}%')).all()

    response = {}
    response['count'] = len(artist_found)
    response['data'] = []
    for artist in artist_found:
        artist_data = {}
        artist_data['id'] = artist.id
        artist_data['name'] = artist.name
        upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.now()).all()
        artist_data['num_upcoming_shows'] = len(upcoming_shows)
        response['data'].append(artist_data)

    return render_template('pages/search_artists.html', results=response, search_term=artist_search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist_data = {}
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    artist_data['genres'] = artist.genres
    artist_data['city'] = artist.city
    artist_data['state'] = artist.state
    artist_data['phone'] = artist.phone
    artist_data['website'] = artist.website
    artist_data['facebook_link'] = artist.facebook_link
    artist_data['seeking_venue'] = artist.seeking_venue
    if artist.seeking_venue:
        artist_data['seeking_description'] = artist.seeking_description
    artist_data['image_link'] = artist.image_link

    artist_data['past_shows'] = []
    artist_data['upcoming_shows'] = []

    past_shows = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).order_by(Show.start_time).all()

    artist_data['past_shows_count'] = len(past_shows)
    for past_count in past_shows:
        show_data = {}
        show_data['venue_id'] = past_count.venue_id
        show_data['venue_name'] = past_count.venue.name
        show_data['venue_image_link'] = past_count.venue.image_link
        show_data['start_time'] = past_count.start_time
        artist_data['past_shows'].append(show_data)

    upcoming_shows = Show.query.filter(Show.artist_id == artist_id)\
        .filter(Show.start_time > datetime.now()).order_by(Show.start_time).all()
    artist_data['upcoming_shows_count'] = len(upcoming_shows)
    for upcoming_count in upcoming_shows:
        show_data = {}
        show_data['venue_id'] = upcoming_count.venue_id
        show_data['venue_name'] = upcoming_count.venue.name
        show_data['venue_image_link'] = upcoming_count.venue.image_link
        show_data['start_time'] = upcoming_count.start_time
        artist_data['upcoming_shows'].append(show_data)

    return render_template('pages/show_artist.html', artist=artist_data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    edit_artist = ArtistForm()
    artist_info = Artist.query.get(artist_id)
    artist = {}
    artist['id'] =artist_info.id
    artist['name'] = artist_info.name
    artist['genres'] = artist_info.genres
    artist['city'] = artist_info.city
    artist['state'] = artist_info.state
    artist['phone'] = artist_info.phone
    artist['website'] = artist_info.website
    artist['facebook_link'] = artist_info.facebook_link
    artist['seeking_venue'] = artist_info.seeking_venue
    artist['seeking_description'] = artist_info.seeking_description
    artist['image_link'] = artist_info.image_link

    edit_artist.name.data = artist_info.name
    edit_artist.genres.data = artist_info.genres
    edit_artist.city.data = artist_info.city
    edit_artist.state.data = artist_info.state
    edit_artist.phone.data = artist_info.phone
    edit_artist.website_link.data = artist_info.website
    edit_artist.facebook_link.data = artist_info.facebook_link
    edit_artist.seeking_venue.data = artist_info.seeking_venue
    edit_artist.seeking_description.data = artist_info.seeking_description
    edit_artist.image_link.data = artist_info.image_link

    return render_template('forms/edit_artist.html', form=edit_artist, artist=artist)

    
    # TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist_form_validation = ArtistForm()
    if artist_form_validation.validate():
        artist = Artist.query.get(artist_id)
        try:
            artist.name=artist_form_validation.name.data
            artist.city=artist_form_validation.city.data
            artist.state=artist_form_validation.state.data
            artist.phone=artist_form_validation.phone.data
            artist.genres=artist_form_validation.genres.data
            artist.website=artist_form_validation.website_link.data
            artist.image_link=artist_form_validation.image_link.data
            artist.facebook_link = artist_form_validation.facebook_link.data
            artist.seeking_venue=artist_form_validation.seeking_venue.data
            artist.seeking_description=artist_form_validation.seeking_description.data
            db.session.commit()
            flash(f'updating {artist.name}...\n {artist.name} updated success!')
        except:
            db.session.rollback()
            print(sys.exc_info())

            flash(f'updating {artist.name}... \ncould not be updated.')
        finally:
            db.session.close()
    else:
      display = []
      for field, error in artist_form_validation.errors.items():
           display.append(f"{field} {'|'.join(error)}")
      flash(f'Errors {str(display)}')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
 
    edit_form = VenueForm()
    if edit_form.validate():

        query_venue = Venue.query.get(venue_id)

        try:
            query_venue.name=edit_form.name.data
            query_venue.address=edit_form.address.data
            query_venue.city=edit_form.city.data
            query_venue.state=edit_form.state.data
            query_venue.phone=edit_form.phone.data
            query_venue.genres=edit_form.genres.data
            query_venue.website=edit_form.website_link.data
            query_venue.image_link=edit_form.image_link.data
            query_venue.facebook_link = edit_form.facebook_link.data
            query_venue.seeking_talent=edit_form.seeking_talent.data
            query_venue.seeking_description=edit_form.seeking_description.data
            db.session.commit()
            flash(f'Editing venue... {query_venue.name} successfully updated!')
        except:
            db.session.rollback()
            flash(f'AEditing venue... {query_venue.name} failed to update.')
        finally:
            db.session.close()
    else:
      display = []
      for field, err in edit_form.errors.items():
           display.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(display)}')
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
    createArtistForm = ArtistForm(request.form)
    if createArtistForm.validate():

        try:
            newArtist = Artist(
                name=createArtistForm.name.data,
                city=createArtistForm.city.data,
                state=createArtistForm.state.data,
                phone=createArtistForm.phone.data,
                genres=createArtistForm.genres.data,
                website=createArtistForm.website_link.data,
                image_link=createArtistForm.image_link.data,
                facebook_link = createArtistForm.facebook_link.data, 
                seeking_venue=createArtistForm.seeking_venue.data,
                seeking_description=createArtistForm.seeking_description.data)

            db.session.add(newArtist)
            db.session.commit()
            flash(f'Artist {createArtistForm.name.data} was successfully listed!')
        except:
            db.session.rollback()
            flash(f'Artist {createArtistForm.name.data} could not be listed.')
        finally:
            db.session.close()
    else:
      display = []
      for field, err in createArtistForm.errors.items():
           display.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(display)}')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    ListOfShows = Show.query.order_by('id').all()
    ShowData = []
    for shows in ListOfShows:
        show = {}
        show['venue_id'] = shows.venue_id
        show['venue_name'] = shows.venue.name
        show['artist_id'] = shows.artist_id
        show['artist_name'] = shows.artist.name
        show['artist_image_link'] = shows.artist.image_link
        show['start_time'] = format_datetime(shows.start_time)
        print(type(show['start_time']))
        ShowData.append(show)

    return render_template('pages/shows.html', shows=ShowData)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    showForm = ShowForm(request.form)
    if showForm.validate():

        try:
            created_Show = Show(
                venue_id=showForm.venue_id.data,
                artist_id=showForm.artist_id.data,
                start_time=showForm.start_time.data)
            db.session.add(created_Show)
            db.session.commit()
            flash('creating Show... successfully listed!')
        except:
            db.session.rollback()
            print(sys.exec_info())
            flash(f'Show could not be listed.')
        finally:
            db.session.close()
    else:
      display = []
      for field, err in showForm.errors.items():
           display.append(f"{field} {'|'.join(err)}")
      flash(f'Errors {str(display)}')

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
