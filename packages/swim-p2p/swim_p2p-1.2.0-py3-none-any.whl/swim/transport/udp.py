import socket
import asyncio
import logging
from typing import Tuple, Optional, Callable, Any, Dict

from .base import Transport

logger = logging.getLogger(__name__)

class UDPTransport(Transport):
    """UDP implementation of the Transport interface using asyncio."""
    
    def __init__(self, buffer_size: int = 65536):
        """Initialize a new UDP transport.
        
        Args:
            buffer_size: Maximum size of UDP packets to receive
                         65536 is the maximum UDP datagram size
        """
        self.buffer_size = buffer_size
        self.transport = None
        self.protocol = None
        self.local_address = None
        self.receive_queue = asyncio.Queue()
        self.running = False
        self.receiver_task = None
        
        # Create separate response queues for different message types
        # This helps ensure we don't mix up responses
        self._response_queues: Dict[str, asyncio.Queue] = {}
    
    async def bind(self, address: Tuple[str, int]) -> None:
        """Bind to a local address asynchronously.
        
        Args:
            address: (host, port) tuple to bind to
        """
        loop = asyncio.get_running_loop()
        
        # Create a protocol class that will handle incoming UDP packets
        class UDPProtocol(asyncio.DatagramProtocol):
            def __init__(self, parent):
                self.parent = parent  # Reference to the transport object
                self.transport = None
                
            def connection_made(self, transport):
                self.transport = transport
                logger.debug(f"UDP socket connection established")
                
            def datagram_received(self, data, addr):
                try:
                    # Try to parse the message to determine its type
                    from swim.utils.serialization import deserialize_message
                    msg = deserialize_message(data)
                    
                    # Check if it's a response to a specific message type
                    msg_type = msg.get("type", "UNKNOWN")
                    msg_id = msg.get("id", "unknown")
                    
                    # Log message details
                    addr_str = f"{addr[0]}:{addr[1]}"
                    logger.debug(f"[{msg_id}] RECEIVED {len(data)} bytes from {addr_str}, type={msg_type}")
                    
                    # Put the message in the general queue
                    self.parent.receive_queue.put_nowait((data, addr))
                    
                    # If it's a specific type we're interested in, also put it in the 
                    # type-specific queue to avoid mixing messages
                    if msg_type in self.parent._response_queues:
                        self.parent._response_queues[msg_type].put_nowait((data, addr))
                        logger.debug(f"[{msg_id}] Added {msg_type} to type-specific queue")
                        
                except Exception as e:
                    # If we can't parse, just put it in the general queue
                    logger.debug(f"Error parsing message: {e}, adding to general queue")
                    self.parent.receive_queue.put_nowait((data, addr))
        
        # Create socket with appropriate options
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # On some platforms, SO_REUSEPORT may not be available
        if hasattr(socket, 'SO_REUSEPORT'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
        # Enable broadcast (important for some SWIM implementations)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Increase buffer sizes 
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024)  # 1MB receive buffer
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # 1MB send buffer
        
        # Modify the binding address - use 0.0.0.0 instead of 127.0.0.1
        # This ensures we listen on all interfaces while keeping the same port
        bind_addr = ('0.0.0.0', address[1])
        sock.bind(bind_addr)
        
        # Create the datagram endpoint using the pre-configured socket
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self),
            sock=sock
        )
        
        # Store the original address for identification
        self.local_address = address
        logger.info(f"UDP transport bound to all interfaces (0.0.0.0:{address[1]}), " 
                   f"identifying as {address[0]}:{address[1]}")
                   
        # Create specific response queues for different message types
        for msg_type in ["PONG", "PING-REQ-ACK", "HEARTBEAT"]:
            self._response_queues[msg_type] = asyncio.Queue()
            logger.debug(f"Created message queue for {msg_type} messages")
            
    async def send(self, data: bytes, dest: Tuple[str, int]) -> None:
        """Send data to a destination asynchronously.
        
        Args:
            data: Bytes to send
            dest: (host, port) destination
        """
        if not self.transport:
            raise RuntimeError("Transport not initialized. Call bind() first.")
            
        try:
            self.transport.sendto(data, dest)
            
            # Try to extract message ID and type for better logging
            try:
                from swim.utils.serialization import deserialize_message
                msg = deserialize_message(data)
                msg_type = msg.get("type", "UNKNOWN")
                msg_id = msg.get("id", "unknown")
                logger.debug(f"[{msg_id}] SENT {len(data)} bytes to {dest[0]}:{dest[1]}, type={msg_type}")
            except:
                logger.debug(f"SENT {len(data)} bytes to {dest[0]}:{dest[1]}")
                
        except Exception as e:
            logger.error(f"Failed to send data to {dest}: {e}")
            raise
    
    async def receive(self, timeout: Optional[float] = None, msg_type: Optional[str] = None) -> Tuple[bytes, Tuple[str, int]]:
        """Receive data from the socket asynchronously.
        
        Args:
            timeout: Max seconds to wait (None = wait forever)
            msg_type: Optional message type to listen for specifically
            
        Returns:
            Tuple of (data_bytes, sender_address)
            
        Raises:
            asyncio.TimeoutError: If the operation times out
        """
        if not self.transport:
            raise RuntimeError("Transport not initialized. Call bind() first.")
        
        try:
            # Use the type-specific queue if requested and available
            queue = self._response_queues.get(msg_type, self.receive_queue) if msg_type else self.receive_queue
            
            if msg_type:
                logger.debug(f"Waiting for specific message type: {msg_type} with timeout {timeout}s")
            
            if timeout is not None:
                # Use asyncio timeout
                start_time = asyncio.get_event_loop().time()
                result = await asyncio.wait_for(queue.get(), timeout)
                elapsed = asyncio.get_event_loop().time() - start_time
                
                # Try to extract message details for better logging
                try:
                    from swim.utils.serialization import deserialize_message
                    data, addr = result
                    msg = deserialize_message(data)
                    msg_id = msg.get("id", "unknown")
                    logger.debug(f"[{msg_id}] Received response after {elapsed:.4f}s "
                               f"from {addr[0]}:{addr[1]}, type={msg.get('type', 'UNKNOWN')}")
                except:
                    pass
                
                return result
            else:
                # Wait indefinitely
                return await queue.get()
        except asyncio.TimeoutError:
            logger.debug(f"Socket receive timed out{f' for {msg_type}' if msg_type else ''}")
            raise
    
    async def start_receiver(self, callback: Callable[[bytes, Tuple[str, int]], Any]) -> None:
        """Start an async task to process received messages.
        
        Args:
            callback: Function to call with (data, sender_address) on receipt
        """
        if self.running:
            return
        
        self.running = True
        
        async def receiver_loop():
            while self.running:
                try:
                    data, addr = await self.receive()
                    # Execute callback - if it's a coroutine, await it
                    result = callback(data, addr)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    if self.running:  # Only log if we're supposed to be running
                        logger.error(f"Error in receiver loop: {e}")
        
        self.receiver_task = asyncio.create_task(receiver_loop())
        logger.info("UDP receiver task started")
    
    async def close(self) -> None:
        """Close the transport and stop the receiver task."""
        self.running = False
        
        if self.receiver_task:
            try:
                self.receiver_task.cancel()
                await asyncio.gather(self.receiver_task, return_exceptions=True)
            except:
                pass
            
        if self.transport:
            self.transport.close()
            self.transport = None
            
        logger.info("UDP transport closed")