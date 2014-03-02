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

            if dbGig.date >= startDate and dbGig.date <= endDate:
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

        bandurl = self.request.path
        band = models.Band.query(models.Band.url == bandurl).get()
        if band is None:
            shouldReportError = True
            newSearchPath = utils.make_url(bandurl)
            band = models.Band.query(models.Band.url == newSearchPath).get()
            if band <> None:
                shouldReportError = False
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(newSearchPath, self.request.query_string), permanent=True)

            if shouldReportError:
                template_vals = { 'path': bandurl, 'suggestedPath' : newSearchPath, 'track': track, 'hash' : hash, 'showShare': False }
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404) 

        else:
            startDate = datetime.date.today()
            dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.band == band.name).order(models.Gig.date).fetch()

            gigs = []
            for dbGig in dbGigs:
                if dbGig.date >= startDate:
                    venueUrl = utils.make_venue_url(dbGig.venue)

                    gig = { 'when' : dbGig.date, 'venue': dbGig.venue, 'venueUrl': venueUrl }
                    gigs.append(gig)

            template_vals = { 'path': bandurl, 'track': track, 'band' : band.name, 'gigs' : gigs }
            midnight = startDate + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire( self.response.headers, now, midnight )
            self.response.out.write(utils.render_template("band.html", template_vals))

class VenueHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track( self.request.headers )

        venueurl = self.request.path
        venue = models.Venue.query(models.Venue.url == venueurl).get()
        if venue is None:
            shouldReportError = True
            newSearchPath = utils.make_url(venueurl)
            venue = models.Venue.query(models.Venue.url == newSearchPath).get()
            if venue <> None:
                shouldReportError = False
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(newSearchPath, self.request.query_string), permanent=True)

            if shouldReportError:
                template_vals = { 'path': venueurl, 'suggestedPath' : newSearchPath, 'track': track, 'hash' : hash, 'showShare': False }
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404) 

        else:
            startDate = datetime.date.today()
            dbGigs = models.Gig.query(models.Gig.date >= startDate and models.Gig.venue == venue.name).order(models.Gig.date).fetch()

            gigs = []
            for dbGig in dbGigs:
                if dbGig.date >= startDate:
                    bandUrl = utils.make_band_url(dbGig.band)

                    gig = { 'when' : dbGig.date, 'band': dbGig.band, 'bandUrl': bandUrl }
                    gigs.append(gig)

            template_vals = { 'path': venueurl, 'track': track, 'venue' : venue.name, 'gigs' : gigs }
            
            midnight = startDate + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire( self.response.headers, now, midnight )
            self.response.out.write(utils.render_template("venue.html", template_vals))

app = webapp2.WSGIApplication([
    ('/[Vv][Ee][Nn][Uu][Ee]/[\w\-\s,\.]*/', VenueHandler),
    ('/[Bb][Aa][Nn][Dd]/[\w\-\s,\.]*/', BandHandler),
    ('/', MainHandler)
], debug=True)
