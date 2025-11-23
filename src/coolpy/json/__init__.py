import coolpy.coding as coding
from typing import Any, Generic, Callable, Union, TypeVar
import json

T = TypeVar('T')

def dumps(obj: Any, **kwargs):
    return json.dumps(coding.encode(obj), **kwargs)


def dump(obj: Any, fp, **kwargs):
    json.dump(coding.encode(obj), fp, **kwargs)


def loads(s: Union[str, bytes, bytearray], Class: Callable[[], T], **kwargs) -> T:
    return coding.decode(json.loads(s, **kwargs), Class)


def load(fp, Class: Callable[[], T], **kwargs) -> T:
    return coding.decode(json.load(fp, **kwargs), Class)


class JSONFile(Generic[T]):
    filename: str
    contents: T
    minify: bool = False

    def __init__(self, filename: str, Class: Callable[[], T], minify: bool = False):
        self.filename = filename
        self.minify = minify
        
        try:
            self.contents = load(open(filename, 'r'), Class)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.contents = Class()

    def save(self):
        if self.minify:
            dump(self.contents, open(self.filename, 'w'), separators=(',', ':'))
        else:
            dump(self.contents, open(self.filename, 'w'), indent=4, sort_keys=True)
