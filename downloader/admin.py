from django.contrib import admin
from .models import TorrentDownload

@admin.register(TorrentDownload)
class TorrentDownloadAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'progress', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'completed_at']