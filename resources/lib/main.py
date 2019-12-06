#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import sys
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import requests
import re
import tvdbsimple as tvdb

ADDON = xbmcaddon.Addon()
ID = ADDON.getAddonInfo('id')
HANDLE = int(sys.argv[1])
tvdb.KEYS.API_KEY = '439DFEBA9D3059C6'
tvdb.KEYS.API_TOKEN = ADDON.getSetting('token')
images_url = 'http://thetvdb.com/banners/'

# log function
def log(msg):
    xbmc.log(msg='{addon}: {msg}'.format(addon=ID, msg=msg), level=xbmc.LOGDEBUG)

# get addon url params
def get_params():
    if not sys.argv[2]:
        return {}
    return dict(urllib.parse.parse_qsl(sys.argv[2].lstrip('?')))

def search_series_api(title):
    search= tvdb.Search()
    ret = None 
    try:
        ret = search.series(title, language=ADDON.getSetting('language'))
    except:
        pass
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)
    return ret
    
def get_series_details_api(id, all=True):
    show = tvdb.Series(id, language=ADDON.getSetting('language'))
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
    return show

def get_cast(show):
    actors = []
    for actor in show.actors:
        if actor['image']:
            actors.append({'name': actor['name'], 'role': actor['role'], 'thumbnail': images_url+actor['image']})
        else:
            actors.append({'name': actor['name'], 'role': actor['role']})
    return actors

def get_series_episodes_api(id, language=None):
    ret = None
    if not language:
        language = ADDON.getSetting('language')
    showeps = tvdb.Series_Episodes(id, language=language)
    try:
        ret = showeps.all()
    except:
        pass
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)
    return ret

def get_episode_details_api(id, language=None):
    if not language:
        language = ADDON.getSetting('language')
    ep = tvdb.Episode(id, language=language)
    try:
        ep.info()
    except:
        return None
    ADDON.setSetting('token', tvdb.KEYS.API_TOKEN)
    return ep

# get the movie info via imdb
def get_imdb_info(id):
    votes = 0
    rating = 0
    r=requests.get('http://www.imdb.com/title/'+id+'/ratings')
    if r.status_code == 200:
        res =re.search(r'<p>(\d+).*?title\?user_rating\=.*?\">(.*?)</a>', r.text)
        if (res):
            votes = int(res.group(1).replace(',',''))
            rating = float(res.group(2))
    return {'votes':votes,'rating':rating}

# add the found shows to the list
def search_series(title, year=None):
    log('Find tvshow with title {title}'.format(title=title))
    shows = search_series_api(title)
    if not shows:
        return
    for show in shows:
        if show['banner']:
            liz=xbmcgui.ListItem(show['seriesName'], thumbnailImage=images_url+show['banner'], offscreen=True)
        else:
            liz=xbmcgui.ListItem(show['seriesName'], offscreen=True)
        #liz.setProperty('relevance', '0.5')
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=str(show['id']), listitem=liz, isFolder=True)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

# get the details of the found series
def get_series_details(id):
    log('Find info of tvshow with id {id}'.format(id=id))
    show = get_series_details_api(id)
    if not show:
        return
    liz=xbmcgui.ListItem(show.seriesName, offscreen=True)
    liz.setInfo('video',
                {'title': show.seriesName,
                 'plot': show.overview,
                 'duration': int(show.runtime) * 60,
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
        liz.setUniqueIDs({ 'tvdb': show.id, 'imdb' : show.imdbId }, 'tvdb')
        imdb_info = get_imdb_info(show.imdbId)
        if imdb_info['votes']>0:
            liz.setRating("imdb", imdb_info['rating'], imdb_info['votes'], isimdbdef)
    else:
        liz.setUniqueIDs({ 'tvdb': show.id }, 'tvdb')

    liz.setCast(get_cast(show))
    add_artworks(show, liz)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

def add_artworks(show, liz):
    for poster in show.Images.poster:
        liz.addAvailableArtwork(images_url+poster['fileName'], 'poster')
    for banner in show.Images.series:
        liz.addAvailableArtwork(images_url+banner['fileName'], 'banner')
    for season in show.Images.season:
        liz.addAvailableArtwork(images_url+season['fileName'], 'poster', season=int(season['subKey']))
    for seasonwide in show.Images.seasonwide:
        liz.addAvailableArtwork(images_url+seasonwide['fileName'], 'banner', season=int(seasonwide['subKey']))
    fanarts = []
    for fanart in show.Images.fanart:
        fanarts.append({'image': images_url+fanart['fileName'], 'preview': images_url+fanart['thumbnail']})
    if fanarts:
        liz.setAvailableFanart(fanarts)

def get_artworks(id):
    show = get_series_details_api(id, False)
    if not show:
        return
    liz=xbmcgui.ListItem(id, offscreen=True)
    add_artworks(show, liz)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

# add the episodes of a series to the list
def get_series_episodes(id):
    log('Find episodes of tvshow with id {id}'.format(id=id))
    episodes = get_series_episodes_api(id)
    if not episodes:
        return
    for ep in episodes:
        liz=xbmcgui.ListItem(ep['episodeName'], offscreen=True)
        details = {'title': ep['episodeName'], 
                   'aired': ep['firstAired']
                  }
        if (ADDON.getSetting('absolutenumber') == 'true'):
            details['season'] = 1
            details['episode'] = ep['absoluteNumber']
        elif (ADDON.getSetting('dvdorder') == 'true'):
            details['season'] = ep['dvdSeason']
            details['episode'] = ep['dvdEpisodeNumber']
        else:
            details['season'] = ep['airedSeason']
            details['episode'] = ep['airedEpisodeNumber']
        liz.setInfo('video', details)
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=str(ep['id']), listitem=liz, isFolder=True)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

# get the details of the found episode
def get_episode_details(id):
    log('Find info of episode with id {id}'.format(id=id))
    ep = get_episode_details_api(id)
    if not ep:
        return
    liz=xbmcgui.ListItem(ep.episodeName, offscreen=True)
    details = {'title': ep.episodeName,
               'plot': ep.overview,
               'credits': ep.writers,
               'cast': ep.guestStars,
               'director': ep.directors,
               'premiered': ep.firstAired,
               'aired': ep.firstAired
              }
              
    if ep.airsAfterSeason >= 0:
        details['sortseason'] = 10000
        details['sortepisode'] = ep.airsAfterSeason
    elif ep.airsBeforeSeason >= 0:
        details['sortepisode'] = ep.airsBeforeSeason
        details['sortseason'] = ep.airsBeforeEpisode

    if (ADDON.getSetting('absolutenumber') == 'true'):
        details['season'] = 1
        details['episode'] = ep.absoluteNumber
    elif (ADDON.getSetting('dvdorder') == 'true'):
        details['season'] = ep.dvdSeason
        details['episode'] = ep.dvdEpisodeNumber
    else:
        details['season'] = ep.airedSeason
        details['episode'] = ep.airedEpisodeNumber

    liz.setInfo('video', details)

    isimdbdef = (ep.imdbId and ADDON.getSetting('RatingS') == 'IMDb')
    liz.setRating("tvdb", ep.siteRating, ep.siteRatingCount, not isimdbdef)
    if ep.imdbId:
        liz.setUniqueIDs({ 'tvdb': ep.id, 'imdb' : ep.imdbId }, 'tvdb')
        imdb_info = get_imdb_info(ep.imdbId)
        if imdb_info['votes']>0:
            liz.setRating("imdb", imdb_info['rating'], imdb_info['votes'], isimdbdef)
    else:
        liz.setUniqueIDs({ 'tvdb': ep.id }, 'tvdb')
    if ep.filename:
        liz.addAvailableArtwork(images_url+ep.filename)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

def run():
    params=get_params()
    if 'action' in params:
        action=urllib.parse.unquote_plus(params["action"])
        if action == 'find' and 'title' in params:
            search_series(urllib.parse.unquote_plus(params["title"]), params.get("year", None))
        elif action == 'getdetails' and 'url' in params:
            get_series_details(urllib.parse.unquote_plus(params["url"]))
        elif action == 'getepisodelist' and 'url' in params:
            get_series_episodes(urllib.parse.unquote_plus(params["url"]))
        elif action == 'getepisodedetails' and 'url' in params:
            get_episode_details(urllib.parse.unquote_plus(params["url"]))
        elif action == 'getartwork' and 'id' in params:
            get_artworks(urllib.parse.unquote_plus(params["id"]))
    xbmcplugin.endOfDirectory(HANDLE)
