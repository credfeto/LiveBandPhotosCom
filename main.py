import datetime

import webapp2

import models
import utils


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
        utils.set_cache_headers_expire(self.response.headers, midnight)
        self.response.out.write(utils.render_template("main.html", template_vals))


class BandHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track(self.request.headers)

        band_url = self.request.path
        band = models.Band.query(models.Band.url == band_url).get()
        if band is None:
            template_vals = {'path': band_url, 'suggestedPath': band_url, 'track': track, 'hash': hash,
                             'showShare': False}
            self.response.out.write(utils.render_template("notfound.html", template_vals))
            self.response.set_status(404)

        else:
            start_date = datetime.date.today()
            db_gigs = models.Gig.query(models.Gig.date >= start_date and models.Gig.band == band.name).order(
                models.Gig.date).fetch()

            gigs = []
            for db_gig in db_gigs:
                if db_gig.date >= start_date:
                    venue_url = utils.make_venue_url(db_gig.venue)

                    gig = {'when': db_gig.date, 'venue': db_gig.venue, 'venue_url': venue_url}
                    gigs.append(gig)

            template_vals = {'path': band_url, 'track': track, 'band': band.name, 'gigs': gigs}
            midnight = start_date + datetime.timedelta(days=1)
            utils.set_cache_headers_expire(self.response.headers, midnight)
            self.response.out.write(utils.render_template("band.html", template_vals))


class VenueHandler(webapp2.RequestHandler):
    def get(self):
        track = utils.should_track(self.request.headers)

        venue_url = self.request.path
        venue = models.Venue.query(models.Venue.url == venue_url).get()
        if venue is None:
            template_vals = {'path': venue, 'suggestedPath': venue_url, 'track': track, 'hash': hash,
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
            utils.set_cache_headers_expire(self.response.headers, midnight)
            self.response.out.write(utils.render_template("venue.html", template_vals))


class CalendarHandler(webapp2.RequestHandler):
    def get(self):
        town = 'Harlow'

        town = town.lower()
        start_date = datetime.date.today()
        db_gigs = models.Gig.query(models.Gig.date >= start_date).order(models.Gig.date).fetch()

        midnight = start_date + datetime.timedelta(days=1)
        utils.set_cache_headers_expire(self.response.headers, midnight)
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

                    when = db_gig.date
                    start_time = utils.get_start_time(when)
                    end_time = utils.get_end_time(when)

                    start_date_formatted = start_time.strftime('%Y%m%dT%H%M:%sZ')
                    end_date_formatted = end_time.strftime('%Y%m%dT%H%M:%sZ')
                    id = start_date_formatted + '.' + utils.make_venue_fragment(
                            db_gig.venue) + '@livebandphotos.com'

                    if id not in ids:
                        ids.append(id);

                        self.response.out.write('BEGIN:VEVENT\r\n')

                        self.response.out.write(
                            'UID:' + id + '\r\n')
                        self.response.out.write('DTSTAMP:' + start_date_formatted + '\r\n')
                        self.response.out.write('DTSTART:' + start_date_formatted + '\r\n')
                        self.response.out.write('DTEND:' + end_date_formatted + '\r\n')
                        self.response.out.write('SUMMARY:' + db_gig.band + ' at ' + db_gig.venue + '\r\n')
                        self.response.out.write('CLASS:PUBLIC\r\n')
                        self.response.out.write('CATEGORIES:GIG,MUSIC\r\n')
                        # self.response.out.write(
                        #    'DESCRIPTION:Whilst every effort is made to make the gig lists on this website as accurate as possible on a website of this size the occasional mistake is bound to slip in.\nAlso occasionally bands change at short notice.\n\nPlease double check by phoning the pub or visiting the bands own website.\r\n')

                        self.response.out.write('END:VEVENT\r\n')

        self.response.out.write('END:VCALENDAR\r\n')



app = webapp2.WSGIApplication([
    ('/[Vv][Ee][Nn][Uu][Ee]/[\w\-\s,\.]*/', VenueHandler),
    ('/[Bb][Aa][Nn][Dd]/[\w\-\s,\.]*/', BandHandler),
    ('/calendar/harlow\.ics', CalendarHandler),
    ('/', MainHandler)
], debug=True)
