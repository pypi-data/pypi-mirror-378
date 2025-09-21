from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ProviderCred:
    
    """
    Represents the credentials required for a push notification 
    provider.

    Attributes:
        project_id (Optional[str]): The project identifier of the 
        provider.
        auth_token (Optional[str]): The authentication token used to 
        authorize requests.
    """
    
    project_id: Optional[str] = None
    auth_token: Optional[str] = None


@dataclass
class Notification:
    
    """
    Represents a generic notification payload.

    Attributes:
        title (Optional[str]): The notification title.
        body (Optional[str]): The notification body text.
        image (Optional[str]): An optional image URL to include in the 
        notification.
    """
    
    title: Optional[str] = None
    body: Optional[str] = None
    image: Optional[str] = None


@dataclass
class AndroidNotification:
    
    """
    Represents Android-specific notification options.

    Attributes:
        title (Optional[str]): Notification title.
        body (Optional[str]): Notification body text.
        icon (Optional[str]): The icon resource name for the 
        notification.
        color (Optional[str]): Accent color in `#RRGGBB` format.
        image (Optional[str]): Image URL for rich notifications.
        channel_id (Optional[str]): The notification channel ID.
        click_action (Optional[str]): The action to perform when the 
        notification is clicked.
    """
    
    title: Optional[str] = None
    body: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    image: Optional[str] = None
    channel_id: Optional[str] = None
    click_action: Optional[str] = None


@dataclass
class Android:
    
    """
    Represents Android-specific message configuration.

    Attributes:
        ttl (Optional[str]): Time-to-live duration (e.g., "3600").
        notification (Optional[AndroidNotification]): The notification 
        details for Android devices.
    """
    
    ttl: Optional[str] = None
    notification: Optional[AndroidNotification] = None


@dataclass
class Message:
    
    """
    Represents a push notification message.

    Attributes:
        notification (Optional[Notification]): A generic notification 
        payload.
        android (Optional[Android]): Android-specific notification 
        settings.
    """
    
    notification: Optional[Notification] = None
    android: Optional[Android] = None


@dataclass
class VKPNSMessage:
    
    """
    Represents the full VKPNS notification message payload.

    Attributes:
        providers (Optional[Dict[str, ProviderCred]]): A mapping of 
        providers (e.g., "fcm") to their credentials.
        tokens (Optional[Dict[str, List[str]]]): A mapping of providers 
        to lists of device tokens.
        message (Optional[Message]): The actual notification message 
        content.
    """
    
    providers: Optional[Dict[str, ProviderCred]] = field(default_factory=dict)
    tokens: Optional[Dict[str, List[str]]] = field(default_factory=dict)
    message: Optional[Message] = None