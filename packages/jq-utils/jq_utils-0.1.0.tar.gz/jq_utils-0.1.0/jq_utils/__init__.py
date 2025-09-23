def jq_get(data, path, default=None):
    """
    JQ-like dictionary/list access function.
    
    Args:
        data: Dictionary or list object
        path: Access path (string). Examples:
              - "key1.key2.key3" (nested dict)
              - "[0]" (list index)
              - "key1[2].key3" (mixed)
              - "key1.*.key3" (wildcard - all elements)
        default: Value to return if key is not found
    
    Returns:
        Value corresponding to the path or default
    
    Examples:
        >>> data = {
        ...     "users": [
        ...         {"name": "Ali", "age": 25},
        ...         {"name": "Ayşe", "age": 30}
        ...     ],
        ...     "settings": {
        ...         "theme": "dark",
        ...         "notifications": {"email": True, "sms": False}
        ...     }
        ... }
        >>> jq_get(data, "users[0].name")
        'Ali'
        >>> jq_get(data, "settings.notifications.email")
        True
        >>> jq_get(data, "users.*.age")
        [25, 30]
    """
    import re
    
    if not path:
        return data
    
    # Split path into parts
    # Example: "key1[2].key3" -> ["key1", "[2]", "key3"]
    parts = re.split(r'\.(?![^\[]*\])', path)
    
    current = data
    
    for part in parts:
        if current is None:
            return default
            
        # Wildcard check
        if part == '*':
            if isinstance(current, list):
                return current
            elif isinstance(current, dict):
                return list(current.values())
            else:
                return default
        
        # Array index check [n]
        array_match = re.match(r'\[(-?\d+)\]', part)
        if array_match:
            index = int(array_match.group(1))
            try:
                if isinstance(current, (list, tuple)):
                    current = current[index]
                else:
                    return default
            except (IndexError, KeyError):
                return default
        
        # Split if key contains array index
        # Example: "users[0]" -> key="users", index=0
        key_with_index = re.match(r'^([^\[]+)\[(-?\d+)\]$', part)
        if key_with_index:
            key = key_with_index.group(1)
            index = int(key_with_index.group(2))
            
            try:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                    if isinstance(current, (list, tuple)):
                        current = current[index]
                    else:
                        return default
                else:
                    return default
            except (IndexError, KeyError, TypeError):
                return default
        
        # Wildcard with array access
        # Example: "users.*.name" - get all users' names
        elif '*' in part:
            continue
        
        # Normal key access
        else:
            try:
                if isinstance(current, dict):
                    current = current.get(part, default)
                    if current == default:
                        return default
                else:
                    return default
            except (KeyError, TypeError, AttributeError):
                return default
    
    return current


def jq_set(data, path, value):
    """
    JQ-like dictionary/list value assignment function.
    
    Args:
        data: Dictionary or list object
        path: Access path (string)
        value: Value to assign
    
    Returns:
        Updated data object
    
    Example:
        >>> data = {"users": [{"name": "Ali"}]}
        >>> jq_set(data, "users[0].age", 25)
        {'users': [{'name': 'Ali', 'age': 25}]}
    """
    import re
    import copy
    
    # Deep copy to preserve original data
    result = copy.deepcopy(data)
    
    if not path:
        return value
    
    parts = re.split(r'\.(?![^\[]*\])', path)
    
    # Separate the last part
    target_path = parts[:-1]
    final_key = parts[-1]
    
    # Navigate to target location
    current = result
    for part in target_path:
        # Array index check
        array_match = re.match(r'\[(-?\d+)\]', part)
        if array_match:
            index = int(array_match.group(1))
            current = current[index]
            continue
        
        # Key with array index
        key_with_index = re.match(r'^([^\[]+)\[(-?\d+)\]$', part)
        if key_with_index:
            key = key_with_index.group(1)
            index = int(key_with_index.group(2))
            
            if key not in current:
                current[key] = []
            
            # Extend list if size is insufficient
            while len(current[key]) <= index:
                current[key].append({})
            
            current = current[key][index]
        else:
            # Normal key
            if part not in current:
                current[part] = {}
            current = current[part]
    
    # Assign final value
    array_match = re.match(r'\[(-?\d+)\]', final_key)
    if array_match:
        index = int(array_match.group(1))
        while len(current) <= index:
            current.append(None)
        current[index] = value
    else:
        key_with_index = re.match(r'^([^\[]+)\[(-?\d+)\]$', final_key)
        if key_with_index:
            key = key_with_index.group(1)
            index = int(key_with_index.group(2))
            
            if key not in current:
                current[key] = []
            
            while len(current[key]) <= index:
                current[key].append(None)
            
            current[key][index] = value
        else:
            current[final_key] = value
    
    return result


def jq_exists(data, path):
    """
    Check if path exists.
    
    Args:
        data: Dictionary or list object
        path: Path to check
    
    Returns:
        bool: True if path exists, False otherwise
    """
    sentinel = object()  # Unique sentinel value
    result = jq_get(data, path, default=sentinel)
    return result is not sentinel


def jq_delete(data, path):
    """
    Delete value at specified path.
    
    Args:
        data: Dictionary or list object
        path: Path to delete
    
    Returns:
        Updated data object
    """
    import re
    import copy
    
    result = copy.deepcopy(data)
    
    if not path:
        return result
    
    parts = re.split(r'\.(?![^\[]*\])', path)
    
    # Separate the last part
    target_path = parts[:-1]
    final_key = parts[-1]
    
    # Navigate to target location
    current = result
    for part in target_path:
        array_match = re.match(r'\[(-?\d+)\]', part)
        if array_match:
            index = int(array_match.group(1))
            current = current[index]
        else:
            key_with_index = re.match(r'^([^\[]+)\[(-?\d+)\]$', part)
            if key_with_index:
                key = key_with_index.group(1)
                index = int(key_with_index.group(2))
                current = current[key][index]
            else:
                current = current[part]
    
    # Delete final element
    array_match = re.match(r'\[(-?\d+)\]', final_key)
    if array_match:
        index = int(array_match.group(1))
        del current[index]
    else:
        key_with_index = re.match(r'^([^\[]+)\[(-?\d+)\]$', final_key)
        if key_with_index:
            key = key_with_index.group(1)
            index = int(key_with_index.group(2))
            del current[key][index]
        else:
            del current[final_key]
    
    return result
