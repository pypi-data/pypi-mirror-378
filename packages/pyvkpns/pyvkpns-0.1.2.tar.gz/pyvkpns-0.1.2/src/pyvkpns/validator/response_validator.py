from typing import List, Dict, Union

from pyvkpns.exceptions import (
    ValidationErrorException, 
    ProviderErrorException,
)


class ResponseValidator:
    
    def validate(
        self, 
        response: Dict[str, Union[str, List[str]]],
    ) -> None:
        
        """
        Validate a response dictionary.

        Depending on the status field in the response, this method 
        raises specific exceptions when errors occur.

        Args:
            response (Dict[str, Union[str, List[str]]]): 
                The response dictionary expected to contain at least 
                a `"status"` key, and optionally `"errors"`.

        Raises:
            ValidationErrorException: If the status is 
            `"VALIDATION_ERROR"`.  
            ProviderErrorException: If the status is 
            `"PROVIDER_ERROR"`.  
        """
        
        match response['status']:
            case 'VALIDATION_ERROR':
                message = (
                    'Validation error occured, ' 
                    f'errors {", ".join(response['errors'])}'
                )
                raise ValidationErrorException(message)

            case 'PROVIDER_ERROR':
                message = 'Invalid vendor auth token'
                raise ProviderErrorException(message)