"""
OMNITECH OMEGA v3.0 - WebSocket Real-time Stream Server
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Set
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.policy import UCB1Policy
except ImportError:
    UCB1Policy = None


class StreamServer:
    """WebSocket server for real-time streaming of RL metrics."""
    
    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set = set()
        self.policy = None
        
        if UCB1Policy:
            try:
                self.policy = UCB1Policy()
            except Exception as e:
                print(f"Warning: Could not initialize policy: {e}")
    
    async def register(self, websocket):
        """Register a new client connection."""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send initial state
        if self.policy:
            await websocket.send(json.dumps({
                'type': 'initial_state',
                'data': self.policy.get_stats(),
                'timestamp': datetime.now().isoformat()
            }))
    
    async def unregister(self, websocket):
        """Unregister a client connection."""
        self.clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def handler(self, websocket, path):
        """Handle WebSocket connections."""
        await self.register(websocket)
        
        try:
            async for message in websocket:
                # Handle incoming messages (if any)
                data = json.loads(message)
                if data.get('type') == 'ping':
                    await websocket.send(json.dumps({
                        'type': 'pong',
                        'timestamp': datetime.now().isoformat()
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)
    
    async def periodic_update(self, interval: float = 2.0):
        """Periodically send updates to all clients."""
        while True:
            if self.policy:
                stats = self.policy.get_stats()
                message = json.dumps({
                    'type': 'update',
                    'data': stats,
                    'timestamp': datetime.now().isoformat()
                })
                await self.broadcast(message)
            
            await asyncio.sleep(interval)
    
    async def run(self):
        """Run the WebSocket server."""
        print(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        
        # Start server
        server = await websockets.serve(self.handler, self.host, self.port)
        
        # Start periodic updates
        asyncio.create_task(self.periodic_update())
        
        # Run forever
        await asyncio.Future()


async def main():
    """Main entry point."""
    server = StreamServer(host='0.0.0.0', port=8765)
    await server.run()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down WebSocket server...")
