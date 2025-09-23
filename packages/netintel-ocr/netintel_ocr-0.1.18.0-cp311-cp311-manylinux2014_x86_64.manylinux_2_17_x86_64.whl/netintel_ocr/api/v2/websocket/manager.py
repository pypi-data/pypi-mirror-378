"""
WebSocket Connection Manager for Real-time Updates
"""

from typing import Dict, Set, Optional, Any, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""

    # Connection messages
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PING = "ping"
    PONG = "pong"

    # Processing messages
    PROCESSING_STATUS = "processing_status"
    PROCESSING_PROGRESS = "processing_progress"
    PROCESSING_COMPLETE = "processing_complete"
    PROCESSING_ERROR = "processing_error"

    # Upload messages
    UPLOAD_PROGRESS = "upload_progress"
    UPLOAD_COMPLETE = "upload_complete"

    # Search messages
    SEARCH_STARTED = "search_started"
    SEARCH_RESULT = "search_result"
    SEARCH_COMPLETE = "search_complete"

    # Notification messages
    NOTIFICATION = "notification"
    ERROR = "error"


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}

        # Subscriptions by topic
        self.subscriptions: Dict[str, Set[str]] = {}

        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

        # Message queue for offline clients
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {}

        # Background tasks
        self.background_tasks: Set[asyncio.Task] = set()

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Accept a new WebSocket connection"""

        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = metadata or {}
            self.connection_metadata[client_id]["connected_at"] = datetime.utcnow().isoformat()

            # Send connection confirmation
            await self.send_personal_message(
                client_id,
                {
                    "type": MessageType.CONNECTED,
                    "client_id": client_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Connected successfully",
                },
            )

            # Send any queued messages
            await self._send_queued_messages(client_id)

            logger.info(f"Client {client_id} connected")
            return True

        except Exception as e:
            logger.error(f"Failed to connect client {client_id}: {str(e)}")
            return False

    def disconnect(self, client_id: str):
        """Disconnect a client"""

        if client_id in self.active_connections:
            del self.active_connections[client_id]

        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]

        # Remove from all subscriptions
        for topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)

        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(
        self,
        client_id: str,
        message: Dict[str, Any],
    ) -> bool:
        """Send a message to a specific client"""

        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {str(e)}")
                self.disconnect(client_id)
                # Queue the message for later delivery
                self._queue_message(client_id, message)
                return False
        else:
            # Queue the message for later delivery
            self._queue_message(client_id, message)
            return False

    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude: Optional[Set[str]] = None,
    ):
        """Broadcast a message to all connected clients"""

        exclude = exclude or set()
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            if client_id not in exclude:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast to {client_id}: {str(e)}")
                    disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

    async def send_to_topic(
        self,
        topic: str,
        message: Dict[str, Any],
    ):
        """Send a message to all clients subscribed to a topic"""

        if topic not in self.subscriptions:
            return

        disconnected = []
        for client_id in self.subscriptions[topic]:
            if not await self.send_personal_message(client_id, message):
                disconnected.append(client_id)

        # Remove disconnected clients from subscription
        for client_id in disconnected:
            self.subscriptions[topic].discard(client_id)

    def subscribe(self, client_id: str, topic: str) -> bool:
        """Subscribe a client to a topic"""

        if client_id not in self.active_connections:
            return False

        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()

        self.subscriptions[topic].add(client_id)
        logger.info(f"Client {client_id} subscribed to {topic}")
        return True

    def unsubscribe(self, client_id: str, topic: str) -> bool:
        """Unsubscribe a client from a topic"""

        if topic in self.subscriptions:
            self.subscriptions[topic].discard(client_id)
            logger.info(f"Client {client_id} unsubscribed from {topic}")
            return True
        return False

    def get_subscriptions(self, client_id: str) -> List[str]:
        """Get all subscriptions for a client"""

        subscriptions = []
        for topic, clients in self.subscriptions.items():
            if client_id in clients:
                subscriptions.append(topic)
        return subscriptions

    def _queue_message(self, client_id: str, message: Dict[str, Any]):
        """Queue a message for offline delivery"""

        if client_id not in self.message_queue:
            self.message_queue[client_id] = []

        # Limit queue size to prevent memory issues
        if len(self.message_queue[client_id]) < 100:
            self.message_queue[client_id].append(message)

    async def _send_queued_messages(self, client_id: str):
        """Send queued messages to a reconnected client"""

        if client_id in self.message_queue:
            messages = self.message_queue[client_id]
            del self.message_queue[client_id]

            for message in messages:
                await self.send_personal_message(client_id, message)

    async def handle_message(
        self,
        client_id: str,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle incoming WebSocket message"""

        message_type = message.get("type")

        if message_type == MessageType.PING:
            return {"type": MessageType.PONG, "timestamp": datetime.utcnow().isoformat()}

        elif message_type == "subscribe":
            topic = message.get("topic")
            if topic and self.subscribe(client_id, topic):
                return {
                    "type": "subscribed",
                    "topic": topic,
                    "message": f"Subscribed to {topic}",
                }

        elif message_type == "unsubscribe":
            topic = message.get("topic")
            if topic and self.unsubscribe(client_id, topic):
                return {
                    "type": "unsubscribed",
                    "topic": topic,
                    "message": f"Unsubscribed from {topic}",
                }

        return {
            "type": "error",
            "message": f"Unknown message type: {message_type}",
        }

    async def start_ping_task(self, interval: int = 30):
        """Start background ping task to keep connections alive"""

        async def ping_clients():
            while True:
                await asyncio.sleep(interval)
                await self.broadcast(
                    {
                        "type": MessageType.PING,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        task = asyncio.create_task(ping_clients())
        self.background_tasks.add(task)

    async def cleanup(self):
        """Clean up resources"""

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Close all connections
        for client_id in list(self.active_connections.keys()):
            self.disconnect(client_id)

    # Processing status notifications

    async def notify_processing_status(
        self,
        document_id: str,
        status: str,
        progress: Optional[int] = None,
        current_page: Optional[int] = None,
        total_pages: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Notify about document processing status"""

        message = {
            "type": MessageType.PROCESSING_STATUS,
            "document_id": document_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if progress is not None:
            message["progress"] = progress
        if current_page is not None:
            message["current_page"] = current_page
        if total_pages is not None:
            message["total_pages"] = total_pages
        if metadata:
            message["metadata"] = metadata

        await self.send_to_topic(f"document:{document_id}", message)

    async def notify_processing_complete(
        self,
        document_id: str,
        success: bool,
        results: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        """Notify when processing is complete"""

        message = {
            "type": MessageType.PROCESSING_COMPLETE if success else MessageType.PROCESSING_ERROR,
            "document_id": document_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if results:
            message["results"] = results
        if error:
            message["error"] = error

        await self.send_to_topic(f"document:{document_id}", message)

    # Upload progress notifications

    async def notify_upload_progress(
        self,
        upload_id: str,
        chunks_received: int,
        chunks_total: int,
        bytes_received: int,
        bytes_total: int,
    ):
        """Notify about upload progress"""

        message = {
            "type": MessageType.UPLOAD_PROGRESS,
            "upload_id": upload_id,
            "chunks_received": chunks_received,
            "chunks_total": chunks_total,
            "bytes_received": bytes_received,
            "bytes_total": bytes_total,
            "progress": int((bytes_received / bytes_total) * 100) if bytes_total > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.send_to_topic(f"upload:{upload_id}", message)

    async def notify_upload_complete(
        self,
        upload_id: str,
        document_id: str,
        success: bool,
        error: Optional[str] = None,
    ):
        """Notify when upload is complete"""

        message = {
            "type": MessageType.UPLOAD_COMPLETE,
            "upload_id": upload_id,
            "document_id": document_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if error:
            message["error"] = error

        await self.send_to_topic(f"upload:{upload_id}", message)


# Global connection manager instance
ws_manager = ConnectionManager()