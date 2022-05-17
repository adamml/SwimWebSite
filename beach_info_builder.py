"""A static site generator for beach information around Ireland. Pages include
data from the Marine Institute, Met Eireann and the Environmental R=Protection
Agency

:author: @adamml
"""
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


def county_name_str_to_fips_code_str(county_name: str) -> str:
    """ Returns the Federal Information Processing System (FIPS) county code
    for a given county name for the country of Ireland.

    :param county_name: A string representing the name of the county to return
        the FIPS code fior, e.g. "Cork" or "Galway"
    :type county_name: str

    :return: A four character string that is the FIPS code for county_name
    :rtype: str

    :raises: ValueError: If county_name is not recognised
    """
    if county_name.lower() == "carlow":
        return "EI01"
    elif county_name.lower() == "cavan":
        return "EI02"
    elif county_name.lower() == "clare":
        return "EI03"
    elif county_name.lower() == "cork":
        return "EI04"
    elif county_name.lower() == "donegal":
        return "EI06"
    elif county_name.lower() == "dublin":
        return "EI07"
    elif county_name.lower() == "galway":
        return "EI10"
    elif county_name.lower() == "kerry":
        return "EI11"
    elif county_name.lower() == "kildare":
        return "EI12"
    elif county_name.lower() == "kilkenny":
        return "EI13"
    elif county_name.lower() == "laois":
        return "EI15"
    elif county_name.lower() == "leitrim":
        return "EI14"
    elif county_name.lower() == "limerick":
        return "EI16"
    elif county_name.lower() == "longford":
        return "EI18"
    elif county_name.lower() == "louth":
        return "EI19"
    elif county_name.lower() == "mayo":
        return "EI20"
    elif county_name.lower() == "meath":
        return "EI21"
    elif county_name.lower() == "monaghan":
        return "EI22"
    elif county_name.lower() == "offaly":
        return "EI23"
    elif county_name.lower() == "roscommon":
        return "EI24"
    elif county_name.lower() == "sligo":
        return "EI25"
    elif county_name.lower() == "tipperary":
        return "EI26"
    elif county_name.lower() == "waterford":
        return "EI27"
    elif county_name.lower() == "westmeath":
        return "EI29"
    elif county_name.lower() == "wexford":
        return "EI30"
    elif county_name.lower() == "wicklow":
        return "EI31"
    else:
        raise ValueError("Unknown county - {}".format(county_name.lower()))


def fetch_all_beaches_from_epa_api():
    """Gets the current data from Ireland's Environment Protection Agency's
    API for the beaches.ie system.

    :return: An object representing the content of the JSON collected from
        the API
    :rtype: object

    :raises: urllib.error.HTTPError:
    :raises: urllib.error.URLError:
    :raises: TimeoutError
    """
    with urllib.request.urlopen('https://api.beaches.ie/odata/beaches?' +
                                '$expand=Incidents') as resp:
        return json.loads(resp.read().decode('utf-8'))['value']


def fetch_all_beaches_from_marine_institute_erddap():
    """Fetches a list of Eden codes from the Marine Institute's Erddap server
    using the EPA beach prediction dataset as a source.

    :return: An object representing the content of the JSON collected from
        the API
    :rtype: object
    """
    with urllib.request.urlopen('https://erddap.marine.ie/erddap/' +
                                'tabledap/' +
                                'IMI-TidePrediction_epa.json?' +
                                'stationID' +
                                '&distinct()') as resp:
        return json.loads(resp.read().decode('utf-8'))['table']['rows']


def fetch_all_met_eireann_weather_warnings():
    with urllib.request.urlopen('https://www.met.ie/Open_Data/json/warning_' +
                                'IRELAND.json') as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_tide_predictions_from_marine_institute():
    with urllib.request.urlopen("https://erddap.marine.ie/erddap/tabledap/IMI-TidePrediction_epa.json?time%2Clongitude%2Clatitude%2CstationID%2Csea_surface_height&time%3E=2022-05-16T21%3A00%3A00Z&time%3C=2022-05-18T03%3A00%3A00Z") as resp:
        return json.loads(resp.read().decode('utf-8'))['table']['rows']


#
# Get the full list of beaches from the EPA's Beaches.ie website
#
try:
    all_epa_beaches = fetch_all_beaches_from_epa_api()
except urllib.error.HTTPError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api() " +
                  " HTTPError")
    raise SystemExit(0)
except urllib.error.URLError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api() " +
                  "URLError")
    raise SystemExit(0)
except TimeoutError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api() " +
                  "TimeoutError")
    raise SystemExit(0)
except json.JSONDecodeError:
    logging.error("Exception occurred: fetch_all_beaches_from_epa_api() " +
                  "JSONDecodeError")
    raise SystemExit(0)

#
# Get the list of beaches supported by predictions from the Marine Institute
#
try:
    all_marine_inst_beaches = fetch_all_beaches_from_marine_institute_erddap()
except urllib.error.HTTPError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap() " +
                  " HTTPError")
    raise SystemExit(0)
except urllib.error.URLError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap() " +
                  " URLError")
    raise SystemExit(0)
except TimeoutError:
    logging.error("Exception occurred: " +
                  "fetch_all_beaches_from_marine_institute_erddap() " +
                  " TimeoutError")
    raise SystemExit(0)
except json.JSONDecodeError:
    logging.error("Exception occurred:" +
                  "fetch_all_beaches_from_marine_institute_erddap() " +
                  "JSONDecodeError")
    raise SystemExit(0)

marine_inst_beaches = [x[0].split('_MODELLED')[0]
                       for x in all_marine_inst_beaches]

#
# Remove EPA beaches from the list if they aren't in the MI dataset
#
for beach in all_epa_beaches:
    if beach['Code'] not in marine_inst_beaches:
        all_epa_beaches.remove(beach)

#
# Get the cuurently active weather warnings for Ireland
#
try:
    warn = fetch_all_met_eireann_weather_warnings()
except urllib.error.HTTPError:
    logging.error("Exception occurred: " +
                  "fetch_all_met_eireann_weather_warnings() " +
                  " HTTPError")
    raise SystemExit(0)
except urllib.error.URLError:
    logging.error("Exception occurred: " +
                  "fetch_all_met_eireann_weather_warnings() " +
                  " URLError")
    raise SystemExit(0)
except TimeoutError:
    logging.error("Exception occurred: " +
                  "fetch_all_met_eireann_weather_warnings() " +
                  " TimeoutError")
    raise SystemExit(0)
except json.JSONDecodeError:
    logging.error("Exception occurred:" +
                  "fetch_all_met_eireann_weather_warnings() " +
                  "JSONDecodeError")
    raise SystemExit(0)

#
# Fetch all the tide predictions from the Marine Institute
#
all_tide_predictions = fetch_tide_predictions_from_marine_institute()

#
# Produce the up to date report for a beach
#
for beach in all_epa_beaches:
    try:
        file_name: str
        if beach['Code'] == __default:
            file_name = 'index'
        else:
            file_name = beach['Code']

        latitude: float
        longitide: float
        if beach['EtrsX']:
            longitide = beach['EtrsX']
        else:
            logging.warning("No EtrsX specified for Code \"{}\": \"{}, {}\"".
                            format(beach['Code'], beach['Name'],
                                   beach['CountyName']))
        if beach['EtrsY']:
            latitude = beach['EtrsY']
        else:
            logging.warning("No EtrsY specified for Code \"{}\": \"{}, {}\"".
                            format(beach['Code'], beach['Name'],
                                   beach['CountyName']))

        blue_flag = ""
        if beach['IsBlueFlag']:
            blue_flag = ("<span class=\"material-icons blue-flag\">" +
                         "flag</span>")

        warning_str = ""
        for w in warn:
            if county_name_str_to_fips_code_str(beach['CountyName']) in w['regions']:
                if w['capId'].find('Weather') > 0:
                    warning_str += ('<span class=\"material-icons ' +
                                   '{}-warning\">warning</span>&nbsp;{} ' +
                                   'weather warning: {} {}&nbsp;').format(
                                                            w['level'].lower(),
                                                            w['level'],
                                                            w['headline'],
                                                            w['description'])

        with open("./docs/{}.md".format(file_name), 'w', 
                  encoding='utf-8') as f:
            f.write("""---
title: Beach information for {}
---
# {}, {} {}

<div class="location-info">latitude: {} longitude: {}</div>
<div class="met-eireann-warnings">{}</div>
<div></div>

## Disclaimer

This page contains data from the Marine Institute, 
Met Eireann and the Environment Protection Agency. The page is provided for
information purposes only and is not to be used for navigation. No liability 
is assumed if information provided leads to personal injury etc...""".
                    format("{}, {}".format(beach['Name'], 
                           beach['CountyName']),
                           beach['Name'],
                           beach['CountyName'],
                           blue_flag,
                           latitude,
                           longitide,
                           warning_str))
    except ValueError:
        logging.error('Value Error on FIPS Code for {}, {}'
                      .format(beach['Name'], beach['CountyName']))
