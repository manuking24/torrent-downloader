from django.db import models
import uuid
import os

class TorrentDownload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('downloading', 'Downloading'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('paused', 'Paused'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    magnet_link = models.TextField(blank=True, null=True)
    torrent_file = models.FileField(upload_to='torrents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0.0)
    download_speed = models.FloatField(default=0.0)  # KB/s
    upload_speed = models.FloatField(default=0.0)  # KB/s
    total_size = models.BigIntegerField(default=0)  # bytes
    downloaded_size = models.BigIntegerField(default=0)  # bytes
    error_message = models.TextField(blank=True, null=True)
    download_path = models.CharField(max_length=512, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_download_url(self):
        if self.status == 'completed' and self.download_path:
            return f'/download/{self.id}/'
        return None