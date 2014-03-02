import os
import datetime
import hashlib
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

def should_track( headers ):

    track = headers.get('DNT', "0")

    if track is None:
        return True

    if track == "1":
        return False

    return True

def isoparse(s):
    try:
        year =  s[0:4]
        month = s[5:7]
        day = s[8:10]
        numericYear = int(year, 10)
        if numericYear < 2000:
            return None

        return datetime.date( numericYear, int(month,10),int(day, 10) )
    except:
        return None

def make_url( originalPath ):

    base = originalPath.lower()
    
    root =  base.strip();
    
    replacedEncodedSpace = root.replace("%20", "-" )
    replacedWrongSlash = replacedEncodedSpace
    replacedDuplicateHyphens = re.sub(r"[^a-z0-9\-/]", "-", replacedWrongSlash)
    replacedBadChars = re.sub(r"(\-{2,})", "-", replacedDuplicateHyphens )
    replacedEndingHyphens = replacedBadChars.rstrip('-') 

    if replacedEndingHyphens.endswith( '/' ) == False:
        replacedEndingHyphens = replacedEndingHyphens + '/'

    return replacedEndingHyphens

def make_band_url(name):
   return make_url('/band/' + name)

def make_venue_url(name):
    return make_url('/venue/' + name)

def is_development():
    env = os.environ['SERVER_SOFTWARE']

    return env.startswith('Development/')

def generate_url_hash(searchPath):
    return hashlib.sha512(searchPath).hexdigest()

def slugify(s):
  s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')
  return re.sub('[^a-zA-Z0-9-]+', '-', s).strip('-')


def render_template(template_name, template_vals=None):
  if not template_vals:
    template_vals = {}
  template_vals.update({
      'template_name': template_name,
      'devel': os.environ['SERVER_SOFTWARE'].startswith('Devel'),
  })
  template_path = os.path.join("views", template_name)
  return template.render(template_path, template_vals)

def redirect_url(path, query_string):
    if is_development() == False:
        path = 'http://www.livebandphotos.com' + path
    if path.endswith( '/' ) == False:
        path = path + '/'
    if query_string and len(query_string) > 0:
        path = path + '?' + query_string

    return path

def set_cache_headers_expire( headers, lastModified, expires ):
    EXPIRATION_MASK = "%a, %d %b %Y %H:%M:%S %Z" 
    
    #expires = expires.replace(tzinfo=gmt) 
    #lastModified = lastModified.replace(tzinfo=gmt) 
    expiryAsDateTime = datetime.datetime.combine(expires, datetime.datetime.min.time()) -  + datetime.timedelta(seconds=1)

    secondsTillExpiry = (expiryAsDateTime - lastModified).total_seconds()

    headers['Cache-Control'] = 'public,max-age=%d' % secondsTillExpiry
    headers['Last-Modified'] = lastModified.strftime(EXPIRATION_MASK)
    headers['Expires'] = expiryAsDateTime.strftime(EXPIRATION_MASK) 
    headers['Pragma'] = 'public'

