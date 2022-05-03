import concurrent.futures
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash import Input
from dash import Output
import datetime
import json
import math
import pandas as pd
import plotly.express as px
import pytz
import urllib.error
import urllib.request
import xml.etree.ElementTree

#
# Function to handle requests to Mat Eireann forecast API
#


def met_eireann_forecast_fetcher(url_and_eden_code: list):
    try:
        with urllib.request.urlopen(url_and_eden_code[0]) as this_forecast:
            this_forecast_as_str = this_forecast.read().decode()
    except urllib.error.URLError:
        print("Error opening: {}".format(url_and_eden_code[0]))
    et = xml.etree.ElementTree.fromstring(this_forecast_as_str)
    _return_list = []
    for time in et.iter("time"):
        if time.attrib["from"] == time.attrib["to"]:
            _return_list.append([time.attrib["from"],
                                 url_and_eden_code[1],
                                 time[0][0].attrib["value"],
                                 time[0][1].attrib["deg"],
                                 time[0][2].attrib["mps"],
                                 time[0][3].attrib["mps"]])
    return _return_list


def marine_institute_forecast_fetcher(url_and_eden_code: list):
    try:
        with urllib.request.urlopen(url_and_eden_code[0]) as this_neatl_forecast:
            this_neatl_forecast_parsed = json.loads(
                this_neatl_forecast.read().decode())
    except urllib.error.URLError:
        print("Error opening: {}".format(url_and_eden_code[0]))

    try:
        with urllib.request.urlopen(url_and_eden_code[1]) as this_swan_forecast:
            this_swan_forecast_parsed = json.loads(
                this_swan_forecast.read().decode())
    except urllib.error.URLError:
        print("Error opening: {}".format(url_and_eden_code[1]))

    this_neatl_forecast_parsed = this_neatl_forecast_parsed["table"]["rows"]
    this_swan_forecast_parsed = this_swan_forecast_parsed["table"]["rows"]
    neatl_curr_speed = [math.pow((math.pow(x[6], 2) + math.pow(x[5], 2)), 0.5)
                        if x[5] is not None and x[6] is not None else None
                        for x in this_neatl_forecast_parsed]
    #
    # TODO:
    #   Calculate current direction
    #
    this_neatl_forecast_parsed = [[x[0],
                                   url_and_eden_code[2],
                                   x[3],
                                   x[4],
                                   x[5],
                                   x[6],
                                   neatl_curr_speed[i],
                                   None,
                                   None,
                                   None,
                                   None] for i, x in enumerate(this_neatl_forecast_parsed)]
    neatl_forecast_times = [x[0] for x in this_neatl_forecast_parsed]
    for row in this_swan_forecast_parsed:
        this_neatl_forecast_parsed[neatl_forecast_times.index(row[0])][7] = row[3]
        this_neatl_forecast_parsed[neatl_forecast_times.index(row[0])][8] = row[4]
        this_neatl_forecast_parsed[neatl_forecast_times.index(row[0])][9] = row[5]
        this_neatl_forecast_parsed[neatl_forecast_times.index(row[0])][10] = row[6]
    return this_neatl_forecast_parsed


#
# Get all the beaches available from the EPA Beaches API
#

epa_beaches_api_url = "https://api.beaches.ie/odata/beaches?$expand=Incidents"

with urllib.request.urlopen(epa_beaches_api_url) as epa_beaches:
    epa_beaches_parsed = json.loads(epa_beaches.read().decode())

epa_beaches_parsed = epa_beaches_parsed["value"]
epa_beaches_parsed = [[x["Code"],
                       x["Name"],
                       x["CountyName"],
                       x["EtrsY"],
                       x["EtrsX"],
                       x["ClosedTypeName"],
                       x["LastSampleOn"],
                       x["NextMonitoringDate"],
                       x["IsBlueFlag"],
                       x["IsGreenCoast"]] for x in epa_beaches_parsed]
epa_beaches_parsed = pd.DataFrame(epa_beaches_parsed,
                                  columns=["EdenCode",
                                           "Name",
                                           "County",
                                           "Latitude",
                                           "Longitude",
                                           "ClosedStatus",
                                           "LastSampleDate",
                                           "NextMonitoringDate",
                                           "IsBlueFlag",
                                           "IsGreenCoast"])

#
# Get all the locations from the Marine Institute's predictions
#

marine_institute_forecasts_url = "https://erddap.marine.ie/erddap/tabledap/" + \
                                 "IMI-TidePrediction_epa.json?longitude%2C" + \
                                 "latitude%2CstationID&distinct()"

with urllib.request.urlopen(
        marine_institute_forecasts_url) as mi_forecast_location:
    mi_forecast_location_parsed = json.loads(
        mi_forecast_location.read().decode())

mi_forecast_location_parsed = mi_forecast_location_parsed["table"]["rows"]
mi_forecast_location_parsed = [[x[2].split("_MODELLED")[0],
                                x[0],
                                x[1]] for x in mi_forecast_location_parsed]

mi_forecast_location_parsed = pd.DataFrame(mi_forecast_location_parsed,
                                           columns=["EdenCode",
                                                    "ErddapLongitude",
                                                    "ErddapLatitude"])

#
# Mege the EPA and Marine Institute locations
#

merged_beaches = mi_forecast_location_parsed.merge(epa_beaches_parsed,
                                                   on="EdenCode")
del epa_beaches_parsed
del mi_forecast_location_parsed

#
# Get the Met Eireann weather warnings
#   TODO: Parse the weather warnings
#

met_eireann_weather_warnings_url = "https://www.met.ie/Open_Data/json/" + \
                                   "warning_IRELAND.json"

with urllib.request.urlopen(
        met_eireann_weather_warnings_url) as met_eireann_warnings:
    met_eireann_warnings_parsed = json.loads(
        met_eireann_warnings.read().decode())

#
# Get today's date and UTC time limits
#   TODO: check if we're on DST or not and change the time zone appropriately
#

erddap_tides_start = (datetime.datetime.today() -
                      datetime.timedelta(days=1)).strftime(
    '%Y-%m-%dT21:00:00Z')
erddap_tides_end = (datetime.datetime.today() +
                    datetime.timedelta(days=1)).strftime(
    '%Y-%m-%dT03:00:00Z')
_is_daylight_saving = False

met_eireann_start: str
met_eireann_end: str

if _is_daylight_saving:
    met_eireann_start = (datetime.datetime.today() -
                         datetime.timedelta(days=1)).strftime(
        '%Y-%m-%dT23:00')
    met_eireann_end = datetime.datetime.today().strftime('%Y-%m-%dT22:59')
else:
    met_eireann_start = datetime.datetime.today().strftime('%Y-%m-%dT00:00')
    met_eireann_end = datetime.datetime.today().strftime('%Y-%m-%dT23:59')

#
# Get the MI tide forecasts for today
#

mi_tide_forecasts_url = "https://erddap.marine.ie/erddap/tabledap/" + \
                        "IMI-TidePrediction_epa.json?time%2CstationID%2C" + \
                        "sea_surface_height&time%3E=" + \
                        "{}&time%3C{}&distinct()".format(erddap_tides_start,
                                                         erddap_tides_end)

with urllib.request.urlopen(mi_tide_forecasts_url) as mi_tide_forecasts:
    mi_tide_forecasts_parsed = json.loads(mi_tide_forecasts.read().decode())

mi_tide_forecasts_parsed = mi_tide_forecasts_parsed["table"]["rows"]

if _is_daylight_saving:
    beach_reduced_information = [[], [], []]
else:
    mi_tide_today = pd.DataFrame([[x[0],
                                   x[1].split("_MODELLED")[0],
                                   x[2]] for x in mi_tide_forecasts_parsed
                                  if x[0].startswith(
                                      datetime.datetime.today().strftime(
                                          '%Y-%m-%d'))],
                                 columns=["Date",
                                          "EdenCode",
                                          "SeaLevel"])
    
    beach_reduced_information = [[x[0],
                                  x[1].split("_MODELLED")[0],
                                  x[2]]
                                 for x in mi_tide_forecasts_parsed
                                 if x[0].startswith(
                                     datetime.datetime.today().strftime(
                                         '%Y-%m-%d'))
                                 and x[0].find(":00:00") > -1]

#
# TODO:
#    Calculate the high and low tides for each station
#

#
# Get the Met Eireann weather forecasts for today
#

met_eireann_forecast_url = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts" + \
                           "/locationforecast?lat={};long={};from={};to={}"

_lats_lons = list(zip(merged_beaches["ErddapLatitude"],
                      merged_beaches["ErddapLongitude"],
                      merged_beaches["EdenCode"]))
_met_eireann_forecast_urls = [[met_eireann_forecast_url.format(
    x[0], x[1], met_eireann_start, met_eireann_end), x[2]]
                              for x in _lats_lons]

#
# TODO:
#   Enable for all URLs, not just first four
#

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    met_eireann_forecasts = executor.map(met_eireann_forecast_fetcher,
                                         _met_eireann_forecast_urls)

met_eireann_forecasts = [y for x in met_eireann_forecasts for y in x]

#
# TODO:
#   Get the MI spatial models for today
#   Ensure that we are on a model grid location that isn't null
#   Enable for all URLs, not just first four
#

neatl_url_pattern = "https://erddap.marine.ie/erddap/griddap/" + \
                    "IMI_NEATL.json?sea_surface_temperature" + \
                    "%5B({0}Z):1:({1}Z)%5D%5B({2}):1:({2})" + \
                    "%5D%5B({3}):1:({3})%5D," + \
                    "sea_surface_salinity%5B({0}Z):1:({1})%5D%5B" + \
                    "({2}):1:({2})%5D%5B({3}):1:({3})%5D," + \
                    "sea_surface_x_velocity%5B({0}Z):1:({1}Z)%5D%5B" + \
                    "({2}):1:({2})%5D%5B({3}):1:({3})%5D," + \
                    "sea_surface_y_velocity%5B({0}Z):1:({1}Z)%5D%5B" + \
                    "({2}):1:({2})%5D%5B({3}):1:({3})%5D"

swan_url_pattern = "https://erddap.marine.ie/erddap/griddap/" + \
                   "IMI_EATL_WAVE.json?significant_wave_height" + \
                   "%5B({0}Z):1:({1}Z)" + \
                   "%5D%5B({2}):1:({2})" + \
                   "%5D%5B({3}):1:({3})%5D," + \
                   "swell_wave_height%5B({0}Z):1:({1}Z)" + \
                   "%5D%5B({2}):1:({2})%5D%5B({3}):1:({3})%5D," + \
                   "mean_wave_direction%5B({0}Z):1:({1}Z)%5D%5B" + \
                   "({2}):1:({2})%5D%5B({3}):1:({3})%5D," + \
                   "mean_wave_period%5B({0}Z):1:({1}Z)%5D%5B" + \
                   "({2}):1:({2})%5D%5B({3}):1:({3})%5D"

neatl_and_swan_urls = [[neatl_url_pattern.format(met_eireann_start,
                                                 met_eireann_end,
                                                 ((x[0] * 10000) -
                                                  ((x[0] * 10000)
                                                  % 125)) / 10000,
                                                 ((x[1] * 10000) -
                                                  ((x[1] * 10000)
                                                  % 125)) / 10000),
                        swan_url_pattern.format(met_eireann_start,
                                                met_eireann_end,
                                                ((x[0] * 10000) -
                                                 ((x[0] * 10000)
                                                 % 250)) / 10000,
                                                ((x[1] * 10000) -
                                                 ((x[1] * 10000)
                                                 % 250)) / 10000),
                        x[2]] for x in _lats_lons]

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    marine_institute_forecasts = executor.map(
        marine_institute_forecast_fetcher, neatl_and_swan_urls)

marine_institute_forecasts = [y for x in marine_institute_forecasts for y in x]
#
# Final data frame for summary tables
#

beach_summary = pd.DataFrame(beach_reduced_information,
                             columns=["Date",
                                      "EdenCode",
                                      "Sea Level"]).merge(
    pd.DataFrame(met_eireann_forecasts,
                 columns=["Date",
                          "EdenCode",
                          "Air Temperature",
                          "Wind Direction",
                          "Wind Speed",
                          "Wind Gust"]), on=["Date", "EdenCode"]).merge(
  pd.DataFrame(marine_institute_forecasts,
               columns=["Date",
                        "EdenCode",
                        "Sea Surface Temperature",
                        "Sea Surface Salinity",
                        "Sea Surface X Velocity",
                        "Sea Surface Y Velocity",
                        "Sea Surface Current Speed",
                        "Significant Wave Height",
                        "Swell Wave Height",
                        "Mean Wave Direction",
                        "Mean Wave Period"]), on=["Date", "EdenCode"])

app = dash.Dash()
app.layout = html.Div([
    dcc.Dropdown(
        options= [{"label": "{}, {}".format(x, y), 
            "value": z} for (x, y, z) in zip(merged_beaches["Name"].tolist(), 
                merged_beaches["County"].tolist(), 
                merged_beaches["EdenCode"].tolist())],
        value="IEWEBWC170_0000_0100",
        id="dropdown"
    ),
    html.Div([html.P("Dashboard contains data from the Marine Institute, the Environment Protection Agency and Met Eireann")]),
    dcc.Graph(id="sealevel-graph"),
    dash_table.DataTable(id="beach-summary-table",
        columns=[{"name": ["", "Date"], "id": "Date"},
                 {"name": ["", "Sea Level (m)"], "id": "Sea Level"},
                 {"name": ["Temperature (deg C)", "Water"], "id": "Sea Surface Temperature"},
                 {"name": ["Temperature (deg C)", "Air"], "id": "Air Temperature"},
                 {"name": ["", "Current Speed"], "id": "Sea Surface Current Speed"},
                 {"name": ["Wave", "Swell Height (m)"], "id": "Swell Wave Height"},
                 {"name": ["Wave", "Period (s)"], "id": "Mean Wave Period"},
                 {"name": ["Wind", "Speed"], "id": "Wind Speed"},
                 {"name": ["Wind", "Direction"], "id": "Wind Direction"}],
                 merge_duplicate_headers=True)
])

@app.callback(
    Output('sealevel-graph', 'figure'),
    Input('dropdown', 'value')
)
def update_sealevel_graph(value):
    df = mi_tide_today
    mask = df['EdenCode'].isin([value])
    fig = px.line(df[mask],
        x='Date', y='SeaLevel',
        height=250)
    return fig

@app.callback(
    Output('beach-summary-table', 'data'),
    Input('dropdown', 'value')
)
def update_beach_summary_table(value):
    return beach_summary[beach_summary['EdenCode'].isin([value])].to_dict("records")

if __name__ == '__main__':
    app.run_server()
