import datetime
import webapp2
import utils
import models
from google.appengine.ext import ndb

class MainHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()
        hash = utils.generate_url_hash(searchPath)

        startDate = datetime.date.today()
        endDate = startDate + datetime.timedelta(days=10)

        dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.date <= endDate).order(models.Gig.date).fetch()

        gigs = []
        for dbGig in dbGigs:
            bandUrl = utils.make_url('/band/' + dbGig.band)
            venueUrl = utils.make_url('/venue/' + dbGig.venue)

            gig = { 'band' : dbGig.band, 'bandUrl': bandUrl, 'when' : dbGig.date, 'venue': dbGig.venue, 'venueUrl': venueUrl }
            gigs.append(gig)

        template_vals = { 'path': searchPath, 'track': track, 'hash' : hash, 'gigs' : gigs }
        self.response.out.write(utils.render_template("main.html", template_vals))

class BandHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()
        hash = utils.generate_url_hash(searchPath)

        template_vals = { 'path': searchPath, 'track': track, 'hash' : hash }
        self.response.out.write(utils.render_template("band.html", template_vals))

class VenueHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        searchPath = self.request.path.lower()
        hash = utils.generate_url_hash(searchPath)

        template_vals = { 'path': searchPath, 'track': track, 'hash' : hash }
        self.response.out.write(utils.render_template("venue.html", template_vals))

app = webapp2.WSGIApplication([
    ('/venue/[\w\-]*/', VenueHandler),
    ('/band/[\w\-]*/', BandHandler),
    ('/', MainHandler)
], debug=True)
