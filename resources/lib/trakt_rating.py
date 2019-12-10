from trakt import Trakt
from trakt.objects import Show


def get_trakt_rating_and_votes(tvdb_id):
    __client_id = "5f2dc73b6b11c2ac212f5d8b4ec8f3dc4b727bb3f026cd254d89eda997fe64ae"
    __client_secret = "7b9ce1836d6f5c60fc78809d5455afaeb33236d86545ec860e814d3d4aae7b5c"
    # Configure
    Trakt.configuration.defaults.client(
        id=__client_id,
        secret=__client_secret
    )

    with Trakt.configuration.http(retry=True):
        item_info = Trakt['search'].lookup(tvdb_id, 'tvdb', extended='full')
        result = {}
        if(item_info is not None):
            if item_info.rating is not None:
                result = {'votes': int(
                    item_info.rating.votes), 'rating': float(item_info.rating.value)}

        return result
