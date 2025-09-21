from typing import Any


def convert_empty_to_none(obj: Any) -> Any:
    
    """
    Recursively convert empty strings to None.

    This function walks through nested structures such as dictionaries,
    lists, and dataclasses, replacing any empty string values ("") with
    `None`.

    Args:
        obj (Any): The object to process. Can be a dict, list, 
        dataclass, string, or any other type.

    Returns:
        Any: A copy of the object with empty strings replaced by None.
        - dict: Returns a dict with all nested values processed.
        - list: Returns a list with all elements processed.
        - dataclass: Returns a new dataclass instance with processed 
        fields.
        - str: Returns None if the string is empty, otherwise the 
        string.
        - other: Returns the object unchanged.

    Example:
        >>> convert_empty_to_none({"a": "", "b": ["", "x"]})
        {'a': None, 'b': [None, 'x']}
    """
    
    if isinstance(obj, dict):
        return {k: convert_empty_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_empty_to_none(v) for v in obj]
    elif isinstance(obj, str) and obj == "":
        return None
    elif hasattr(obj, "__dataclass_fields__"):  
        return obj.__class__(**{
            k: convert_empty_to_none(getattr(obj, k))
            for k in obj.__dataclass_fields__
        })
    else:
        return obj