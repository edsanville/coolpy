#!/usr/bin/env python3
from coolpy.args import parse_args, Arg
import logging

class Args:
    """Test for coolpy.args"""
    names: list[str] = Arg(default=None, help="Names of the users", nargs="+", choices=["Alice", "Bob", "Charlie"])
    age: int = Arg(help="Age of the user", flags=["-a"])
    foo: bool = Arg(help="A boolean flag")
    log_level: str = Arg(default="INFO", help="Logging level", choices=logging.getLevelNamesMapping().keys())


def cli():
    parsed_args = parse_args(Args())

    logging.basicConfig(level=parsed_args.log_level)
    l = logging.getLogger("test_parse_args")
    l.info("Parsed arguments: %s", parsed_args)


def test_args():
    import sys

    sys.argv = [
        "test_args.py",
        "-a", "30",
        "Alice", "Bob",
        "--foo",
        "--log_level", "DEBUG"
    ]

    args = parse_args(Args())

    assert args.age == 30
    assert args.names == ["Alice", "Bob"]
    assert args.foo is True
    assert args.log_level == "DEBUG"

    print("Args test passed.")


if __name__ == "__main__":
    cli()
