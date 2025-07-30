from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import TorrentDownload
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import random
import threading
from pathlib import Path

@shared_task
def download_torrent_task(torrent_id):
    """Simulate torrent download (replace with real torrent client)"""
    try:
        torrent = TorrentDownload.objects.get(id=torrent_id)
        torrent.status = 'downloading'
        torrent.total_size = random.randint(100*1024*1024, 1024*1024*1024)  # 100MB - 1GB
        torrent.save()
        
        # Update torrent name if needed
        if torrent.name.startswith('Torrent '):
            torrent.name = f"Sample Download {random.randint(1, 1000)}"
            torrent.save()
        
        channel_layer = get_channel_layer()
        
        # Simulate download progress
        for progress in range(0, 101, 5):
            if torrent.status != 'downloading':
                torrent.refresh_from_db()
                if torrent.status != 'downloading':
                    break
            
            torrent.progress = progress
            torrent.downloaded_size = int((progress / 100) * torrent.total_size)
            torrent.download_speed = random.randint(500, 5000)  # KB/s
            torrent.upload_speed = random.randint(50, 500)  # KB/s
            torrent.save()
            
            # Send progress update via WebSocket
            async_to_sync(channel_layer.group_send)(
                f'torrent_{torrent_id}',
                {
                    'type': 'torrent_progress',
                    'progress': torrent.progress,
                    'download_speed': torrent.download_speed,
                    'upload_speed': torrent.upload_speed,
                }
            )
            
            time.sleep(2)  # Simulate time
        
        # Create demo file
        download_path = settings.DOWNLOAD_DIR / f"{torrent.name}.txt"
        download_path.write_text(f"This is a demo file for {torrent.name}\nDownloaded at: {timezone.now()}")
        
        # Complete download
        torrent.status = 'completed'
        torrent.progress = 100.0
        torrent.download_path = str(download_path)
        torrent.completed_at = timezone.now()
        torrent.save()
        
        # Send completion notification
        async_to_sync(channel_layer.group_send)(
            f'torrent_{torrent_id}',
            {
                'type': 'torrent_completed',
                'message': 'Download completed successfully'
            }
        )
        
    except Exception as e:
        try:
            torrent = TorrentDownload.objects.get(id=torrent_id)
            torrent.status = 'error'
            torrent.error_message = str(e)
            torrent.save()
        except:
            pass