import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import blobstore


class Band(ndb.Model):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(required=True)

class Venue(ndb.Model):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(required=True)

class Gig(ndb.Model):
    id = ndb.IntegerProperty(required=True)
    band = ndb.StringProperty(required=True)
    venue = ndb.StringProperty(required=True)
    date = ndb.DateProperty(required=True)
    updated = ndb.DateTimeProperty(required=True)
