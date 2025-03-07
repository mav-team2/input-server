import asyncio
import json
import logging

import websockets
from fastapi import WebSocket

from src.api.clients.ComfyUI.client import ComfyClient


class ComfyAPI:
    """
    Asynchronous high-level client that wraps AsyncComfyClient to handle serialization
    and asynchronous WebSocket communications. It provides an async generator that yields
    progress updates from the ComfyUI server.
    """
    def __init__(self, client: ComfyClient, ws_timeout: int = 60):
        """
        Initialize the AsyncComfyAPI with a AsyncComfyClient instance and the WebSocket URL.

        Args:
            client (AsyncComfyClient): An instance of the low-level AsyncComfyClient.
            ws (WebSocket): fastapi WebSocket instance for real-time communication.
            ws_timeout (int): Maximum time in seconds to wait for a progress update.
        """
        self.client = client
        # ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
        self.ws = websockets.WebSocket()
        self.ws.connect()
        self.ws_timeout = ws_timeout

    async def stream_progress(self):
        """
        Asynchronous generator that yields progress messages received via WebSocket.

        Yields:
            str: Raw message received from the WebSocket server.
        """
        try:
            # Connect to the WebSocket server asynchronously
            async with self.ws.connect(self.ws_url) as websocket:
                while True:
                    try:
                        # Wait for a message with a timeout
                        message = await asyncio.wait_for(websocket.recv(), timeout=self.ws_timeout)
                        logging.info(f"Received WebSocket message: {message}")
                        yield message
                        # Check if the message indicates completion.
                        try:
                            data = json.loads(message)
                            if data.get("status") == "completed":
                                logging.info("Received completion status from WebSocket")
                                break
                        except json.JSONDecodeError:
                            pass  # If message is not JSON, continue streaming.
                    except asyncio.TimeoutError:
                        logging.warning("WebSocket stream timed out")
                        break
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            yield json.dumps({"error": str(e)})

    async def generate_image_with_progress(self, prompt: str, params: dict = None):
        """
        High-level method to generate an image while streaming progress updates.
        It calls the low-level generate_image API and then yields updates from the WebSocket.

        Args:
            prompt (str): The text prompt for image generation.
            params (dict): Additional image generation parameters.

        Yields:
            str or dict: Progress updates from the WebSocket and finally the job result.
        """
        # Initiate image generation and get the job ID.
        response = await self.client.generate_image(prompt, params)
        job_id = response.get("job_id")
        if not job_id:
            raise ValueError("No job_id returned from generate_image API call")
        logging.info(f"Image generation started with job_id: {job_id}")

        # Stream progress updates via the WebSocket.
        async for message in self.stream_progress():
            yield message
            try:
                data = json.loads(message)
                # Break if the progress update indicates job completion.
                if data.get("job_id") == job_id and data.get("status") == "completed":
                    logging.info("Image generation completed as per progress update")
                    break
            except json.JSONDecodeError:
                continue

        # Retrieve and yield the final job result.
        final_result = await self.client.get_job_result(job_id)
        yield final_result