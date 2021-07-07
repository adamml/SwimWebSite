#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <swimwebsite/util.h>
#include <swimwebsite/EPABeachInformation.h>

#define JSMN_HEADER
#include <jsmn/jsmn.h>

County county_name_string_to_enum_value(const char * county_name){
  int i = 0;
  char this_county_name[30];
  while(i < strlen(county_name)){
    this_county_name[i] = tolower(county_name[i]);
    i++;
  }
  this_county_name[i] = 0;

  if (strcmp(this_county_name, "carlow")==0) {
    return CARLOW;
  } else if (strcmp(this_county_name, "cavan")==0) {
    return CAVAN;
  } else if (strcmp(this_county_name, "clare")==0) {
    return CLARE;
  } else if (strcmp(this_county_name, "cork")==0) {
    return CORK;
  } else if (strcmp(this_county_name, "donegal")==0) {
    return DONEGAL;
  } else if (strcmp(this_county_name, "dublin")==0) {
    return DUBLIN;
  } else if (strcmp(this_county_name, "galway")==0) {
    return GALWAY;
  }
}

void init_epa_beach_information(EPABeachInformation *beach, char *beach_id) {
  jsmn_parser p;
  jsmntok_t t[1024];
  jsmn_init(&p);

  char url_template[] = "https://api.beaches.ie/odata/beaches?$filter=Code%20eq%20%27{}%27";
  char replace_pattern[] = "{}";
  char * url;
  url = repl_str(url_template, replace_pattern, beach_id);

  char * raw_json;
  raw_json = get_string_from_url(url);

  int r;
  r = jsmn_parse(&p, raw_json, strlen(raw_json), t, sizeof(t) / sizeof(t[0]));
  int i;
  char beach_name[] = "Name";
  char buffer[1024];
  char county_name[] = "CountyName";
  char etrsx[] = "EtrsX";
  char etrsx_raw[50];
  char etrsy[] = "EtrsY";
  char etrsy_raw[50];
  for(i = 0; i < r; i+=2){
    snprintf(buffer, sizeof(buffer), "%.*s",t[i].end - t[i].start, raw_json + t[i].start);
    if(strcmp(buffer, beach_name) == 0){
      snprintf(beach->beach_name, sizeof(beach->beach_name), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
    }
    if(strcmp(buffer, county_name) == 0){
      snprintf(beach->county, sizeof(beach->county), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
      beach->enum_county = county_name_string_to_enum_value(beach->county);
    }
    if(strcmp(buffer, etrsx) == 0){
      snprintf(etrsx_raw, sizeof(etrsx_raw), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
      beach->longitude = atof(etrsx_raw);
    }
    if(strcmp(buffer, etrsy) == 0){
      snprintf(etrsy_raw, sizeof(etrsy_raw), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
      beach->latitude = atof(etrsy_raw);
    }
  }
  free(raw_json);
  free(url);
}
