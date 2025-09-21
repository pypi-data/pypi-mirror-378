class ProviderErrorException(Exception):
    
    """
    Exception raised when a provider-related error occurs.
    """

    def __init__(
        self, 
        message: str,
    ) -> None:
  
        """
        Initialize ProviderErrorException.

        Args:
            message (str): Human-readable error message.
        """
        
        super().__init__(message)


class ValidationErrorException(Exception):
    
    """
    Exception raised when a validation error occurs.
    """

    def __init__(
        self, 
        message: str,
    ) -> None:
        
        """
        Initialize ValidationErrorException.

        Args:
            message (str): Human-readable error message.
        """
        
        super().__init__(message)