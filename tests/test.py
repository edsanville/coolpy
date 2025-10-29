#!/usr/bin/env python3
from coolpy.args import parse_args
from dataclasses import dataclass, field


@dataclass
class Args:
    """Test for coolpy.args"""
    names: list[str] = field(metadata={"help": "Names of the users", "nargs": "+", "choices": ["Alice", "Bob", "Charlie"]})
    age: int = field(metadata={"help": "Age of the user", "flags": ["-a"]})
    foo: bool = field(default=False, metadata={"help": "A boolean flag"})


def test_parse_args():
    parsed_args: Args = parse_args(Args)
    parsed_args.names
    print(parsed_args)

if __name__ == "__main__":
    test_parse_args()