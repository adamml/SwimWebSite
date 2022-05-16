from fileinput import filename
import json
import logging
import urllib.error
import urllib.request

#
# Set the default beach id to Salthill, Galway
#
__default = 'IEWEBWC170_0000_0200'

#
# set up the logger
#
logger = logging.getLogger()
handler = logging.FileHandler("error.log")
handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s]: %(message)s'))
logger.addHandler(handler)


def fetch_all_beaches_from_epa_api():
    """Gets the current data from Ireland's Environment Protection Agency's
    API for the beaches.ie system.

    :returns: A JSON object representing the content returned from the API
    :rtype: json.JSON

    :raises: urllib.error.HTTPError:
    :raises: urllib.error.URLError:
    :raises: TimeoutError
    """
    with urllib.request.urlopen('https://api.beaches.ie/odata/beaches?' +
                                '$expand=Incidents') as resp:
        return json.loads(resp.read().decode('utf-8'))['value']


def fetch_all_beaches_from_marine_institute_erddap():
    with urllib.request.urlopen('https://erddap.marine.ie/erddap/' +
                                'tabledap/' +
                                'IMI-TidePrediction_epa.json?' +
                                'stationID' +
                                '&distinct()') as resp:
        return json.loads(resp.read().decode('utf-8'))['table']['rows']


#
# Get the full list of beaches from the EPA's Beaches.ie website
#
try:
    all_epa_beaches = fetch_all_beaches_from_epa_api()
except urllib.error.HTTPError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api()" +
                  " HTTPError")
except urllib.error.URLError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api()" +
                  "URLError")
except TimeoutError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api()"+
                  "TimeoutError")

#
# Get the list of beaches supported by predictions from the Marine Institute
#
try:
    all_marine_inst_beaches = fetch_all_beaches_from_marine_institute_erddap()
except urllib.error.HTTPError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap()" +
                  " HTTPError")
except urllib.error.URLError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap()" +
                  " URLError")
except TimeoutError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap()" +
                  " TimeoutError")

marine_inst_beaches = [x[0].split('_MODELLED')[0]
                       for x in all_marine_inst_beaches]

#
# Remove EPA beaches from the list if they aren't in the MI dataset
#
for beach in all_epa_beaches:
    if beach['Code'] not in marine_inst_beaches:
        all_epa_beaches.remove(beach)

#
# Produce the current table for a beach
#
for beach in all_epa_beaches:
    file_name: str
    if beach['Code'] == __default:
        file_name = 'index'
    else:
        file_name = beach['Code']

    latitude: float
    longitide: float
    if beach['EtrsX']:
        longitide = beach['EtrsX']
    if beach['EtrsY']:
        latitude = beach['EtrsY']
    blue_flag = ""
    if beach['IsBlueFlag']:
        blue_flag = "<span class=\"material-icons\" style=\"color: blue;\">flag</span>"

    with open("./docs/{}.md".format(file_name), 'w', encoding='utf-8') as f:
        f.write("""---
title: Beach information for {}
---
# {}, {} {}

<div align="center"><i>latitude: {} longitude: {}</i></div>""".
                format("{}, {}".format(beach['Name'], beach['CountyName']),
                       beach['Name'],
                       beach['CountyName'],
                       blue_flag,
                       latitude,
                       longitide))
