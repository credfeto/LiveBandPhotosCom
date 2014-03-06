import datetime
import webapp2
import utils
import models
from google.appengine.ext import ndb
from google.appengine.api import capabilities
from google.appengine.api import memcache

class SiteMapSectionHandler(webapp2.RequestHandler):
    def get(self):

        memcacheEnabled = capabilities.CapabilitySet('memcache').is_enabled()

        expiry_seconds = 60 * 60 * 12
        memcachedKey = 'sitemap-output'
        output = ''

        if memcacheEnabled:
            try:
                output = memcache.get(memcachedKey)
            except KeyError:
                output = ''

        if output is None or len(output) == 0:

            today = datetime.date.today()
            when = datetime.datetime.now()

            

            items = []
            items.append( { 'path' : '/', 'lastmod' : today } )

            bands = models.Band.query()
            for band in bands:
                items.append( { 'path' : band.url, 'lastmod' : band.updated } )

            venues = models.Venue.query()
            for venue in venues:
                items.append( { 'path' : venue.url, 'lastmod' : venue.updated } )

            template_vals = {'items' : items, 'host' : self.request.host_url }

            output = utils.render_template("sitemap.html", template_vals)
        
            if memcacheEnabled:    
                memcache.set(memcachedKey, output, expiry_seconds)

        self.response.headers['Cache-Control'] = 'public,max-age=%d' % 86400
        self.response.headers['Pragma'] = 'public'
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(output)


app = webapp2.WSGIApplication([
    ('/sitemap', SiteMapSectionHandler)
], debug=True)
