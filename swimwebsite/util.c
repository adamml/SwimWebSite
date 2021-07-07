#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <swimwebsite/util.h>
#include <curl/curl.h>

struct string {
  char *ptr;
  size_t len;
};

void init_string(struct string *s) {
  s->len = 0;
  s->ptr = malloc(s->len+1);
  if (s->ptr == NULL) {
    fprintf(stderr, "malloc() failed\n");
    exit(EXIT_FAILURE);
  }
  s->ptr[0] = '\0';
}

size_t writefunc(void *ptr, size_t size, size_t nmemb, struct string *s)
{
  size_t new_len = s->len + size*nmemb;
  s->ptr = realloc(s->ptr, new_len+1);
  if (s->ptr == NULL) {
    fprintf(stderr, "realloc() failed\n");
    exit(EXIT_FAILURE);
  }
  memcpy(s->ptr+s->len, ptr, size*nmemb);
  s->ptr[new_len] = '\0';
  s->len = new_len;

  return size*nmemb;
}

char * get_string_from_url(char *url)
{
  CURL *curl;
  curl = curl_easy_init();
  struct string s;
  if(curl) {
    CURLcode res;
    init_string(&s);

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writefunc);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &s);
    res = curl_easy_perform(curl);
    if(res!=CURLE_OK){
      //printf("%s\n", curl_easy_strerror(res));
      curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
      res = curl_easy_perform(curl);
      if(res!=CURLE_OK){
        printf("%s\n", curl_easy_strerror(res));
      }
    }

    /* always cleanup */
    curl_easy_cleanup(curl);
  }
  return s.ptr;
}


char *repl_str(const char *str, const char *from, const char *to) {

	/* Adjust each of the below values to suit your needs. */

	/* Increment positions cache size initially by this number. */
	size_t cache_sz_inc = 16;
	/* Thereafter, each time capacity needs to be increased,
	 * multiply the increment by this factor. */
	const size_t cache_sz_inc_factor = 3;
	/* But never increment capacity by more than this number. */
	const size_t cache_sz_inc_max = 1048576;

	char *pret, *ret = NULL;
	const char *pstr2, *pstr = str;
	size_t i, count = 0;
	#if (__STDC_VERSION__ >= 199901L)
	uintptr_t *pos_cache_tmp, *pos_cache = NULL;
	#else
	ptrdiff_t *pos_cache_tmp, *pos_cache = NULL;
	#endif
	size_t cache_sz = 0;
	size_t cpylen, orglen, retlen, tolen, fromlen = strlen(from);

	/* Find all matches and cache their positions. */
	while ((pstr2 = strstr(pstr, from)) != NULL) {
		count++;

		/* Increase the cache size when necessary. */
		if (cache_sz < count) {
			cache_sz += cache_sz_inc;
			pos_cache_tmp = realloc(pos_cache, sizeof(*pos_cache) * cache_sz);
			if (pos_cache_tmp == NULL) {
				goto end_repl_str;
			} else pos_cache = pos_cache_tmp;
			cache_sz_inc *= cache_sz_inc_factor;
			if (cache_sz_inc > cache_sz_inc_max) {
				cache_sz_inc = cache_sz_inc_max;
			}
		}

		pos_cache[count-1] = pstr2 - str;
		pstr = pstr2 + fromlen;
	}

	orglen = pstr - str + strlen(pstr);

	/* Allocate memory for the post-replacement string. */
	if (count > 0) {
		tolen = strlen(to);
		retlen = orglen + (tolen - fromlen) * count;
	} else	retlen = orglen;
	ret = malloc(retlen + 1);
	if (ret == NULL) {
		goto end_repl_str;
	}

	if (count == 0) {
		/* If no matches, then just duplicate the string. */
		strcpy(ret, str);
	} else {
		/* Otherwise, duplicate the string whilst performing
		 * the replacements using the position cache. */
		pret = ret;
		memcpy(pret, str, pos_cache[0]);
		pret += pos_cache[0];
		for (i = 0; i < count; i++) {
			memcpy(pret, to, tolen);
			pret += tolen;
			pstr = str + pos_cache[i] + fromlen;
			cpylen = (i == count-1 ? orglen : pos_cache[i+1]) - pos_cache[i] - fromlen;
			memcpy(pret, pstr, cpylen);
			pret += cpylen;
		}
		ret[retlen] = '\0';
	}

end_repl_str:
	/* Free the cache and return the post-replacement string,
	 * which will be NULL in the event of an error. */
	free(pos_cache);
	return ret;
}

char * countyToFipsCode(County c){
  switch (c) {
    case CARLOW:
      return "EI01";
    case CAVAN:
      return "EI02";
    case CLARE:
      return "EI03";
    case CORK:
      return "EI04";
    case DONEGAL:
      return "EI06";
    case DUBLIN:
      return "EI07";
    case GALWAY:
      return "EI10";
    case KERRY:
      return "EI11";
    case KILDARE:
      return "EI12";
    case KILKENNY:
      return "EI13";
    case LAOIS:
      return "EI15";
    case LEITRIM:
      return "EI14";
    case LIMERICK:
      return "EI15";
    case LONGFORD:
      return "EI18";
    case LOUTH:
      return "EI19";
    case MAYO:
      return "EI20";
    case MEATH:
      return "EI21";
    case MONAGHAN:
      return "EI22";
    case OFFALY:
      return "EI23";
    case ROSCOMMON:
      return "EI24";
    case SLIGO:
      return "EI25";
    case TIPPERARY:
      return "EI26";
    case WATERFORD:
      return "EI27";
    case WESTMEATH:
      return "EI29";
    case WEXFORD:
      return "EI30";
    case WICKLOW:
      return "EI31";
    default:
      return (char *)-1;
  }
}
