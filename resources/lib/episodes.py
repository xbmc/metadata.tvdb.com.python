
import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
from . import tvdb
from .utils import log
from .imdb_rating import get_imdb_rating_and_votes


ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])

# add the episodes of a series to the list


def get_series_episodes(id):
    log('Find episodes of tvshow with id {id}'.format(id=id))
    episodes = tvdb.get_series_episodes_api(id)
    if not episodes:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    for ep in episodes:
        liz = xbmcgui.ListItem(ep['episodeName'], offscreen=True)
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
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=str(
            ep['id']), listitem=liz, isFolder=True)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)

# get the details of the found episode


def get_episode_details(id, images_url: str):
    log('Find info of episode with id {id}'.format(id=id))
    ep = tvdb.get_episode_details_api(id)
    if not ep:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    liz = xbmcgui.ListItem(ep.episodeName, offscreen=True)
    details = {'title': ep.episodeName,
               'plot': ep.overview,
               'credits': ep.writers,
               'cast': ep.guestStars,
               'director': ep.directors,
               'premiered': ep.firstAired,
               'aired': ep.firstAired
               }

    if ep.airsAfterSeason and ep.airsAfterSeason >= 0:
        details['sortseason'] = 10000
        details['sortepisode'] = ep.airsAfterSeason
    elif ep.airsBeforeSeason and ep.airsBeforeSeason >= 0:
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
        liz.setUniqueIDs({'tvdb': ep.id, 'imdb': ep.imdbId}, 'tvdb')
        imdb_info = get_imdb_rating_and_votes(ep.imdbId)
        if imdb_info['votes'] > 0:
            liz.setRating(
                "imdb", imdb_info['rating'], imdb_info['votes'], isimdbdef)
    else:
        liz.setUniqueIDs({'tvdb': ep.id}, 'tvdb')
    if ep.filename:
        liz.addAvailableArtwork(images_url+ep.filename)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)
