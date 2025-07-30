from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-torrent/', views.add_torrent, name='add_torrent'),
    path('upload-torrent/', views.upload_torrent, name='upload_torrent'),
    path('status/<uuid:torrent_id>/', views.get_torrent_status, name='get_torrent_status'),
    path('download/<uuid:torrent_id>/', views.download_file, name='download_file'),
    path('delete/<uuid:torrent_id>/', views.delete_torrent, name='delete_torrent'),
    path('list/', views.list_torrents, name='list_torrents'),
]