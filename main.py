import datetime
import webapp2
import utils
import models
from google.appengine.ext import ndb


class MainHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track(self.request.headers)

        search_path = self.request.path.lower()

        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=10)

        db_gigs = models.Gig.query(models.Gig.date >= start_date and models.Gig.date <= end_date).order(
            models.Gig.date).fetch()

        gigs = []
        for db_gig in db_gigs:

            if db_gig.date >= start_date and models.Gig.date <= end_date:
                band_url = utils.make_band_url(db_gig.band)
                venue_url = utils.make_venue_url(db_gig.venue)

                gig = {'band': db_gig.band, 'band_url': band_url, 'when': db_gig.date, 'venue': db_gig.venue,
                       'venue_url': venue_url}
                gigs.append(gig)

        template_vals = {'path': search_path, 'track': track, 'hash': hash, 'gigs': gigs}
        midnight = start_date + datetime.timedelta(days=1)
        now = datetime.datetime.now()
        utils.set_cache_headers_expire(self.response.headers, now, midnight)
        self.response.out.write(utils.render_template("main.html", template_vals))


class BandHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track(self.request.headers)

        band_url = self.request.path
        band = models.Band.query(models.Band.url == band_url).get()
        if band is None:
            should_report_error = True
            new_search_path = utils.make_url(band_url)
            band = models.Band.query(models.Band.url == new_search_path).get()
            if band is not None:
                should_report_error = False
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(new_search_path, self.request.query_string), permanent=True)

            if should_report_error:
                template_vals = {'path': band_url, 'suggestedPath': new_search_path, 'track': track, 'hash': hash,
                                 'showShare': False}
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404)

        else:
            start_date = datetime.date.today()
            db_gigs = models.Gig.query(models.Gig.date >= start_date and models.Gig.band == band.name).order(
                models.Gig.date).fetch()

            gigs = []
            for dbGig in db_gigs:
                if dbGig.date >= start_date:
                    venue_url = utils.make_venue_url(dbGig.venue)

                    gig = {'when': dbGig.date, 'venue': dbGig.venue, 'venue_url': venue_url}
                    gigs.append(gig)

            template_vals = {'path': band_url, 'track': track, 'band': band.name, 'gigs': gigs}
            midnight = start_date + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire(self.response.headers, now, midnight)
            self.response.out.write(utils.render_template("band.html", template_vals))


class VenueHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track(self.request.headers)

        venue_url = self.request.path
        venue = models.Venue.query(models.Venue.url == venue_url).get()
        if venue is None:
            should_report_error = True
            new_search_path = utils.make_url(venue)
            venue = models.Venue.query(models.Venue.url == new_search_path).get()
            if venue is not None:
                should_report_error = False
                self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
                self.response.headers['Pragma'] = 'public'
                self.redirect(utils.redirect_url(new_search_path, self.request.query_string), permanent=True)

            if should_report_error:
                template_vals = {'path': venue, 'suggestedPath': new_search_path, 'track': track, 'hash': hash,
                                 'showShare': False}
                self.response.out.write(utils.render_template("notfound.html", template_vals))
                self.response.set_status(404)

        else:
            start_date = datetime.date.today()
            db_gigs = models.Gig.query(models.Gig.date >= start_date and models.Gig.venue == venue.name).order(
                models.Gig.date).fetch()

            gigs = []
            for db_gig in db_gigs:
                if db_gig.date >= start_date:
                    band_url = utils.make_band_url(db_gig.band)

                    gig = {'when': db_gig.date, 'band': db_gig.band, 'band_url': band_url}
                    gigs.append(gig)

            template_vals = {'path': venue, 'track': track, 'venue': venue.name, 'gigs': gigs}

            midnight = start_date + datetime.timedelta(days=1)
            now = datetime.datetime.now()
            utils.set_cache_headers_expire(self.response.headers, now, midnight)
            self.response.out.write(utils.render_template("venue.html", template_vals))


class CalendarHandler(webapp2.RequestHandler):
    def get(self):
        town = 'Harlow'

        town = town.lower()
        start_date = datetime.date.today()
        db_gigs = models.Gig.query(models.Gig.date >= start_date).order(models.Gig.date).fetch()

        date_test = start_date.strftime('%Y%m%d')

        midnight = start_date + datetime.timedelta(days=1)
        now = datetime.datetime.now()
        utils.set_cache_headers_expire(self.response.headers, now, midnight)
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write('BEGIN:VCALENDAR\r\n')
        self.response.out.write('VERSION:2.0\r\n')
        self.response.out.write('PRODID:-//livebandphotos.com//Gig Calendar 1.0//EN\r\n')
        self.response.out.write('CALSCALE:GREGORIAN\r\n')
        self.response.out.write('METHOD:PUBLISH\r\n')

        ids = []
        for db_gig in db_gigs:

            if db_gig.date >= start_date:

                if db_gig.venue.lower().endswith(', ' + town.lower()):
                    band_url = utils.make_band_url(db_gig.band)
                    venue_url = utils.make_venue_url(db_gig.venue)

                    when = db_gig.date
                    date_formatted = when.strftime('%Y%m%d')
                    id = date_formatted + '.' + utils.make_venue_fragment(
                            db_gig.venue) + '@livebandphotos.com'

                    if id not in ids:
                        ids.append(id);

                        self.response.out.write('BEGIN:VEVENT\r\n')

                        self.response.out.write(
                            'UID:' + id + '\r\n')
                        self.response.out.write('DTSTAMP:' + date_formatted + 'T210000Z\r\n')
                        self.response.out.write('DTSTART:' + date_formatted + 'T210000Z\r\n')
                        self.response.out.write('DTEND:' + date_formatted + 'T235959Z\r\n')
                        self.response.out.write('SUMMARY:' + db_gig.band + ' at ' + db_gig.venue + '\r\n')
                        self.response.out.write('CLASS:PUBLIC\r\n')
                        self.response.out.write('CATEGORIES:GIG,MUSIC\r\n')
                        self.response.out.write(
                            'DESCRIPTION:Whilst every effort is made to make the gig lists on this website as accurate as possible on a website of this size the occasional mistake is bound to slip in. Also occasionally bands change at short notice. Please double check by phoning the pub or visiting the bands own website.\r\n')

                        self.response.out.write('END:VEVENT\r\n')

        self.response.out.write('END:VCALENDAR\r\n')



app = webapp2.WSGIApplication([
    ('/[Vv][Ee][Nn][Uu][Ee]/[\w\-\s,\.]*/', VenueHandler),
    ('/[Bb][Aa][Nn][Dd]/[\w\-\s,\.]*/', BandHandler),
    ('/calendar/harlow\.ics', CalendarHandler),
    ('/', MainHandler)
], debug=True)
