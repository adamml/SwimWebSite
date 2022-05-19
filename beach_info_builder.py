"""A static site generator for beach information around Ireland. Pages include
data from the Marine Institute, Met Eireann and the Environmental R=Protection
Agency

:author: @adamml
"""
import astral
import astral.sun
import datetime
import json
import logging
import time
import urllib.error
import urllib.request

from string import Template

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
    :raises: json.JSONDecodeError
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

    :raises: urllib.error.HTTPError:
    :raises: urllib.error.URLError:
    :raises: TimeoutError
    :raises: json.JSONDecodeError
    """
    with urllib.request.urlopen('https://erddap.marine.ie/erddap/' +
                                'tabledap/' +
                                'IMI-TidePrediction_epa.json?' +
                                'stationID' +
                                '&distinct()') as resp:
        return json.loads(resp.read().decode('utf-8'))['table']['rows']


def fetch_all_met_eireann_weather_warnings():
    """Fetches the currently active weather and environemntal warnings for
    Ireland as published by Met Eireann.

    :returns: An object containing a list of dictionaries parsed from the
        Met Eireann weather warnings extracted from the API
    :rtype: object

    :raises: urllib.error.HTTPError:
    :raises: urllib.error.URLError:
    :raises: TimeoutError
    :raises: json.JSONDecodeError
    """
    with urllib.request.urlopen('https://www.met.ie/Open_Data/json/warning_' +
                                'IRELAND.json') as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_tide_predictions_from_marine_institute(is_dst: bool = False):
    start: str
    end: str
    if is_dst is True:
        start = "{}T22%3A00%3A00Z".format((datetime.datetime.utcnow()
                                           - datetime.timedelta(days=1))
                                          .strftime("%Y-%m-%d"))
        end = "{}T03%3A00%3A00Z".format((datetime.datetime.utcnow() +
                                         datetime.timedelta(days=1))
                                        .strftime("%Y-%m-%d"))
    else:
        start = "{}T21%3A00%3A00Z".format((datetime.datetime.utcnow()
                                           - datetime.timedelta(days=1))
                                          .strftime("%Y-%m-%d"))
        end = "{}T21%3A00%3A00Z".format((datetime.datetime.utcnow() +
                                         datetime.timedelta(days=1))
                                        .strftime("%Y-%m-%d"))
    with urllib.request.urlopen(("https://erddap.marine.ie/erddap/" +
                                 "tabledap/IMI-TidePrediction_epa.json?" +
                                 "time%2C" +
                                 "longitude%2C" +
                                 "latitude%2C" +
                                 "stationID%2C" +
                                 "sea_surface_height" +
                                 "&time%3E={}" +
                                 "&time%3C={}").format(start, end)) as resp:
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
# TODO: Make this server robust
#
is_dst: bool
if time.localtime().tm_isdst > 0:
    is_dst = True
else:
    is_dst = False

#
# Fetch all the tide predictions from the Marine Institute
#
try:
    all_tide_predictions = fetch_tide_predictions_from_marine_institute(is_dst)
except urllib.error.HTTPError:
    logging.error("Exception occurred: " +
                  "all_tide_predictions() " +
                  " HTTPError")
    raise SystemExit(0)
except urllib.error.URLError:
    logging.error("Exception occurred: " +
                  "all_tide_predictions() " +
                  " URLError")
    raise SystemExit(0)
except TimeoutError:
    logging.error("Exception occurred: " +
                  "all_tide_predictions() " +
                  " TimeoutError")
    raise SystemExit(0)
except json.JSONDecodeError:
    logging.error("Exception occurred:" +
                  "all_tide_predictions() " +
                  "JSONDecodeError")
    raise SystemExit(0)

#
# Produce the up to date report for a beach
#
for beach in all_epa_beaches:
    try:
        #
        # Set the file name prefix to for the current beach. One beach needs to
        # be the index for the site, and this is set by the the __default
        # variable at the top of the script
        #
        file_name: str
        if beach['Code'] == __default:
            file_name = 'index'
        else:
            file_name = beach['Code']

        #
        # Set the latitude and longitude for the beach. For most beaches the
        # data are carried in the EPA's information, but not for all. In these
        # cases all fall back on to the Marine Institute's forecasts is needed.
        #
        latitude: float
        longitude: float
        if beach['EtrsX']:
            longitude = beach['EtrsX']
        else:
            logging.warning("No EtrsX specified for Code \"{}\": \"{}, {}\"".
                            format(beach['Code'], beach['Name'],
                                   beach['CountyName']))
            for predn in all_tide_predictions:
                if "{}_MODELLED".format(beach['Code']) == predn[3]:
                    longitude = predn[1]
                if longitude:
                    break
        if beach['EtrsY']:
            latitude = beach['EtrsY']
        else:
            logging.warning("No EtrsY specified for Code \"{}\": \"{}, {}\"".
                            format(beach['Code'], beach['Name'],
                                   beach['CountyName']))
            for predn in all_tide_predictions:
                if "{}_MODELLED".format(beach['Code']) == predn[3]:
                    latitude = predn[2]
                if latitude:
                    break
        #
        # Set the string for a Blue Flag beach, the information regarding this
        # comes from the EPA's data
        #
        blue_flag = ""
        if beach['IsBlueFlag']:
            blue_flag = ("<span class=\"material-icons blue-flag\" " +
                         "alt=\"This a Blue Flag beach\">" +
                         "flag</span>")

        #
        # Set the string for the Met Eireann weather warnings for the beach.
        # Met Eireann use a FIPS code for the counties affected by a given
        # weather warning, which needs to be calculated from the county name
        # in the EPA's beach information. This portion of the script looks
        # for weather warnings only, and does not display, for example,
        # the environmental warnings around blight.
        #
        warning_str = ""
        for w in warn:
            if county_name_str_to_fips_code_str(
                    beach['CountyName']) in w['regions']:
                if w['capId'].find('Weather') > 0:
                    warning_str += ('<span class=\"material-icons ' +
                                    '{}-warning\">warning</span>&nbsp;{} ' +
                                    'weather warning: {} {}&nbsp;').format(
                                                            w['level'].lower(),
                                                            w['level'],
                                                            w['headline'],
                                                            w['description'])

        #
        # Calculate the dawn, dusk, sunrise, sunset times for the beach
        #
        astral_loc = astral.LocationInfo('name', 'region', 'tz/name',
                                         latitude, longitude)
        dawn_info = astral.sun.sun(astral_loc.observer,
                                   date=datetime.datetime.now())
        tdelta: datetime.timedelta
        if is_dst:
            tdelta = datetime.timedelta(hours=1)
        else:
            tdelta = datetime.timedelta(hours=0)

        #
        # Get the sea level for this beach through the day
        #
        sea_level_summary = [None, None, None, None, None, None, None, None]
        for predn in all_tide_predictions:
            if "{}_MODELLED".format(beach['Code']) == predn[3]:
                if datetime.datetime.strptime(predn[0],
                                              "%Y-%m-%dT%H:%M:%SZ") == \
                            datetime.datetime.strptime("{} 00:00:00".
                                                       format((datetime.
                                                               datetime.
                                                               utcnow() +
                                                               tdelta).
                                                              strftime("%Y-" +
                                                                       "%m-" +
                                                                       "%d")),
                                                       "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[0] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 03:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[1] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 06:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[2] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 09:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[3] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 12:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[4] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 15:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[5] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 18:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[6] = predn[4]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 21:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    sea_level_summary[7] = predn[4]

        #
        # Handle next monitoring date
        #
        next_mon_date: str
        if beach['NextMonitoringDate']:
            next_mon_date = datetime.datetime.strptime(
                beach['NextMonitoringDate'], "%Y-%m-%dT%H:%M:%S").strftime(
                            "%d %B %Y")
        else:
            next_mon_date = "Unknown"

        #
        # Write the data to file
        #
        with open("./docs/{}.md".format(file_name), 'w',
                  encoding='utf-8') as f:
            f.write(Template("""---
title: Beach information for $beach_name, $county_name
---
## $beach_name, $county_name $blue_flag

latitude: $latitude, longitude: $longitude
{: .location-info}

$weather_warnings
{: .met-eireann-warnings}

___Last updated___: $now_strftime; ___Water Quality___: $water_quality;
___Last sample on___: $last_sample; ___Next Monitoring Date___: $next_mon_date
{: .last-updated-and-water-quality}

|   |   |   |   |   |
|---|---|---|---|---|
|   |   |   | Dawn  | $dawn_strftime |
|   |   |   | Sunrise  | $sunrise_strftime |
|   |   |   | Sunset  | $sunset_strftime |
|   |   |   | Dusk  | $dusk_strftime |
{: .tide-and-sun-table}

<div></div>

| | 00:00 | 03:00 | 06:00 | 09:00 | 12:00 | 15:00 | 18:00 | 21:00 |
|---|---|---|---|---|---|---|---|---|
| Sea level | $sl00 | $sl03 | $sl06 | $sl09| $sl12 | $sl15 | $sl18 | $sl21 |
{: .detail-table}

__Disclaimer__: This page contains data from the Marine Institute,
Met Eireann and the Environment Protection Agency. The page is provided for
information purposes only and is not to be used for navigation. No liability
is assumed if information provided leads to personal injury etc...
{: .disclaimer}""").
                    safe_substitute(beach_name=beach['Name'],
                                    county_name=beach['CountyName'],
                                    blue_flag=blue_flag,
                                    latitude=latitude,
                                    longitude=longitude,
                                    weather_warnings=warning_str,
                                    now_strftime=datetime.datetime.now().
                                    strftime("%d %B %Y %H:%M"),
                                    dawn_strftime=(dawn_info['dawn'] + tdelta).
                                    strftime("%H:%M"),
                                    sunrise_strftime=(dawn_info['sunrise']
                                                      + tdelta).strftime(
                                                          "%H:%M"),
                                    sunset_strftime=(dawn_info['sunset']
                                                     + tdelta).strftime(
                                                         "%H:%M"),
                                    dusk_strftime=(dawn_info['dusk'] +
                                                   tdelta).strftime("%H:%M"),
                                    sl00=sea_level_summary[0],
                                    sl03=sea_level_summary[1],
                                    sl06=sea_level_summary[2],
                                    sl09=sea_level_summary[3],
                                    sl12=sea_level_summary[4],
                                    sl15=sea_level_summary[5],
                                    sl18=sea_level_summary[6],
                                    sl21z=sea_level_summary[7],
                                    water_quality=beach['WaterQualityName'],
                                    last_sample=datetime.datetime.strptime(
                                        beach['LastSampleOn'],
                                        "%Y-%m-%dT%H:%M:%S").
                                    strftime("%d %B %Y"),
                                    next_mon_date=next_mon_date))
    except ValueError as e:
        logging.error('Value Error on FIPS Code for {}, {}, {}'
                      .format(beach['Name'], beach['CountyName'], str(e)))
    except TypeError as e:
        logging.error('TypeError on NextMonitoringDate Code for {}, {}, {}'
                      .format(beach['Name'], beach['CountyName'], str(e)))
