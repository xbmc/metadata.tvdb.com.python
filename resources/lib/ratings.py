import sys
import xbmcaddon
from .imdb_rating import get_imdb_rating_and_votes
from .utils import log


ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])


def ratings_episode(liz, ep):
    got_imdb_rating = False
    if ep.imdbId:
        imdb_rating = get_imdb_rating_and_votes(ep.imdbId)
        log("Imdb rating: {}".format(imdb_rating))
        if imdb_rating['votes'] > 0:
            got_imdb_rating = True
            is_imdb_def = (ep.imdbId and ADDON.getSetting(
                'RatingS') == 1)  # IMDb
            log("is_imdb_def: {} {} {}".format(
                is_imdb_def, ep.imdbId, ADDON.getSetting('RatingS')))
            liz.setRating(
                "imdb", imdb_rating['rating'], imdb_rating['votes'], is_imdb_def)

    liz.setRating("tvdb", ep.siteRating, ep.siteRatingCount,
                  not (is_imdb_def and got_imdb_rating))


def ratings_series(liz, show):
    got_imdb_rating = False
    if show.imdbId:
        imdb_rating = get_imdb_rating_and_votes(show.imdbId)
        log("Imdb rating: {}".format(imdb_rating))
        if imdb_rating['votes'] > 0:
            got_imdb_rating = True
            is_imdb_def = (show.imdbId and ADDON.getSetting(
                'RatingS') == 1)  # IMDb
            log("is_imdb_def: {} {} {}".format(is_imdb_def,
                                               show.imdbId, ADDON.getSetting('RatingS')))
            liz.setRating(
                "imdb", imdb_rating['rating'], imdb_rating['votes'], is_imdb_def)

    liz.setRating("tvdb", show.siteRating,
                  show.siteRatingCount, not (is_imdb_def and got_imdb_rating))
