from typing import Any


def remove_none(d: Any) -> Any:
    
    """
    Recursively remove None values from dictionaries and lists.

    This function traverses nested dictionaries and lists, filtering out
    any keys or elements whose value is `None`.

    Args:
        d (Any): The object to process. Can be a dict, list, or any 
        other type.

    Returns:
        Any: A copy of the object with all None values removed.
        - dict: Returns a dict with None values filtered out.
        - list: Returns a list with None elements removed.
        - other: Returns the object unchanged.

    Example:
        >>> remove_none({"a": None, "b": 1, "c": [None, 2, None]})
        {'b': 1, 'c': [2]}
    """
    
    if isinstance(d, dict):
        return {k: remove_none(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_none(v) for v in d if v is not None]
    else:
        return d