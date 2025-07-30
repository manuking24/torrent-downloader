from channels.generic.websocket import AsyncWebsocketConsumer
import json

class TorrentProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.torrent_id = self.scope['url_route']['kwargs']['torrent_id']
        self.group_name = f'torrent_{self.torrent_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def torrent_progress(self, event):
        await self.send(text_data=json.dumps({
            'type': 'progress',
            'progress': event['progress'],
            'download_speed': event['download_speed'],
            'upload_speed': event['upload_speed'],
        }))
    
    async def torrent_completed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'completed',
            'message': event['message']
        }))