import requests
from bs4 import BeautifulSoup
import sys
import re
import geocoder


BASE_URL = 'http://info.kingcounty.gov'

HEALTH_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'

HEALTH_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}


def get_inspection_page(**kwargs):
    payload = HEALTH_PARAMS.copy()
    for key, val in kwargs.items():
        if key in HEALTH_PARAMS:
            payload[key] = val
    r = requests.get(BASE_URL + HEALTH_PATH, params=payload)
    r.raise_for_status()
    return r.content, r.encoding


def load_inspection_page():
    content = open('inspection_page.html', 'r')
    resp_content = content.read()
    content.closed
    encoding = open('inspection_page_encoding.html', 'r')
    resp_encoding = encoding.read()
    encoding.closed
    return resp_content, resp_encoding


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def extract_data_listings(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(elem):
    is_tr = elem.name == 'tr'
    td_children = elem.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two


def clean_data(td):
    data = td.string
    try:
        return data.strip(" \n:-")
    except AttributeError:
        return u""


def extract_restaurant_metadata(elem):
    metadata_rows = elem.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for row in metadata_rows:
        key_cell, val_cell = row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata


def is_inspection_row(elem):
    is_tr = elem.name == 'tr'
    if not is_tr:
        return False
    td_children = elem.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_tr and has_four and contains_word and does_not_start


def extract_score_data(elem):
    inspection_rows = elem.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += intval
            high_score = intval if intval > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'High Score': high_score,
        u'Total Inspections': samples
    }
    return data


def generate_results(test=False):
    kwargs = {
        'Inspection_Start': '2/18/2013',
        'Inspection_End': '2/18/2015',
        'Zip_Code': '98102'
    }
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = load_inspection_page()
    else:
        html, encoding = get_inspection_page(**kwargs)
    doc = parse_source(html, encoding)
    listings = extract_data_listings(doc)
    count = 0
    for listing in listings:
        metadata = extract_restaurant_metadata(listing)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        yield metadata
        count += 1
        if count == 10:
            break

def get_geojson(result):
    address = " ".join(result.get('Address', ''))
    if not address:
        return None
    geocoded = geocoder.google(address)
    return geocoded.geojson


if __name__ == '__main__':
    import pprint
    test = len(sys.argv) > 1 and sys.argv[1] == 'test'
    for result in generate_results(test):
        geo_result = get_geojson(result)
        pprint.pprint(geo_result)
        # code to re-create files as needed
        #html_part = open('inspection_page.html', 'w')
        #html_part.write(html)
        #html_part.closed
        #encoding_part = open('inspection_page_encoding.html', 'w')
        #encoding_part.write(encoding)
        #encoding_part.closed

# https://github.com/efrainc/basic_scraper/blob/master/scraper.py
