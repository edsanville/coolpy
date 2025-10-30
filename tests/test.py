#!/usr/bin/env python3
from coolpy.args import parse_args, Arg


class Args:
    """Test for coolpy.args"""
    names: list[str] = Arg(default=None, help="Names of the users", nargs="+", choices=["Alice", "Bob", "Charlie"])
    age: int = Arg(help="Age of the user", flags=["-a"])
    foo: bool = Arg(default=False, help="A boolean flag")


def test_parse_args():
    parsed_args = parse_args(Args())
    parsed_args.names
    print(parsed_args)

if __name__ == "__main__":
    test_parse_args()
