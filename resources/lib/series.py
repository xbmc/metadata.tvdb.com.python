#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xbmcaddon
import xbmcgui
import xbmcplugin
import sys
from . import tvdb
from .utils import log
from .artwork import add_artworks
from .ratings import ratings


ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])


def search_series(title, year=None) -> None:
    # add the found shows to the list
    log('Searching for TV show "{}"'.format(title))

    search_results = tvdb.search_series_api(title)
    search_results = _filter_exact_matches(search_results, title)
    if year is not None:
        filtered_search_result = tvdb.filter_by_year(search_results, year)

        search_results = filtered_search_result if len(
            filtered_search_result) > 0 else search_results

    if search_results is None:
        return
    for show in search_results:
        liz = xbmcgui.ListItem(show['seriesName'], offscreen=True)
        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=str(show['id']),
            listitem=liz,
            isFolder=True
        )


def search_series_by_imdb_id(imdb_id) -> None:
    # add the found shows to the list
    log('Searching for TV show with imdb id "{}"'.format(imdb_id))

    search_results = tvdb.search_series_api('', imdb_id)

    if search_results is None:
        return
    for show in search_results:
        liz = xbmcgui.ListItem(show['seriesName'], offscreen=True)
        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=str(show['id']),
            listitem=liz,
            isFolder=True
        )


def search_series_by_tvdb_id(tvdb_id) -> None:
    # add the found shows to the list
    log('Searching for TV show with tvdb id "{}"'.format(tvdb_id))

    search_results = tvdb.get_series_details_api(tvdb_id)

    if search_results is None:
        return
    for show in search_results:
        liz = xbmcgui.ListItem(show.seriesName, offscreen=True)
        xbmcplugin.addDirectoryItem(
            handle=HANDLE,
            url=str(show.id),
            listitem=liz,
            isFolder=True
        )


def _filter_exact_matches(series_list, title: str):
    ret = []
    for show in series_list:
        if show['seriesName'] == title:
            ret.append(show)
    return ret


def get_series_details(id, images_url: str):
    # get the details of the found series
    log('Find info of tvshow with id {id}'.format(id=id))
    show = tvdb.get_series_details_api(id)
    if not show:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    liz = xbmcgui.ListItem(show.seriesName, offscreen=True)
    liz.setInfo('video',
                {'title': show.seriesName,
                 'tvshowtitle': show.seriesName,
                 'plot': show.overview,
                 'plotoutline': show.overview,
                 'duration': int(show.runtime) * 60 if show.runtime else 0,
                 'mpaa': show.rating,
                 'genre': show.genre,
                 'studio': show.network,
                 'premiered': show.firstAired,
                 'status': show.status,
                 'episodeguide': show.id,
                 'mediatype': 'tvshow'
                 })

    ratings(liz, show, False)

    if show.imdbId:
        liz.setUniqueIDs({'tvdb': show.id, 'imdb': show.imdbId}, 'tvdb')
    else:
        liz.setUniqueIDs({'tvdb': show.id}, 'tvdb')

    liz.setCast(_get_cast(show, images_url))
    add_artworks(show, liz, images_url)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)


def _get_cast(show, images_url: str):
    actors = []
    for actor in sorted(show.actors, key=lambda actor: actor['sortOrder']):
        if actor['image']:
            actors.append(
                {'name': actor['name'], 'role': actor['role'], 'thumbnail': images_url+actor['image']})
        else:
            actors.append({'name': actor['name'], 'role': actor['role']})
    return actors
