import datetime
import webapp2
import utils
import models
from google.appengine.ext import ndb

class CalendarHandler(webapp2.RequestHandler):
    def get(self):
        town = 'Harlow'

        town = town.lower()
        start_date = datetime.date.today()
        db_gigs = models.Gig.query(models.Gig.date >= start_date).order(models.Gig.date).fetch()

        gigs = []
        for db_gig in db_gigs:

            if db_gig.date >= startDat:

                if db_gig.venue.lower().endswith(', ' + town.lower()):

                    band_url = utils.make_band_url(dbGig.band)
                    venue_url = utils.make_venue_url(dbGig.venue)

                    gig = { 'band' : db_gig.band, 'bandUrl': band_url, 'when' : db_gig.date, 'venue': db_gig.venue, 'venueUrl': venue_url }
                    gigs.append(gig)

        now = datetime.datetime.now()
        utils.set_cache_headers_expire(self.response.headers, now, midnight)
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write('BEGIN:VCALENDAR')
        self.response.out.write('VERSION:2.0')
        self.response.out.write('PRODID:-//livebandphotos.com//Gig Calendar 1.0//EN')
        self.response.out.write('CALSCALE:GREGORIAN')
        self.response.out.write('METHOD:PUBLISH')

        for gig in gigs:
            when = gig.date
            self.response.out.write('BEGIN:VEVENT')

            self.response.out.write('UID:' + when.strftime('%Y%M%D') +'.'+ utils.make_venue_fragment(gig.venue) + '@livebandphotos.com')
            self.response.out.write('DTSTAMP:' + when.strftime('%Y%M%D') + 'T210000Z')
            self.response.out.write('DTSTART' + when.strftime('%Y%M%D') + 'T210000Z')
            self.response.out.write('DTEND:' + when.strftime('%Y%M%D') +  'T235959Z')
            self.response.out.write('SUMMARY:' + gig.band + ' + at ' + gig.venue)
            self.response.out.write('END:VEVENT')

        self.response.out.write('END:VCALENDAR')


app = webapp2.WSGIApplication([
    ('.*', CalendarHandler)
], debug=True)
