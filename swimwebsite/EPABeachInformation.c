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

  if (strcmp(this_county_name, "carlow")==0) {return CARLOW;}
  else if (strcmp(this_county_name, "cavan")==0) {return CAVAN;}
  else if (strcmp(this_county_name, "clare")==0) {return CLARE;}
  else if (strcmp(this_county_name, "cork")==0) {return CORK;}
  else if (strcmp(this_county_name, "donegal")==0) {return DONEGAL;}
  else if (strcmp(this_county_name, "dublin")==0) {return DUBLIN;}
  else if (strcmp(this_county_name, "galway")==0) {return GALWAY;}
  else if (strcmp(this_county_name, "kerry")==0) {return KERRY;}
  else if (strcmp(this_county_name, "kildare")==0) {return KILDARE;}
  else if (strcmp(this_county_name, "kilkenny")==0) {return KILKENNY;}
  else if (strcmp(this_county_name, "laois")==0) {return LAOIS;}
  else if (strcmp(this_county_name, "leitim")==0) {return LEITRIM;}
  else if (strcmp(this_county_name, "limerick")==0) {return LIMERICK;}
  else if (strcmp(this_county_name, "longford")==0) {return LONGFORD;}
  else if (strcmp(this_county_name, "louth")==0) {return LOUTH;}
  else if (strcmp(this_county_name, "mayo")==0) {return MAYO;}
  else if (strcmp(this_county_name, "meath")==0) {return MEATH;}
  else if (strcmp(this_county_name, "monaghan")==0) {return MONAGHAN;}
  else if (strcmp(this_county_name, "offaly")==0) {return OFFALY;}
  else if (strcmp(this_county_name, "roscommon")==0) {return ROSCOMMON;}
  else if (strcmp(this_county_name, "sligo")==0) {return SLIGO;}
  else if (strcmp(this_county_name, "tipperary")==0) {return TIPPERARY;}
  else if (strcmp(this_county_name, "waterford")==0) {return WATERFORD;}
  else if (strcmp(this_county_name, "westmeath")==0) {return WESTMEATH;}
  else if (strcmp(this_county_name, "wexford")==0) {return WEXFORD;}
  else if (strcmp(this_county_name, "wicklow")==0) {return WICKLOW;}
  else {return GALWAY;}
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
  char blue_flag_status[] = "IsBlueFlag";
  char blue_flag_status_raw[5];
  char buffer[1024];
  char county_name[] = "CountyName";
  char etrsx[] = "EtrsX";
  char etrsx_raw[50];
  char etrsy[] = "EtrsY";
  char etrsy_raw[50];
  char last_updated_date[] = "LastUpdatedOn";
  char next_water_quality[] = "NextMonitoringDate";
  char restrictions_in_place[] = "HasRestrictionInPlace";
  char restrictions_in_place_raw[5];
  char true_str[] = "true";
  for(i = 0; i < r; i+=2){
    snprintf(buffer, sizeof(buffer), "%.*s",t[i].end - t[i].start, raw_json + t[i].start);
    if(strcmp(buffer, beach_name) == 0){
      snprintf(beach->beach_name, sizeof(beach->beach_name), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
    }
    if(strcmp(buffer, next_water_quality) == 0){
      snprintf(beach->next_water_quality, sizeof(beach->next_water_quality), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
    }
    if(strcmp(buffer, last_updated_date) == 0){
      snprintf(beach->last_updated_date, sizeof(beach->last_updated_date), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
    }
    if(strcmp(buffer, blue_flag_status) == 0){
      snprintf(blue_flag_status_raw, sizeof(blue_flag_status_raw), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
      if(strcmp(blue_flag_status_raw, true_str) == 0){beach->blue_flag_status = 1;}
      else {beach->blue_flag_status = 0;}
    }
    if(strcmp(buffer, restrictions_in_place) == 0){
      snprintf(restrictions_in_place_raw, sizeof(restrictions_in_place_raw), "%.*s",t[i+1].end - t[i+1].start, raw_json + t[i+1].start);
      if(strcmp(restrictions_in_place_raw, true_str) == 0){beach->restrictions_in_place = 1;}
      else {beach->restrictions_in_place = 0;}
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
