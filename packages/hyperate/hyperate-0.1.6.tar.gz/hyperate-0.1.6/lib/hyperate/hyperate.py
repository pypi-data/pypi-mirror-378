import asyncio
import websockets
import json
import re
from typing import Callable, Optional

class HypeRate:
    def __init__(self, api_token: str, base_url: str = "wss://app.hyperate.io/socket/websocket"):
        self.api_token = api_token.strip()
        self.base_url = base_url
        self.ws = None
        self.connected = False
        self._event_handlers = {
            'connected': [],
            'disconnected': [],
            'heartbeat': [],
            'clip': [],
            'channel_joined': [],
            'channel_left': [],
        }
        self._receive_task = None
        self._heartbeat_task = None
        self._loop = asyncio.get_event_loop()

    def on(self, event: str, handler: Callable):
        if event in self._event_handlers:
            self._event_handlers[event].append(handler)

    async def connect(self):
        url = f"{self.base_url}?token={self.api_token}"
        self.ws = await websockets.connect(url)
        self.connected = True
        self._fire_event('connected')
        self._receive_task = self._loop.create_task(self._receive())
        self._heartbeat_task = self._loop.create_task(self._heartbeat())

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        self.connected = False
        self._fire_event('disconnected')

    async def _heartbeat(self):
        while self.connected:
            await self.send_packet({"topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": 0})
            await asyncio.sleep(10)

    async def _receive(self):
        try:
            async for message in self.ws:
                self._handle_message(message)
        except Exception:
            self.connected = False
            self._fire_event('disconnected')

    def _handle_message(self, message):
        try:
            data = json.loads(message)
            topic = data.get("topic", "")
            if topic.startswith("hr:"):
                payload = data.get("payload", {})
                hr = payload.get("hr")
                if hr is not None:
                    self._fire_event('heartbeat', payload)
            elif topic.startswith("clips:"):
                payload = data.get("payload", {})
                slug = payload.get("twitch_slug")
                if slug:
                    self._fire_event('clip', payload)
        except Exception:
            pass

    async def send_packet(self, packet):
        if self.ws:
            await self.ws.send(json.dumps(packet))

    async def join_heartbeat_channel(self, device_id: str):
        await self.join_channel(f"hr:{device_id}")

    async def leave_heartbeat_channel(self, device_id: str):
        await self.leave_channel(f"hr:{device_id}")

    async def join_clips_channel(self, device_id: str):
        await self.join_channel(f"clips:{device_id}")

    async def leave_clips_channel(self, device_id: str):
        await self.leave_channel(f"clips:{device_id}")

    async def join_channel(self, channel_name: str):
        packet = {"topic": channel_name, "event": "phx_join", "payload": {}, "ref": 1}
        await self.send_packet(packet)
        self._fire_event('channel_joined', channel_name)

    async def leave_channel(self, channel_name: str):
        packet = {"topic": channel_name, "event": "phx_leave", "payload": {}, "ref": 2}
        await self.send_packet(packet)
        self._fire_event('channel_left', channel_name)

    def _fire_event(self, event, *args):
        for handler in self._event_handlers.get(event, []):
            handler(*args)

# Device utility functions
class Device:
    VALID_ID_REGEX = re.compile(r'^[a-zA-Z0-9]{3,8}$')

    @staticmethod
    def is_valid_device_id(device_id: str) -> bool:
        if device_id == "internal-testing":
            return True
        return bool(Device.VALID_ID_REGEX.match(device_id))

    @staticmethod
    def extract_device_id(input_str: str) -> Optional[str]:
        match = re.search(r'((https?:\/\/)?app\.hyperate\.io\/)?(?P<device_id>[a-zA-Z0-9\-]+)(\?.*)?', input_str)
        if match:
            return match.group("device_id")
        return None
