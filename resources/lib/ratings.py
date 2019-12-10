import sys
import xbmcaddon
from .imdb_rating import get_imdb_rating_and_votes
from .utils import log
from .trakt_rating import get_trakt_rating_and_votes


ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])


def ratings(liz, item):

    imdb_is_default = _get_and_set_imdb_ratings(liz, item)

    trakt_is_default = _get_and_set_trakt_ratings(liz, item)

    liz.setRating("tvdb", item.siteRating,
                  item.siteRatingCount, not (imdb_is_default or trakt_is_default))


def _get_and_set_imdb_ratings(liz, item):
    got_imdb_rating = False
    is_imdb_def = False

    if item.imdbId:
        imdb_rating = get_imdb_rating_and_votes(item.imdbId)
        log("Imdb rating: {}".format(imdb_rating))
        if imdb_rating['votes'] > 0:
            got_imdb_rating = True
            is_imdb_def = (item.imdbId and ADDON.getSetting(
                'RatingS') == "1")  # IMDb
            log("is_imdb_def: {} {} {}".format(
                is_imdb_def, item.imdbId, ADDON.getSetting('RatingS')))
            liz.setRating(
                "imdb", imdb_rating['rating'], imdb_rating['votes'], is_imdb_def)

    return is_imdb_def and got_imdb_rating


def _get_and_set_trakt_ratings(liz, item):
    got_trakt_rating = False
    is_trakt_def = False

    trakt_rating = get_trakt_rating_and_votes(item.id)
    log("Trakt rating: {}".format(trakt_rating))
    if ('votes' in trakt_rating and trakt_rating['votes'] > 0) or trakt_rating['rating'] > 0:
        got_trakt_rating = True
        is_trakt_def = (ADDON.getSetting(
            'RatingS') == "2")  # Trakt
        log("is_trakt_def: {} {}".format(is_trakt_def,
                                         ADDON.getSetting('RatingS')))

        if trakt_rating['votes'] > 0:
            liz.setRating(
                "trakt", trakt_rating['rating'], trakt_rating['votes'], is_trakt_def)
        else:
            liz.setRating(
                "trakt", trakt_rating['rating'], defaultt=is_trakt_def)

    return is_trakt_def and got_trakt_rating