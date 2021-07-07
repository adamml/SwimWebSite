#ifndef COM_GITHUB_ADAMML_SWIMWEBSITE_UTIL_H
#define COM_GITHUB_ADAMML_SWIMWEBSITE_UTIL_H

/**
*/
char * get_string_from_url(char *url);

typedef enum {
  CARLOW,
  CAVAN,
  CLARE,
  CORK,
  DONEGAL,
  DUBLIN,
  GALWAY,
  KERRY,
  KILDARE,
  KILKENNY,
  LAOIS,
  LEITRIM,
  LIMERICK,
  LONGFORD,
  LOUTH,
  MAYO,
  MEATH,
  MONAGHAN,
  OFFALY,
  ROSCOMMON,
  SLIGO,
  TIPPERARY,
  WATERFORD,
  WESTMEATH,
  WEXFORD,
  WICKLOW
} County;

char * countyToFipsCode(County c);

char *repl_str(const char *str, const char *from, const char *to);

#endif
