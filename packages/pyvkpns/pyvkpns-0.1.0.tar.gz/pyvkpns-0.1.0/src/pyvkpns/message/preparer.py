from typing import List
from dataclasses import asdict

from src.pyvkpns.utils import remove_none, convert_empty_to_none
from src.pyvkpns.message.model import (
    VKPNSMessage,
    ProviderCred,
    Message,
    Notification,
    Android,
    AndroidNotification,
)


class MessagePreparer:
    
    """
    Prepares notification payloads for VKPNS.

    This class builds a structured payload based on the given 
    notification parameters. It converts empty strings into `None` 
    values and removes any fields with `None` values from the final 
    output.
    """
    
    def prepare(
        self,
        project_id: str,
        auth_token: str,
        platform: str,
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
        Prepare a JSON-compatible dictionary for sending a 
        notification.

        Args:
            project_id (str): The project identifier for the provider.
            auth_token (str): The authentication token for the provider.
            platform (str): Target platform (e.g., "fcm", "huawei", 
            "apns").
            tokens (List[str]): List of device tokens to send the 
            notification to.
            title (str): The title of the notification.
            body (str): The body text of the notification.
            ttl (str, optional): Time-to-live for the notification.
            icon (str, optional): Notification icon.
            image (str, optional): Notification image URL.
            channel_id (str, optional): Notification channel identifier.
            click_action (str, optional): Action triggered on 
            notification click.
            color (str, optional): Accent color for the notification.

        Returns:
            dict: A dictionary payload with empty strings converted to 
            `None` and `None` fields removed.

        Example:
            >>> preparer = MessagePreparer()
            >>> data = preparer.prepare(
            ...     project_id="proj_123",
            ...     auth_token="token_abc",
            ...     platform="fcm",
            ...     tokens=["tok1"],
            ...     title="Hello",
            ...     body="World"
            ... )
            >>> "providers" in data
            True
        """
        
        json = VKPNSMessage(
            providers={
                f'{platform}': ProviderCred(
                    project_id=project_id,
                    auth_token=auth_token,
                ),
            },
            tokens={
                f'{platform}': tokens,
            },
            message=Message(
                notification=Notification(
                    title=title,
                    body=body,
                ),
                android=Android(
                    ttl=ttl,
                    notification=AndroidNotification(
                        title=title,
                        body=body,
                        icon=icon,
                        color=color,
                        image=image,
                        channel_id=channel_id,
                        click_action=click_action,
                    ),
                ),
            ),
        )
        
        data = asdict(json)
        clear_data = convert_empty_to_none(data)
        return remove_none(clear_data)