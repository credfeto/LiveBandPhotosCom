import datetime
import webapp2

from google.appengine.api import mail
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import blobstore


class Band(ndb.Model):
    id = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(auto_now=True)

class Venue(ndb.Model):
    id = ndb.IntegerProperty(required=True)
    name = ndb.StringProperty(required=True)
    updated = ndb.DateTimeProperty(auto_now=True)

class Gig(ndb.Model):
    id = ndb.IntegerProperty(required=True)
    band = ndb.StringProperty(required=True)
    venue = ndb.StringProperty(required=True)
    date = ndb.DateProperty(required=True)
    updated = ndb.DateTimeProperty(required=True)
