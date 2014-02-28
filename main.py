import datetime
import webapp2
import utils
import models
from google.appengine.ext import ndb

class MainHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()

        startDate = datetime.date.today()
        endDate = startDate + datetime.timedelta(days=10)

        dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.date <= endDate).order(models.Gig.date).fetch()

        gigs = []
        for dbGig in dbGigs:
            bandUrl = utils.make_band_url(dbGig.band)
            venueUrl = utils.make_venue_url(dbGig.venue)

            gig = { 'band' : dbGig.band, 'bandUrl': bandUrl, 'when' : dbGig.date, 'venue': dbGig.venue, 'venueUrl': venueUrl }
            gigs.append(gig)

        template_vals = { 'path': searchPath, 'track': track, 'hash' : hash, 'gigs' : gigs }
        midnight = startDate + datetime.timedelta(days=1)
        now = datetime.datetime.now()
        utils.set_cache_headers_expire( self.response.headers, now, midnight )
        self.response.out.write(utils.render_template("main.html", template_vals))

class BandHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()
        bandurl = utils.make_url(searchPath)
        
        band = models.Band.query(models.Band.url == bandurl).get()
        if band is None:
            self.response.set_status(404) 
        else:
            startDate = datetime.date.today()
            dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.band == band.name).order(models.Gig.date).fetch()

            gigs = []
            for dbGig in dbGigs:
                venueUrl = utils.make_venue_url(dbGig.venue)

                gig = { 'when' : dbGig.date, 'venue': dbGig.venue, 'venueUrl': venueUrl }
                gigs.append(gig)

            template_vals = { 'path': searchPath, 'track': track, 'band' : band.name, 'gigs' : gigs }
            midnight = startDate + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire( self.response.headers, now, midnight )
            self.response.out.write(utils.render_template("band.html", template_vals))

class VenueHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()
        venueurl = utils.make_url(searchPath)
        
        venue = models.Venue.query(models.Venue.url == venueurl).get()
        if venue is None:
            self.response.set_status(404) 
        else:
            startDate = datetime.date.today()
            dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.venue == venue.name).order(models.Gig.date).fetch()

            gigs = []
            for dbGig in dbGigs:
                bandUrl = utils.make_band_url(dbGig.band)

                gig = { 'when' : dbGig.date, 'band': dbGig.band, 'bandUrl': bandUrl }
                gigs.append(gig)

            template_vals = { 'path': searchPath, 'track': track, 'venue' : venue.name, 'gigs' : gigs }
            
            midnight = startDate + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire( self.response.headers, now, midnight )
            self.response.out.write(utils.render_template("venue.html", template_vals))

app = webapp2.WSGIApplication([
    ('/venue/[\w\-]*/', VenueHandler),
    ('/band/[\w\-]*/', BandHandler),
    ('/', MainHandler)
], debug=True)
