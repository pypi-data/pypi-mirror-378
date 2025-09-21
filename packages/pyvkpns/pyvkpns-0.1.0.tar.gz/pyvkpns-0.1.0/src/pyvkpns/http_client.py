from typing import Dict, Union
import aiohttp

from src.pyvkpns.credentials import VKPNS_LINK, HEADERS


class HttpClient:
    
    _instance = None
    _session: aiohttp.ClientSession | None = None

    def __new__(cls, *args, **kwargs):
        
        """
        Implements the Singleton pattern — always returns the same 
        instance of HttpClient.
        """
        
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _get_session(
        self,
    ) -> aiohttp.ClientSession:
        
        """
        Create or return an existing aiohttp session.

        Returns:
            aiohttp.ClientSession: The active HTTP session.
        """
        
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def send(
        self,
        payload: Dict[str, Union[str, Dict]],
    ) -> Dict[str, Union[str, Dict]]:
        
        """
        Send a POST request to the VKPNS API.

        Args:
            payload (Dict[str, Union[str, Dict]]): JSON payload to send 
            in the POST request.

        Returns:
            Dict[str, Union[str, Dict]]: The server response parsed from
            JSON.

        Raises:
            aiohttp.ClientError: If a client-related error occurs.
            asyncio.TimeoutError: If the request times out.
        """
        
        session = await self._get_session()
        async with session.post(
            url=VKPNS_LINK,
            headers=HEADERS,
            json=payload,
            timeout=5,
        ) as response:
            return await response.json()

    async def close(self):
        
        """
        Close the aiohttp session if it is open.
        """     
        
        if self._session and not self._session.closed:
            await self._session.close()