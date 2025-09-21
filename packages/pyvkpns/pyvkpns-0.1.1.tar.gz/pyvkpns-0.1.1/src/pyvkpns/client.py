from typing import List

from pyvkpns.http_client import HttpClient
from pyvkpns.message.preparer import MessagePreparer
from pyvkpns.validator import ResponseValidator


class VKPNSClient:
    
    """
    Client for sending push notifications via the VKPNS service.
    """
    
    def __init__(
        self,
        project_id: str,
        service_token: str,
        platform: str,
    ) -> None:
        
        """
        Initialize the VKPNS client.

        Args:
            project_id (str): Project identifier from VKPNS.
            service_token (str): Authentication token for the service.
            platform (str): Target platform 
            (e.g., "fcm", "huawei", "apns").
        """
        
        self._project_id = project_id
        self._service_token = service_token
        self._platform = platform
        self._client = HttpClient()
        self._message_preparer = MessagePreparer()
        self._response_validator = ResponseValidator()
    
    async def send_notification(
        self,
        tokens: List[str],
        title: str,
        body: str,
        ttl: str = None,
        icon: str = None,
        image: str = None,
        channel_id: str = None,
        click_action: str = None,
        color: str = None,
    ) -> None:
        
        """
        Send a push notification to the specified tokens.

        Args:
            tokens (List[str]): List of device tokens to receive the 
            notification.
            title (str): Notification title.
            body (str): Notification body text.
            ttl (str, optional): Time-to-live for the notification 
            (e.g., "3600").
            icon (str, optional): Notification icon identifier.
            image (str, optional): URL or identifier for the 
            notification image.
            channel_id (str, optional): Android channel ID.
            click_action (str, optional): Action triggered when the 
            notification is clicked.
            color (str, optional): Notification color (e.g., "#FF0000").

        Raises:
            ValidationErrorException: If the VKPNS API returns a 
            validation error.
            ProviderErrorException: If the VKPNS API returns a provider 
            error.
        """
        
        data = self._message_preparer.prepare(
            self._project_id,
            self._service_token,
            platform=self._platform,
            title=title,
            body=body,
            ttl=ttl,
            icon=icon,
            image=image,
            channel_id=channel_id,
            click_action=click_action,
            tokens=tokens,
            color=color,
        )
        response = await self._client.send(data)
        self._response_validator.validate(response)