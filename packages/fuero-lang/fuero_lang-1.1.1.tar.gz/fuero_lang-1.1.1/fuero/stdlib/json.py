"""
json utilities for fuero
provides json parsing, serialization, and manipulation functions
"""

import json
import jsonschema
from typing import Any, Dict, List, Optional, Union


class Json:
    """json processing and manipulation utilities"""
    
    def __init__(self):
        pass
    
    # Basic JSON operations
    def parse(self, json_string: str) -> Any:
        """Parse JSON string to Python object"""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def stringify(self, obj: Any, indent: Optional[int] = None, sort_keys: bool = False) -> str:
        """Convert Python object to JSON string"""
        try:
            return json.dumps(obj, indent=indent, sort_keys=sort_keys, ensure_ascii=False)
        except TypeError as e:
            raise ValueError(f"Object not JSON serializable: {e}")
    
    def pretty_print(self, obj: Any, indent: int = 2) -> str:
        """Convert object to pretty-printed JSON string"""
        return self.stringify(obj, indent=indent, sort_keys=True)
    
    # File operations
    def load_file(self, filepath: str) -> Any:
        """Load JSON from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {filepath}: {e}")
    
    def save_file(self, obj: Any, filepath: str, indent: Optional[int] = 2) -> bool:
        """Save object to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(obj, f, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            raise IOError(f"Failed to save JSON file {filepath}: {e}")
    
    # JSON manipulation
    def get_value(self, obj: Dict, path: str, default: Any = None) -> Any:
        """Get value from nested JSON using dot notation path"""
        keys = path.split('.')
        current = obj
        
        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, list) and key.isdigit():
                    current = current[int(key)]
                else:
                    return default
            return current
        except (KeyError, IndexError, TypeError):
            return default
    
    def set_value(self, obj: Dict, path: str, value: Any) -> Dict:
        """Set value in nested JSON using dot notation path"""
        keys = path.split('.')
        current = obj
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        return obj
    
    def delete_key(self, obj: Dict, path: str) -> Dict:
        """Delete key from nested JSON using dot notation path"""
        keys = path.split('.')
        current = obj
        
        try:
            for key in keys[:-1]:
                current = current[key]
            del current[keys[-1]]
        except KeyError:
            pass  # Key doesn't exist, nothing to delete
        
        return obj
    
    def has_key(self, obj: Dict, path: str) -> bool:
        """Check if key exists in nested JSON using dot notation path"""
        return self.get_value(obj, path, object()) is not object()
    
    # JSON merging and manipulation
    def merge(self, obj1: Dict, obj2: Dict, deep: bool = True) -> Dict:
        """Merge two JSON objects"""
        if not deep:
            result = obj1.copy()
            result.update(obj2)
            return result
        
        def deep_merge(dict1, dict2):
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(obj1, obj2)
    
    def flatten(self, obj: Dict, separator: str = '.') -> Dict:
        """Flatten nested JSON object"""
        def _flatten(obj, parent_key='', sep='.'):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(_flatten(v, new_key, sep=sep).items())
                    elif isinstance(v, list):
                        for i, item in enumerate(v):
                            items.extend(_flatten(item, f"{new_key}{sep}{i}", sep=sep).items())
                    else:
                        items.append((new_key, v))
            return dict(items)
        
        return _flatten(obj, sep=separator)
    
    def unflatten(self, obj: Dict, separator: str = '.') -> Dict:
        """Unflatten a flattened JSON object"""
        result = {}
        for key, value in obj.items():
            keys = key.split(separator)
            current = result
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
        
        return result
    
    # JSON filtering and transformation
    def filter_keys(self, obj: Dict, keys: List[str], include: bool = True) -> Dict:
        """Filter JSON object by keys"""
        if include:
            return {k: v for k, v in obj.items() if k in keys}
        else:
            return {k: v for k, v in obj.items() if k not in keys}
    
    def map_values(self, obj: Dict, func) -> Dict:
        """Apply function to all values in JSON object"""
        result = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                result[key] = self.map_values(value, func)
            elif isinstance(value, list):
                result[key] = [self.map_values(item, func) if isinstance(item, dict) else func(item) for item in value]
            else:
                result[key] = func(value)
        return result
    
    def find_values(self, obj: Any, key: str) -> List[Any]:
        """Find all values for a given key in nested JSON"""
        results = []
        
        def _find(obj, target_key):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == target_key:
                        results.append(v)
                    _find(v, target_key)
            elif isinstance(obj, list):
                for item in obj:
                    _find(item, target_key)
        
        _find(obj, key)
        return results
    
    # JSON validation
    def validate_schema(self, obj: Any, schema: Dict) -> bool:
        """Validate JSON object against schema"""
        try:
            jsonschema.validate(obj, schema)
            return True
        except jsonschema.ValidationError:
            return False
    
    def get_validation_errors(self, obj: Any, schema: Dict) -> List[str]:
        """Get validation errors for JSON object against schema"""
        errors = []
        try:
            jsonschema.validate(obj, schema)
        except jsonschema.ValidationError as e:
            errors.append(str(e))
        return errors
    
    # JSON comparison
    def equals(self, obj1: Any, obj2: Any) -> bool:
        """Deep comparison of two JSON objects"""
        return obj1 == obj2
    
    def diff(self, obj1: Dict, obj2: Dict) -> Dict:
        """Find differences between two JSON objects"""
        def _diff(o1, o2, path=""):
            differences = {}
            
            # Check for keys in obj1 but not in obj2
            for key in o1:
                current_path = f"{path}.{key}" if path else key
                if key not in o2:
                    differences[current_path] = {"type": "removed", "value": o1[key]}
                elif isinstance(o1[key], dict) and isinstance(o2[key], dict):
                    nested_diff = _diff(o1[key], o2[key], current_path)
                    differences.update(nested_diff)
                elif o1[key] != o2[key]:
                    differences[current_path] = {
                        "type": "changed",
                        "old_value": o1[key],
                        "new_value": o2[key]
                    }
            
            # Check for keys in obj2 but not in obj1
            for key in o2:
                current_path = f"{path}.{key}" if path else key
                if key not in o1:
                    differences[current_path] = {"type": "added", "value": o2[key]}
            
            return differences
        
        return _diff(obj1, obj2)
    
    # JSON utilities
    def size(self, obj: Any) -> int:
        """Get size of JSON object (number of keys at all levels)"""
        def _count(obj):
            if isinstance(obj, dict):
                return len(obj) + sum(_count(v) for v in obj.values())
            elif isinstance(obj, list):
                return len(obj) + sum(_count(item) for item in obj)
            else:
                return 0
        
        return _count(obj)
    
    def keys_at_depth(self, obj: Dict, depth: int) -> List[str]:
        """Get all keys at a specific depth"""
        def _get_keys(obj, current_depth, target_depth):
            if current_depth == target_depth:
                return list(obj.keys()) if isinstance(obj, dict) else []
            
            keys = []
            if isinstance(obj, dict):
                for value in obj.values():
                    keys.extend(_get_keys(value, current_depth + 1, target_depth))
            elif isinstance(obj, list):
                for item in obj:
                    keys.extend(_get_keys(item, current_depth + 1, target_depth))
            
            return keys
        
        return _get_keys(obj, 0, depth)
    
    def max_depth(self, obj: Any) -> int:
        """Get maximum depth of nested JSON object"""
        def _depth(obj):
            if isinstance(obj, dict):
                return 1 + max((_depth(v) for v in obj.values()), default=0)
            elif isinstance(obj, list):
                return 1 + max((_depth(item) for item in obj), default=0)
            else:
                return 0
        
        return _depth(obj)
    
    def to_csv_rows(self, obj: List[Dict]) -> List[List[str]]:
        """Convert list of JSON objects to CSV rows"""
        if not obj or not isinstance(obj, list):
            return []
        
        # Get all unique keys
        all_keys = set()
        for item in obj:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        
        headers = sorted(all_keys)
        rows = [headers]
        
        for item in obj:
            if isinstance(item, dict):
                row = [str(item.get(key, '')) for key in headers]
                rows.append(row)
        
        return rows
