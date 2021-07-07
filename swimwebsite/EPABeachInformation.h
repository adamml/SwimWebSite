#ifndef COM_GITHUB_ADAMML_SWIMWEBSITE_EPABEACHINFORMATION
#define COM_GITHUB_ADAMML_SWIMWEBSITE_EPABEACHINFORMATION

#include <swimwebsite/util.h>

/**
struct EPABeachInformation
--------------------------

Used for storing information gleaned from the Environment Protection Agency's
beaches.ie API

.. note::
  This structure requires access to the County enum from <swimwebsite/util.h>

  :param beach_name: The name of the beach
  :type beach_name: char [200]
  :param blue_flag_status: 0 if no Blue Flag, otherwise 1
  :type blue_flag_status: int
  :param county: The name of the county in which the beach is located
  :type county: char[30]
  :param enum_county: Enumerated value for the county in which the beach is
                      located. If the value of
  :type enum_county: County
  :param last_updated_date: The date on which the beaches.ie record was last
                            last updated
  :type last_updated_date: char[30]
  :param latitude: The latitude at which the beach can be found
  :type latitude: float
  :param longitude: The longitude at which the beach can be found
  :type longitude: float
  :param next_water_quality: The date at which the beach's water quality is next
                              due to be tested
  :type next_water_quality: char[30]
  :param restrictions_in_place: 0 if no restrictions are in place at the beach,
                                otherwise 1
  :type restrictions_in_place: int
  :param water_quality: A description of the water quality at the beach
  :type water_quality: char[200]

*/
struct EPABeachInformation_t;
typedef struct EPABeachInformation_t{
  char beach_name[200];
  int blue_flag_status;
  char county[30];
  County enum_county;
  char last_updated_date[30];
  float latitude;
  float longitude;
  char next_water_quality[30];
  int restrictions_in_place;
  char water_quality[200];
}EPABeachInformation;

/**
void init_epa_beach_information(EPABeachInformation \*beach, char \*beach_id)
-----------------------------------------------------------------------------

Inititalises a EPABeachInformation structuree

.. note::

  This function requires access to the internet in order to call the Environment
  Protection Agency's beaches.ie API. Thw internet call requires curl.h and
  libcurl. The function also uses the jsmn [#]_ library to parse the returned
  JSON.

    :param \*beach: The structure to be initialised
    :type \*beach: EPABeachInformation
    :param \*beach_id: The Eden code for the beach from the Environment
           Protection Agency's API
    :type \*beach_id: char
    :rtype: void

.. rubric: Footnotes

.. [#] https://github.com/zserge/jsmn

*/
void init_epa_beach_information(EPABeachInformation *beach, char *beach_id);

#endif
