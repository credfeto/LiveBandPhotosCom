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
        numeric_year = int(year, 10)
        if numeric_year < 2000:
            return None

        return datetime.date(numeric_year, int(month, 10), int(day, 10))
    except:
        return None

def make_url(originalPath):

    base = originalPath.lower()
    
    root =  base.strip();
    
    replaced_encoded_space = root.replace("%20", "-" )
    replaced_wrong_slash = replaced_encoded_space
    replaced_duplicate_hyphens = re.sub(r"[^a-z0-9\-/]", "-", replaced_wrong_slash)
    replaced_bad_chars = re.sub(r"(\-{2,})", "-", replaced_duplicate_hyphens )
    replaced_ending_hyphens = replaced_bad_chars.rstrip('-')

    if not replaced_ending_hyphens.endswith('/'):
        replaced_ending_hyphens = replaced_ending_hyphens + '/'

    return replaced_ending_hyphens

def make_band_url(name):
   return make_url('/band/' + name)

def make_venue_url(name):
    return make_url('/venue/' + name)

def make_venue_fragment(name):
    base = name.lower()

    root = base.strip();

    replaced_encoded_space = root.replace("%20", "-")
    replaced_wrong_slash = replaced_encoded_space
    replaced_duplicate_hyphens = re.sub(r"[^a-z0-9\-/]", "-", replaced_wrong_slash)
    replaced_bad_chars = re.sub(r"(\-{2,})", "-", replaced_duplicate_hyphens)
    replaced_ending_hyphens = replaced_bad_chars.rstrip('-')

    return replaced_ending_hyphens

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
    if not is_development():
        path = 'https://www.livebandphotos.com' + path
    if not path.endswith('/'):
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
    headers['Access-Control-Allow-Origin'] = "'self'"
    headers['Access-Control-Allow-Methods'] = "GET, HEAD, OPTIONS"
    headers[
        'Content-Security-Policy'] = "default-src 'none'; img-src 'self'; style-src 'self'; report-uri https://markridgwell.report-uri.com/r/d/csp/enforce"
    headers['Expect-CT'] = "max-age=0, report=uri=\"https://markridgwell.report-uri.com/r/d/ct/reportOnly\""
    headers['X-Frame-Options'] = "DENY"
    headers['X-XSS-Protection'] = "1; mode=block; report=https://markridgwell.report-uri.com/r/d/xss/enforce"
    headers['X-Content-Type-Options'] = "nosniff"
    headers['Vary'] = 'DNT'
    headers['strict-transport-security'] = 'max-age=31536000; includeSubdomains; preload'
    headers['Referrer-Policy'] = 'no-referrer'
