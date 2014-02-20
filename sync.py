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

def sync_now( url ):
    result = urlfetch.fetch(url = url, deadline = 120)
    if result.status_code == 200:

        process_content( result.content )



def process_content( content ):

    today = datetime.date.today()
    now = datetime.datetime.now()

    bands = []
    venues = []

    root = ET.fromstring( content )

    itemsWritten = 0
    itemsRemoved = 0
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
                    
            #self.response.out.write( parsedId )
            #self.response.out.write( '\t')
            #self.response.out.write( bandname )
            #self.response.out.write( '\t')
            #self.response.out.write( venuename )
            #self.response.out.write( '\t')
            #self.response.out.write( gigDateRaw )
            #self.response.out.write( '\t')
            #self.response.out.write( parsedDate )
            #self.response.out.write( '\n') 
                    
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

