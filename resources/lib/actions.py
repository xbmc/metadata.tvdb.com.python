#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xbmcplugin
import sys
import requests
import urllib.request
import urllib.parse
import urllib.error
from . import series
from . import episodes
from .artwork import get_artworks
from .utils import log
from .nfo import get_show_from_nfo


HANDLE = int(sys.argv[1])
images_url = 'http://thetvdb.com/banners/'


def run():
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    log('Called addon with params: {}'.format(sys.argv))
    if 'action' in params:
        action = urllib.parse.unquote_plus(params["action"])
        if action == 'find' and 'title' in params:
            series.search_series(urllib.parse.unquote_plus(
                params["title"]), params.get("year", None))
        elif action.lower() == 'nfourl':
            get_show_from_nfo(params['nfo'], images_url)
        elif action == 'getdetails' and 'url' in params:
            series.get_series_details(
                urllib.parse.unquote_plus(params["url"]), images_url)
        elif action == 'getepisodelist' and 'url' in params:
            episodes.get_series_episodes(
                urllib.parse.unquote_plus(params["url"]))
        elif action == 'getepisodedetails' and 'url' in params:
            episodes.get_episode_details(
                urllib.parse.unquote_plus(params["url"]), images_url)
        elif action == 'getartwork' and 'id' in params:
            get_artworks(urllib.parse.unquote_plus(params["id"]), images_url)
    xbmcplugin.endOfDirectory(HANDLE)
