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
        
        download_torrent_task.delay(str(torrent.id))
        
        return JsonResponse({
            'success': True,
            'torrent_id': str(torrent.id),
            'message': 'Torrent added successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_torrent(request):
    try:
        if 'torrent_file' not in request.FILES:
            return JsonResponse({'error': 'No torrent file uploaded'}, status=400)
        
        torrent_file = request.FILES['torrent_file']
        
        torrent = TorrentDownload.objects.create(
            name=torrent_file.name.replace('.torrent', ''),
            torrent_file=torrent_file
        )
        
        download_torrent_task.delay(str(torrent.id))
        
        return JsonResponse({
            'success': True,
            'torrent_id': str(torrent.id),
            'message': 'Torrent file uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_torrent_status(request, torrent_id):
    try:
        torrent = get_object_or_404(TorrentDownload, id=torrent_id)
        return JsonResponse({
            'id': str(torrent.id),
            'name': torrent.name,
            'status': torrent.status,
            'progress': torrent.progress,
            'download_speed': torrent.download_speed,
            'upload_speed': torrent.upload_speed,
            'total_size': torrent.total_size,
            'downloaded_size': torrent.downloaded_size,
            'error_message': torrent.error_message,
            'download_url': torrent.get_download_url(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def download_file(request, torrent_id):
    try:
        torrent = get_object_or_404(TorrentDownload, id=torrent_id)
        
        if torrent.status != 'completed' or not torrent.download_path:
            raise Http404("File not ready for download")
        
        file_path = Path(torrent.download_path)
        
        if not file_path.exists():
            raise Http404("File not found")
        
        if file_path.is_dir():
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(file_path):
                        for file in files:
                            file_path_obj = Path(root) / file
                            arcname = file_path_obj.relative_to(file_path)
                            zipf.write(file_path_obj, arcname)
                
                with open(tmp_file.name, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="{torrent.name}.zip"'
                    
                os.unlink(tmp_file.name)
                return response
        else:
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
                return response
                
    except Exception as e:
        raise Http404(str(e))

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_torrent(request, torrent_id):
    try:
        torrent = get_object_or_404(TorrentDownload, id=torrent_id)
        
        if torrent.download_path and os.path.exists(torrent.download_path):
            if os.path.isdir(torrent.download_path):
                import shutil
                shutil.rmtree(torrent.download_path)
            else:
                os.remove(torrent.download_path)
        
        if torrent.torrent_file:
            torrent.torrent_file.delete()
        
        torrent.delete()
        
        return JsonResponse({'success': True, 'message': 'Torrent deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def list_torrents(request):
    torrents = TorrentDownload.objects.all()
    data = []
    for torrent in torrents:
        data.append({
            'id': str(torrent.id),
            'name': torrent.name,
            'status': torrent.status,
            'progress': torrent.progress,
            'download_speed': torrent.download_speed,
            'upload_speed': torrent.upload_speed,
            'total_size': torrent.total_size,
            'downloaded_size': torrent.downloaded_size,
            'created_at': torrent.created_at.isoformat(),
            'download_url': torrent.get_download_url(),
        })
    return JsonResponse({'torrents': data})