#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import xbmcgui
import xbmcplugin
from . import tvdb
HANDLE = int(sys.argv[1])


def add_artworks(show, liz, images_url: str):
    for poster in show.Images.poster:
        liz.addAvailableArtwork(images_url+poster['fileName'], 'poster')
    for banner in show.Images.series:
        liz.addAvailableArtwork(images_url+banner['fileName'], 'banner')
    for season in show.Images.season:
        liz.addAvailableArtwork(
            images_url+season['fileName'], 'poster', season=int(season['subKey']))
    for seasonwide in show.Images.seasonwide:
        liz.addAvailableArtwork(
            images_url+seasonwide['fileName'], 'banner', season=int(seasonwide['subKey']))
    fanarts = []
    for fanart in show.Images.fanart:
        fanarts.append(
            {'image': images_url+fanart['fileName'], 'preview': images_url+fanart['thumbnail']})
    if fanarts:
        liz.setAvailableFanart(fanarts)


def get_artworks(id, images_url: str):
    show = tvdb.get_series_details_api(id, False)
    if not show:
        xbmcplugin.setResolvedUrl(
            HANDLE, False, xbmcgui.ListItem(offscreen=True))
        return
    liz = xbmcgui.ListItem(id, offscreen=True)
    add_artworks(show, liz, images_url)
    xbmcplugin.setResolvedUrl(handle=HANDLE, succeeded=True, listitem=liz)
