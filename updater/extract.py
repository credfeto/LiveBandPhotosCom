from chameleon import PageTemplateLoader
import datetime
import os
import pathlib
import re

import xml.etree.ElementTree as et

root = pathlib.Path(__file__).parent.resolve()
today = datetime.date.today()
now = datetime.datetime.now()

templates = PageTemplateLoader(os.path.join(root, "templates"))

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

def build_band_page(band_url, band_name, gigs):

  band_template = templates['band.pt']


  band_gigs = []
  for gig in gigs:
    gbu = make_band_url(gig['band'])
    # print(gbu)
    if gbu == band_url:
      band_gigs.append(gig)
      print(gig['venue'])

  page = band_template(path=band_url, track=False, band=band_name, gigs=band_gigs)
  print(page)


if __name__ == "__main__":

  gigs_file = root / "gigs.xml"

  gigs_root = et.ElementTree(file=gigs_file)

  bands = {}
  venues = {}
  gigs = []

  found_gigs = 0
  relevant_gigs = 0
  bands_xml = gigs_root.findall(".//table[@name='tempgig']/records/record")

  for gig_xml in bands_xml:
    found_gigs = found_gigs + 1

    id = gig_xml.find('id').text
    bandname = gig_xml.find('bandname').text
    venuename = gig_xml.find('venuename').text
    gigDateRaw = gig_xml.find('gigdate').text
                
    parsedId = int(id, 10)
    parsedDate = isoparse(gigDateRaw)
    if parsedDate != None and parsedDate >= today:
      
      relevant_gigs = relevant_gigs + 1

      bands[make_band_url(bandname)] = bandname
      venues[make_venue_url(venuename)] = venuename

      gigs.append({
              'id': parsedId,
              'band': bandname,
              'venue': venuename,
              'date': parsedDate
               })


  for band in bands:
    print(band)

  for venue in venues:
    print(venue)


  print("Total Gigs: " +str(found_gigs))
  print("Relevant Gigs: " +str(relevant_gigs))

  build_band_page('/band/reboot/', 'Reboot', gigs)
