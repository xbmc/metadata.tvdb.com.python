import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlencode

from . import cache
from .utils import logger

FANARTTV_URL = 'https://webservice.fanart.tv/v3/tv/{}'
FANARTTV_PARAMS = {'api_key': 'b018086af0e1478479adfc55634db97d'}

HEADERS = {
    'User-Agent': 'Kodi TV Show scraper by Team Kodi; contact pkscout@kodi.tv',
    'Accept': 'application/json'
}

IMAGE_TYPE_DICT = {
    'hdtvlogo': 'clearlogo',
    'clearlogo': 'clearlogo',
    'hdclearart': 'clearart',
    'clearart': 'clearart',
    'tvposter': 'poster',
    'seasonposter': 'poster',
    'tvbanner': 'banner',
    'seasonbanner': 'banner',
    'tvthumb': 'landscape',
    'seasonthumb': 'landscape',
    'characterart': 'characterart',
    'showbackground': 'fanart',
}


def get_fanarttv_art(id, show, settings):
    if not (show and id and settings.getSettingBool('enable_fanarttv')):
        return

    show.FanartTV = {
        'artwork': [],
        'fanart': []
    }

    resp = cache.load_fanarttv_info_from_cache(id)

    if resp is None:
        client_key = settings.getSettingString('fanarttv_clientkey')
        if client_key:
            FANARTTV_PARAMS['client_key'] = client_key

        fanarttv_url = FANARTTV_URL.format(id) + '?' + urlencode(FANARTTV_PARAMS)
        req = Request(fanarttv_url, headers=HEADERS)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                logger.error('failed to reach the remote site\nSite: {}\nReason: {}'.format(fanarttv_url, e.reason))
            elif hasattr(e, 'code'):
                logger.error('remote site unable to fulfill the request\nSite: {}\nError code: {}'.format(fanarttv_url, e.code))
            response = None

        if response is None:
            return

        resp = json.loads(response.read().decode('utf-8'))
        cache.cache_fanarttv_info(id, resp)

    language = settings.getSettingString('language')

    for key in resp:
        if key not in IMAGE_TYPE_DICT:
            continue

        image_type = IMAGE_TYPE_DICT[key]
        subKey = 'fanart' if key == 'showbackground' else 'artwork'

        for item in resp[key]:
            if not (item['lang'] == '' or item['lang'] == '00' or item['lang'] == language or item['lang'] == 'en'):
                continue

            image = {
                'url': item['url'],
                'preview': item['url'].replace('.fanart.tv/fanart/', '.fanart.tv/preview/'),
                'type': image_type,
                'likes': int(item['likes'])
            }
            if key.startswith('season') and item['season']:
                image['season'] = item['season']

            show.FanartTV[subKey].append(image)
