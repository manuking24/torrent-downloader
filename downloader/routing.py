from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/torrent/<uuid:torrent_id>/', consumers.TorrentProgressConsumer.as_asgi()),
]