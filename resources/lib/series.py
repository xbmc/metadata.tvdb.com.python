#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
from . import tvdb
from .utils import log
from .artwork import add_artworks
from .imdb_rating import get_imdb_rating_and_votes


ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])


# add the found shows to the list
def search_series(title, year=None):
    log('Searching for TV show "{}"'.format(title))

    search_results = tvdb.search_series_api(title)
    if year is not None:
        filtered_search_result = tvdb.filter_by_year(search_results, year)
        if len(filtered_search_result) > 0:
            search_results = _find_exact_series_match(
                filtered_search_result, title)
        else:
            search_results = _find_exact_series_match(search_results, title)

    if search_results is None:
        return
    for show in search_results:
        liz = xbmcgui.ListItem(show['seriesName'], offscreen=True)
        # liz.setProperty('relevance', '0.5')
        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=str(show['id']),
            listitem=liz,
            isFolder=True
        )


def _find_exact_series_match(series_list, title: str):
    log(series_list)
    first_or_default = next(
        (x for x in series_list if x['seriesName'] == title), None)

    if first_or_default is None:
        return series_list
    else:
        return [first_or_default]

    # get the details of the found series


def get_series_details(id, images_url: str):
    log('Find info of tvshow with id {id}'.format(id=id))
    show = tvdb.get_series_details_api(id)
    if not show:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    liz = xbmcgui.ListItem(show.seriesName, offscreen=True)
    liz.setInfo('video',
                {'title': show.seriesName,
                 'plot': show.overview,
                 'duration': int(show.runtime) * 60 if show.runtime else 0,
                 'mpaa': show.rating,
                 'genre': show.genre,
                 'studio': show.network,
                 'premiered': show.firstAired,
                 'status': show.status,
                 'episodeguide': show.id
                 })
    isimdbdef = (show.imdbId and ADDON.getSetting('RatingS') == 'IMDb')
    liz.setRating("tvdb", show.siteRating, show.siteRatingCount, not isimdbdef)
    if show.imdbId:
        liz.setUniqueIDs({'tvdb': show.id, 'imdb': show.imdbId}, 'tvdb')
        imdb_info = get_imdb_rating_and_votes(show.imdbId)
        if imdb_info['votes'] > 0:
            liz.setRating(
                "imdb", imdb_info['rating'], imdb_info['votes'], isimdbdef)
    else:
        liz.setUniqueIDs({'tvdb': show.id}, 'tvdb')

    liz.setCast(_get_cast(show, images_url))
    add_artworks(show, liz, images_url)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)


def _get_cast(show, images_url: str):
    actors = []
    for actor in show.actors:
        if actor['image']:
            actors.append(
                {'name': actor['name'], 'role': actor['role'], 'thumbnail': images_url+actor['image']})
        else:
            actors.append({'name': actor['name'], 'role': actor['role']})
    return actors
