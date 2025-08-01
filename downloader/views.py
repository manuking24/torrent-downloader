from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import TorrentDownload
from .tasks import download_torrent_task
import json
import os
import zipfile
import tempfile
from pathlib import Path
import traceback
import logging

logger = logging.getLogger(__name__)
def index(request):
    torrents = TorrentDownload.objects.all()
    return render(request, 'downloader/index.html', {'torrents': torrents})
@csrf_exempt
@require_http_methods(["POST"])
def add_torrent(request):
    try:
        data = json.loads(request.body)
        magnet_link = data.get('magnet_link', '').strip()
        
        if not magnet_link:
            return JsonResponse({'error': 'Magnet link is required'}, status=400)
        
        torrent = TorrentDownload.objects.create(
            name=f"Torrent {TorrentDownload.objects.count() + 1}",
            magnet_link=magnet_link
        )
        
        # Comment out Celery task to isolate error:
        # download_torrent_task.delay(str(torrent.id))
        
        return JsonResponse({
            'success': True,
            'torrent_id': str(torrent.id),
            'message': 'Torrent added successfully'
        })
        
    except Exception as e:
        logger.error(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)