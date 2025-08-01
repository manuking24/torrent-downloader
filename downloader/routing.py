from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/torrent/(?P<torrent_id>[0-9a-f-]+)/$', consumers.TorrentProgressConsumer.as_asgi()),
]
