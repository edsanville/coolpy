from typing import Any, Callable, TypeVar, get_type_hints, get_origin, get_args, Literal
import types

normal_types = set([int, float, str, bool, type(None)])

T = TypeVar("T")

def encode(obj: any):
    t = type(obj)

    if t in normal_types:
        return obj
    
    if t == list or t == set:
        return [encode(item) for item in obj]

    if t == dict:
        return {key: encode(obj[key]) for key in obj if obj[key] is not None}
    
    # python objects
    try:
        return {key: encode(getattr(obj, key)) for key in vars(obj) if getattr(obj, key) is not None}
    except Exception as e:
        raise Exception(f"Cannot serialize object of type '{t}': {obj}, {e}")


def decode(obj: any, Class: Callable[[], T]) -> T:
    if Class is None or Class is Any or obj is None:
        return obj
    
    if isinstance(Class, types.UnionType):
        for type_option in get_args(Class):
            try:
                return decode(obj, type_option)
            except:
                pass
        raise Exception(f"Cannot denormalize '{obj}' to any type in Union '{Class}'")

    t = type(obj)

    if Class == t:
        return obj
    
    # We can convert integers to floats without loss of data
    if Class == float and t == int:
        return float(obj)

    if Class == list:
        return [item for item in obj]
    
    if Class == set:
        return set([item for item in obj])

    if Class == dict:
        return {key: obj[key] for key in obj}
    
    if get_origin(Class) == Literal:
        return obj

    if get_origin(Class) == list:
        assert(t == list)
        type_args = get_args(Class)
        
        if len(type_args) == 0:
            # No type arguments
            return [item for item in obj]

        return [decode(item, type_args[0]) for item in obj]

    if get_origin(Class) == set:
        assert(t == list)
        type_args = get_args(Class)
        
        if len(type_args) == 0:
            # No type arguments
            return set([item for item in obj])

        return set([decode(item, type_args[0]) for item in obj])

    if get_origin(Class) == dict:
        assert(t == dict)
        type_args = get_args(Class)
        
        if len(type_args) == 0:
            # No type arguments
            return {key: obj[key] for key in obj}
        
        key_type, value_type = type_args
        assert(key_type == str)
        value_type = type_args[1]
        return {key: decode(obj[key], value_type) for key in obj}

    # python objects
    if t != dict:
        raise Exception(f"Need a dict when denormalizing to class '{repr(Class)}', got '{t}': {obj}")
    
    kwargs = {}
    for var_name, type_hint in get_type_hints(Class).items():
        if var_name in obj:
            kwargs[var_name] = decode(obj[var_name], type_hint)
    return Class(**kwargs)

