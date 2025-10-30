"""Merge objects, lists, sets, and dicts recursively."""

def merge(*objs):
    """Merge multiple objects into one. Later objects override earlier ones."""
    result = None
    for obj in objs:
        if obj is None:
            continue

        if result is None:
            result = obj
            continue

        if type(result) != type(obj):
            result = obj
            continue

        if isinstance(obj, (int, float, str, bool)):
            result = obj
            continue

        if isinstance(obj, list):
            result = result + obj
        elif isinstance(obj, set):
            result = result.union(obj)
        elif isinstance(obj, dict):
            for key in obj:
                if key in result:
                    result[key] = merge(result[key], obj[key])
                else:
                    result[key] = obj[key]
        else:
            for name in vars(obj):
                name: str
                if name.startswith('_'):
                    continue

                setattr(result, name,
                        merge(getattr(result, name, None), getattr(obj, name, None)))

    return result
