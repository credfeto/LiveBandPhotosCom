import webapp2
import json
import hashlib
import urllib2
from collections import defaultdict 

import datetime

from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import urlfetch 

import xml.etree.ElementTree as ET


import models
import utils

class TaskSyncHandler(webapp2.RequestHandler):
    def get(self):

        url = 'http://admin.livebandphotos.co.uk/transfer.php'
        #url = 'http://localhost/GalleryMetadata/transfer.xml'

        result = urlfetch.fetch(url);
        if result.status_code == 200:

            today = datetime.date.today()
            now = datetime.datetime.now()

            bands = []
            venues = []

            root = ET.fromstring( result.content )

            self.response.headers['Content-Type'] = "text/plain"
            
            itemsWritten = 0
            itemsRemoved = 0
            self.response.out.write( 'Gigs\n')
            found = 0
            bandsXml = root.findall(".//table[@name='tempgig']/records/record")
            for gigXml in bandsXml:
                found = found + 1

                id = gigXml.find('id').text
                bandname = gigXml.find('bandname').text
                venuename = gigXml.find('venuename').text
                gigDateRaw = gigXml.find('gigdate').text
                
                parsedId = int(id, 10)
                parsedDate = utils.isoparse(gigDateRaw)
                if parsedDate <> None and parsedDate >= today:
                    
                    self.response.out.write( parsedId )
                    self.response.out.write( '\t')
                    self.response.out.write( bandname )
                    self.response.out.write( '\t')
                    self.response.out.write( venuename )
                    self.response.out.write( '\t')
                    self.response.out.write( gigDateRaw )
                    self.response.out.write( '\t')
                    self.response.out.write( parsedDate )
                    self.response.out.write( '\n') 
                    
                    gig = models.Gig.query(models.Gig.id == parsedId).get()
                    if gig is None:
                        gig = models.Gig(
                                         id = parsedId,
                                         band = bandname,
                                         venue = venuename,
                                         date = parsedDate,
                                         updated = now)
                        gig.put()
                        
                        itemsWritten = itemsWritten + 1
                    else:
                        if gig.band <> bandname or gig.venue <> venuename or gig.date <> parsedDate:
                            # ideally don't want to update things that are not changing.
                            gig.band = bandname
                            gig.venue = venuename
                            gig.date = parsedDate

                        gig.updated = now
                        gig.put()

                        itemsWritten = itemsWritten + 1
    

            if found  > 0 :
                toDelete = models.Gig.query( models.Gig.updated < now ).fetch()
                for dbItem in toDelete:
                    dbItem.key.delete()
                    itemsRemoved = itemsRemoved + 1

            self.response.out.write("\n\n")
            self.response.out.write("Items Found : " + str(found))
            self.response.out.write("\n")
            self.response.out.write("Items Written : " + str(itemsWritten))
            self.response.out.write("\n")
            self.response.out.write("Items Removed : " + str(itemsRemoved))
            self.response.out.write("\n")
            self.response.out.write("OK")
        else:
            self.response.headers['Content-Type'] = "text/plain"
            self.response.out.write("ERROR")


app = webapp2.WSGIApplication([
    ('/tasks/sync', TaskSyncHandler)
])
