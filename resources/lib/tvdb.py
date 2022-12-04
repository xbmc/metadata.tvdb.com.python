#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xbmcaddon
import tvdbsimple as tvdb

from . import cache
from .utils import safe_get

ADDON = xbmcaddon.Addon()
tvdb.KEYS.API_KEY = 'd60d3c015fdb148931e8254c0e96f072'
tvdb.KEYS.API_TOKEN = ADDON.getSetting('token')


def filter_by_year(shows, year: int):
    ret = []
    for show in shows:
        firstAired = safe_get(show, 'firstAired', '')
        if firstAired and firstAired.startswith(str(year)):
            ret.append(show)
    return ret


def search_series_api(title: str, settings, imdb_id: str = ''):
    search = tvdb.Search()
    ret = None
    try:
        ret = search.series(title, language=settings.getSettingString(
            'language'), imdbId=imdb_id)
    except:
        pass
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)
    return ret


def search_series_by_slug_api(slug: str, settings):
    search = tvdb.Search()
    ret = None
    try:
        ret = search.series(slug=slug, language=settings.getSettingString(
            'language'))
    except:
        pass
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)
    return ret


def get_series_details_api(show_id, settings, all=True):
    language = settings.getSettingString('language')
    show = cache.load_show_info_from_cache(show_id, language, 'series')
    if show is not None:
        return show

    show = tvdb.Series(show_id, language=language)
    if all:
        try:
            show.info()
        except:
            return None
        try:
            show.actors()
        except:
            show.actors = []
    try:
        show.Images.fanart()
    except:
        show.Images.fanart = []
    try:
        show.Images.poster()
    except:
        show.Images.poster = []
    try:
        show.Images.series()
    except:
        show.Images.series = []
    try:
        show.Images.season()
    except:
        show.Images.season = []
    try:
        show.Images.seasonwide()
    except:
        show.Images.seasonwide = []
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)

    if all:
        cache.cache_show_info(show_id, show, language, 'series')

    return show


def get_series_episodes_api(show_id, settings):
    ret = None
    language = settings.getSettingString('language')
    ret = cache.load_show_info_from_cache(show_id, language, 'episodes')
    if ret is not None:
        return ret

    showeps = tvdb.Series_Episodes(show_id, language=language)
    try:
        ret = showeps.all()
    except:
        pass
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)

    cache.cache_show_info(show_id, ret, language, 'episodes')
    return ret


def get_episode_details_api(episode_id, settings):
    language = settings.getSettingString('language')

    ep = cache.load_episode_info_from_cache(episode_id, language)
    if ep is not None:
        return ep

    ep = tvdb.Episode(episode_id, language=language)
    try:
        ep.info()
    except:
        return None
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)

    cache.cache_episode_info(episode_id, ep, language)
    return ep
