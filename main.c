#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <swimwebsite/EPABeachInformation.h>
#include <swimwebsite/util.h>

int main(){
  EPABeachInformation epabeach;
  init_epa_beach_information(&epabeach, "IESWBWC090_0000_0300");
  printf("%s, %s\n", epabeach.beach_name, epabeach.county);
  printf("%.5f %.5f\n", epabeach.latitude, epabeach.longitude);
  printf("%s\n", countyToFipsCode(epabeach.enum_county));
  return 1;
}
