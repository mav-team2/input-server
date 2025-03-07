import json

import httpx
import logging

logger = logging.getLogger(__name__)

class ComfyClient:
    """
    Asynchronous low-level client to interact with the ComfyUI API.
    Uses httpx.AsyncClient for making non-blocking HTTP requests.
    """
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the AsyncComfyClient with the base URL of the ComfyUI server.

        Args:
            base_url (str): Base URL of the ComfyUI server (e.g., "http://localhost:8188")
            timeout (int): HTTP request timeout in seconds.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def queue_prompt(self, prompt, client_id=None):
        """
        Queues a prompt for processing by the ComfyUI server.

        Args:
            prompt: The prompt data to be processed
            client_id: Optional client identifier

        Returns:
            dict: The JSON response from the ComfyUI server
        """
        data = {"prompt": prompt}
        if client_id:
            data["client_id"] = client_id

        try:
            url = self.base_url + '/prompt'
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Received response: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in queue_prompt: {e}")
            raise

    async def generate_image(self, prompt: str, params: dict = None) -> dict:
        """
        Sends a request to generate an image based on the provided prompt.

        Args:
            prompt (str): The text prompt for image generation.
            params (dict): Additional image generation parameters.

        Returns:
            dict: The JSON response from the ComfyUI server (expected to include a job_id).
        """
        url = f"{self.base_url}/api/generate"
        data = {"prompt": prompt}
        if params:
            data.update(params)
        logger.info(f"Sending image generation request to {url} with data: {data}")
        
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Received response: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            raise

    async def get_queue_status(self) -> dict:
        """
        Retrieves the current status of the image generation queue.

        Returns:
            dict: JSON response with the queue status.
        """
        url = f"{self.base_url}/api/queue"
        logger.info(f"Fetching queue status from {url}")
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Queue status: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in get_queue_status: {e}")
            raise

    async def cancel_job(self, job_id: str) -> dict:
        """
        Cancels an image generation job using the provided job_id.

        Args:
            job_id (str): The identifier of the job to cancel.

        Returns:
            dict: The JSON response from the server after canceling the job.
        """
        url = f"{self.base_url}/api/cancel"
        data = {"job_id": job_id}
        logger.info(f"Sending cancel request for job_id {job_id} to {url}")
        try:
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Cancel job response: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in cancel_job: {e}")
            raise

    async def get_job_result(self, job_id: str) -> dict:
        """
        Retrieves the final result of an image generation job.

        Args:
            job_id (str): The identifier of the job.

        Returns:
            dict: The JSON response containing the final result.
        """
        url = f"{self.base_url}/api/job/{job_id}"
        logger.info(f"Fetching result for job_id {job_id} from {url}")
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Job result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in get_job_result: {e}")
            raise