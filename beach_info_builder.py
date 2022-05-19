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
import math
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
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
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
    """Fetches the full set of tide predictions for a day from the Marine
    Institute's Erddap server. The returned object contains time, longitude,
    latitude, station id and predicted sea level in metres for each prediction

    :param: is_dst: Should Daylight Saving Time be applied, True if yes
    :type: is_dst: bool, defaults to False

    :return: An object representing the content of the JSON collected from
        the API
    :rtype: object

    :raises: urllib.error.HTTPError:
    :raises: urllib.error.URLError:
    :raises: TimeoutError
    :raises: json.JSONDecodeError
    """
    start: str
    end: str
    if is_dst is True:
        start = "{}T20%3A00%3A00Z".format((datetime.datetime.utcnow()
                                           - datetime.timedelta(days=1))
                                          .strftime("%Y-%m-%d"))
        end = "{}T02%3A00%3A00Z".format((datetime.datetime.utcnow() +
                                         datetime.timedelta(days=1))
                                        .strftime("%Y-%m-%d"))
    else:
        start = "{}T21%3A00%3A00Z".format((datetime.datetime.utcnow()
                                           - datetime.timedelta(days=1))
                                          .strftime("%Y-%m-%d"))
        end = "{}T03%3A00%3A00Z".format((datetime.datetime.utcnow() +
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


def fetch_all_neatl_model_from_marine_institute(is_dst: bool = False,
                                                min_lat: float = None,
                                                min_lon: float = None,
                                                max_lat: float = None,
                                                max_lon: float = None):
    start: str
    end: str
    if is_dst is True:
        start = "{}T23%3A00%3A00Z".format((datetime.datetime.utcnow() -
                                         datetime.timedelta(days=1))
                                          .strftime("%Y-%m-%d"))
        end = "{}T23%3A00%3A00Z".format(datetime.datetime.utcnow()
                                        .strftime("%Y-%m-%d"))
    else:
        start = "{}T00%3A00%3A00Z".format(datetime.datetime.utcnow()
                                          .strftime("%Y-%m-%d"))
        end = "{}T00%3A00%3A00Z".format((datetime.datetime.utcnow() +
                                         datetime.timedelta(days=1))
                                        .strftime("%Y-%m-%d"))
    with urllib.request.urlopen(("https://erddap.digitalocean.ie/erddap/" +
                                 "griddap/" +
                                 "IMI_NEATL.json?" +
                                 "sea_surface_temperature%5B" +
                                 "({start}):1:({end})%5D%5B" +
                                 "({min_lat}):1:({max_lat})%5D%5B" +
                                 "({min_lon}):1:({max_lon})%5D," +
                                 "sea_surface_x_velocity%5B" +
                                 "({start}):1:({end})%5D%5B" +
                                 "({min_lat}):1:({max_lat})%5D%5B" +
                                 "({min_lon}):1:({max_lon})%5D," +
                                 "sea_surface_y_velocity%5B" +
                                 "({start}):1:({end})%5D%5B" +
                                 "({min_lat}):1:({max_lat})%5D%5B" +
                                 "({min_lon}):1:({max_lon})%5D").format(
                                    start=start,
                                    end=end,
                                    min_lon=min_lon,
                                    min_lat=min_lat,
                                    max_lon=max_lon,
                                    max_lat=max_lat)) as resp:
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
# Get the NEATL predictions from the Marine Institute
#
neatl_forecast = \
    fetch_all_neatl_model_from_marine_institute(
        is_dst=is_dst,
        min_lat=min([x[2] for x in all_tide_predictions]) - 0.0125,
        max_lat=max([x[2] for x in all_tide_predictions]) + 0.0125,
        min_lon=min([x[1] for x in all_tide_predictions]) - 0.0125,
        max_lon=max([x[1] for x in all_tide_predictions]) + 0.0125)

#
# Identify none null grid positions from the NEATL forecast
#
neatl_valid_grid = [[x[1], x[2]] for x in neatl_forecast if x[3] is not None]

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
        logging.info("Beginning processing {}, {}".format(beach["Name"],
                                                          beach["CountyName"]))
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
        # Find the closest NEATL grid point
        #
        neatl_distances = [math.pow(math.pow(float(latitude) - float(x[0]), 2)
                           + math.pow(float(longitude) - float(x[1]), 2), 0.5)
                           for x in neatl_valid_grid]
        neatl_closest_idx = neatl_distances.index(min(neatl_distances))
        neatl_lat = neatl_valid_grid[neatl_closest_idx][0]
        neatl_lon = neatl_valid_grid[neatl_closest_idx][1]

        #
        # Extract data from the NEATL predictions
        #
        water_temp = [None, None, None, None, None, None, None, None]
        water_velocity_x = [None, None, None, None, None, None, None, None]
        water_velocity_y = [None, None, None, None, None, None, None, None]
        current_speed = [None, None, None, None, None, None, None, None]
        current_direction = [None, None, None, None, None, None, None, None]

        for predn in neatl_forecast:
            if predn[1] == neatl_lat and predn[2] == neatl_lon:
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
                    water_temp[0] = predn[3]
                    water_velocity_x[0] = predn[4]
                    water_velocity_y[0] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 03:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[1] = predn[3]
                    water_velocity_x[1] = predn[4]
                    water_velocity_y[1] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 06:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[2] = predn[3]
                    water_velocity_x[2] = predn[4]
                    water_velocity_y[2] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 09:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[3] = predn[3]
                    water_velocity_x[3] = predn[4]
                    water_velocity_y[3] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 12:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[4] = predn[3]
                    water_velocity_x[4] = predn[4]
                    water_velocity_y[4] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 15:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[5] = predn[3]
                    water_velocity_x[5] = predn[4]
                    water_velocity_y[5] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 18:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[6] = predn[3]
                    water_velocity_x[6] = predn[4]
                    water_velocity_y[6] = predn[5]
                elif datetime.datetime.strptime(predn[0],
                                                "%Y-%m-%dT%H:%M:%SZ") == \
                        datetime.datetime.strptime("{} 21:00:00".
                                                   format((datetime.
                                                           datetime.utcnow() +
                                                           tdelta).
                                                          strftime("%Y-%m-%d")
                                                          ),
                                                   "%Y-%m-%d %H:%M:%S"):
                    water_temp[7] = predn[3]
                    water_velocity_x[7] = predn[4]
                    water_velocity_y[7] = predn[5]
        
        current_speed = [math.pow((math.pow(x[0], 2) + math.pow(x[1], 2)), 0.5) for x in zip(water_velocity_x, water_velocity_y)]

        for i, vec in enumerate(zip(water_velocity_x, water_velocity_y)):
            if vec[0] > 0 and vec[1] > 0:
                current_direction[i] = math.degrees(math.atan(vec[0]/vec[1]))
        logging.info(current_direction)
        #
        # Write the data to file
        #
        with open("./docs/{}.md".format(file_name), 'w',
                  encoding='utf-8') as f:
            f.write(Template("""---
title: Beach information for $beach_name, $county_name
---
# $beach_name, $county_name $blue_flag
{: .h1-display}

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
| Water temperature | $wt00 | $wt03 | $wt06 | $wt09 | $wt12 | $wt15 | $wt18 | $wt21 |
| Current | $cu00 | $cu03 | $cu06 | $cu09 | $cu12| $cu15 | $cu18 | $cu21 |
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
                                    sl21=sea_level_summary[7],
                                    wt00="{:.1f}".format(water_temp[0]),
                                    wt03="{:.1f}".format(water_temp[1]),
                                    wt06="{:.1f}".format(water_temp[2]),
                                    wt09="{:.1f}".format(water_temp[3]),
                                    wt12="{:.1f}".format(water_temp[4]),
                                    wt15="{:.1f}".format(water_temp[5]),
                                    wt18="{:.1f}".format(water_temp[6]),
                                    wt21="{:.1f}".format(water_temp[7]),
                                    cu00="{:.1f}".format(current_speed[0]),
                                    cu03="{:.1f}".format(current_speed[1]),
                                    cu06="{:.1f}".format(current_speed[2]),
                                    cu09="{:.1f}".format(current_speed[3]),
                                    cu12="{:.1f}".format(current_speed[4]),
                                    cu15="{:.1f}".format(current_speed[5]),
                                    cu18="{:.1f}".format(current_speed[6]),
                                    cu21="{:.1f}".format(current_speed[7]),
                                    water_quality=beach['WaterQualityName'],
                                    last_sample=datetime.datetime.strptime(
                                        beach['LastSampleOn'],
                                        "%Y-%m-%dT%H:%M:%S").
                                    strftime("%d %B %Y"),
                                    next_mon_date=next_mon_date))
        logging.info("Finished processing {}, {}".format(beach["Name"],
                                                         beach["CountyName"]))
    except ValueError as e:
        logging.error('Value Error on FIPS Code for {}, {}, {}'
                      .format(beach['Name'], beach['CountyName'], str(e)))
