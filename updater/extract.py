import datetime
import os
import pathlib
import re
import xml.etree.ElementTree as et

import htmlmin
from chameleon import PageTemplateLoader

root = pathlib.Path(__file__).parent.resolve()
templates_path = os.path.join(root, "templates")
destination_base = pathlib.Path(root).parent.resolve() / "dst"
today = datetime.date.today()
limit = today + datetime.timedelta(days=10)
now = datetime.datetime.now()
templates = PageTemplateLoader(templates_path)


def iso_parse_date(s):
    try:
        year = s[0:4]
        month = s[5:7]
        day = s[8:10]
        numeric_year = int(year, 10)
        if numeric_year < 2000:
            return None

        return datetime.date(numeric_year, int(month, 10), int(day, 10))

    except:
        return None


def make_url(original_path):
    url_base = original_path.lower()

    url_root = url_base.strip();

    replaced_encoded_space = url_root.replace("%20", "-")
    replaced_wrong_slash = replaced_encoded_space
    replaced_duplicate_hyphens = re.sub(r"[^a-z0-9\-/]", "-", replaced_wrong_slash)
    replaced_bad_chars = re.sub(r"(\-{2,})", "-", replaced_duplicate_hyphens)
    replaced_ending_hyphens = replaced_bad_chars.rstrip('-')

    if not replaced_ending_hyphens.endswith('/'):
        replaced_ending_hyphens = replaced_ending_hyphens + '/'

    return replaced_ending_hyphens


def make_band_url(name):
    return make_url('/band/' + name)


def make_venue_url(name):
    return make_url('/venue/' + name)


def create_folder(folder):
    if not folder.exists():
        try:
            folder.mkdir()
        except FileExistsError:
            pass


def write_file(file_name, contents):
    file_name.open("w").write(contents)


def output_page(url, page):
    fragments = url[1:-1].split("/")
    output_folder = destination_base
    for fragment in fragments:
        create_folder(output_folder)
        output_folder = output_folder / fragment
    create_folder(output_folder)
    band_index_html = output_folder / "index.html"

    page = htmlmin.minify(page, remove_empty_space=True)

    write_file(band_index_html, page)


def sort_gigs_by_date(gigs):
    return sorted(gigs, key=lambda x: x['date'], reverse=False)


def build_band_page(band_url, band_name, gigs):
    band_template = templates['band.pt']

    band_gigs = []
    for gig in gigs:
        gig_band_url = gig['band_url']
        if gig_band_url == band_url:
            band_gigs.append(gig)

    print(band_url)

    page = band_template(path=band_url, track=False, band=band_name, gigs=band_gigs)

    output_page(band_url, page)


def build_venue_page(venue_url, venue_name, gigs):
    venue_template = templates['venue.pt']

    venue_gigs = []
    for gig in gigs:
        gig_venue_url = gig['venue_url']
        if gig_venue_url == venue_url:
            venue_gigs.append(gig)

    print(venue_url)

    page = venue_template(path=venue_url, track=False, venue=venue_name, gigs=venue_gigs)

    output_page(venue_url, page)


def build_index_page(gigs):
    main_template = templates['main.pt']

    main_gigs = []
    for gig in gigs:
        date = gig['date']
        if date <= limit:
            main_gigs.append(gig)

    page = main_template(gigs=main_gigs)

    output_page('/', page)

def build_all():
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

        gig_id = gig_xml.find('id').text
        band_name = gig_xml.find('bandname').text
        venue_name = gig_xml.find('venuename').text
        gig_date_raw = gig_xml.find('gigdate').text

        parsed_id = int(gig_id, 10)
        parsed_date = iso_parse_date(gig_date_raw)
        if parsed_date is not None and parsed_date >= today:
            relevant_gigs = relevant_gigs + 1

            bands[make_band_url(band_name)] = band_name
            venues[make_venue_url(venue_name)] = venue_name

            gigs.append({
                'id': parsed_id,
                'band': band_name,
                'venue': venue_name,
                'date': parsed_date,
                'band_url': make_band_url(band_name),
                'venue_url': make_venue_url(venue_name)
            })

    gigs = sort_gigs_by_date(gigs)

    print("Total Gigs: " + str(found_gigs))
    print("Relevant Gigs: " + str(relevant_gigs))

    print(templates_path)
    print(destination_base)

    build_index_page(gigs)

    for band in bands:
        build_band_page(band, bands[band], gigs)

    for venue in venues:
        build_venue_page(venue, venues[venue], gigs)


if __name__ == "__main__":
    build_all()
