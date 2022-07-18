#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

import xbmcgui
import xbmcplugin

from . import tvdb
from .nfo import parse_episode_guide_url
from .ratings import ratings
from .utils import log

HANDLE = int(sys.argv[1])

# add the episodes of a series to the list


def get_series_episodes(id, settings):
    log(f'Find episodes of tvshow with id {id}')
    if not id.isdigit():
        # Kodi has a bug: when a show directory contains an XML NFO file with
        # episodeguide URL, that URL is always passed here regardless of
        # the actual parsing result in get_show_id_from_nfo()
        parse_result = parse_episode_guide_url(id)
        if not parse_result:
            return

        if parse_result.provider == 'thetvdb':
            id = parse_result.show_id
            log(f'Changed show id to {id}')

    episodes = tvdb.get_series_episodes_api(id, settings)

    if not episodes:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    seasonVar = 'airedSeason'
    epNumberVar = 'airedEpisodeNumber'
    if (settings.getSettingBool('dvdorder') == True):
        seasonVar = 'dvdSeason'
        epNumberVar = 'dvdEpisodeNumber'
    for ep in episodes:
        liz = xbmcgui.ListItem(ep['episodeName'], offscreen=True)
        details = {'title': ep['episodeName'],
                   'aired': ep['firstAired']
                   }
        if (settings.getSettingBool('absolutenumber') == True and ep[seasonVar] > 0):
            details['season'] = 1
            details['episode'] = ep['absoluteNumber']
        else:
            details['season'] = ep[seasonVar]
            details['episode'] = ep[epNumberVar]
        liz.setInfo('video', details)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=str(
            ep['id']), listitem=liz, isFolder=True)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

# get the details of the found episode


def get_episode_details(id, images_url: str, settings):
    log(f'Find info of episode with id {id}')
    ep = tvdb.get_episode_details_api(id, settings)
    if not ep:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    liz = xbmcgui.ListItem(ep.episodeName, offscreen=True)
    details = {'title': ep.episodeName,
               'plot': ep.overview,
               'plotoutline': ep.overview,
               'credits': ep.writers,
               'cast': ep.guestStars,
               'director': ep.directors,
               'premiered': ep.firstAired,
               'aired': ep.firstAired,
               'mediatype': 'episode'
               }

    if ep.airsAfterSeason and ep.airsAfterSeason >= 0:
        details['sortseason'] = 10000
        details['sortepisode'] = ep.airsAfterSeason
    elif ep.airsBeforeSeason and ep.airsBeforeSeason >= 0:
        details['sortepisode'] = ep.airsBeforeSeason
        details['sortseason'] = ep.airsBeforeEpisode

    seasonFunc = lambda e: e.airedSeason
    epNumberFunc = lambda e: e.airedEpisodeNumber
    if (settings.getSettingBool('dvdorder') == True):
        seasonFunc = lambda e: e.dvdSeason
        epNumberFunc = lambda e: e.dvdEpisodeNumber
    if (settings.getSettingBool('absolutenumber') == True and seasonFunc(ep) > 0):
        details['season'] = 1
        details['episode'] = ep.absoluteNumber
    else:
        details['season'] = seasonFunc(ep)
        details['episode'] = epNumberFunc(ep)

    liz.setInfo('video', details)

    ratings(liz, ep, True, settings)

    if ep.imdbId:
        liz.setUniqueIDs({'tvdb': ep.id, 'imdb': ep.imdbId}, 'tvdb')
    else:
        liz.setUniqueIDs({'tvdb': ep.id}, 'tvdb')

    if ep.filename:
        liz.addAvailableArtwork(images_url+ep.filename)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)
