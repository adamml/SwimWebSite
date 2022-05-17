import json
import logging
import urllib.request

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s {} %(message)s'.format(__name__))

def EPAData(beach_id):
    """Gets the data for a given beach from the EPA's beaches.ie API

    Args:
        beach_id: A `str` of the identifier for the beach within the API.

    Returns:
        A dict of information for the beach or None if there is an error with
        the URL
    """
    base_url = "https://api.beaches.ie/odata/beaches?$filter=Code%20eq%20%27{}%27"
    try:
        with urllib.request.urlopen(base_url.format(beach_id)) as resp:
            return json.loads(resp.read())
    except urllib.error.URLError as e:
        log.error(e)

print(epa_data = EPAData("IESWBWC090_0000_0300"))
