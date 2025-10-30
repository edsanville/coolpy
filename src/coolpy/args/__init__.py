import typing as t
import argparse
import os
import sys
from dataclasses import dataclass

"""Use a class with type hints to define and parse command line arguments."""

@dataclass
class Arg:
    default: any = None
    default_factory: t.Callable[[], any] = None
    help: str = None
    flags: list[str] = None
    nargs: int = None
    choices: list[any] = None


T = t.TypeVar('T')


def parse_args(args: T, prog: str=os.path.basename(sys.argv[0]), description: str=None) -> T:
    """Parse command-line arguments using a class with type hints for each argument.

    Args:
        args (T): An instance of a class with a type-hinted attribute for each argument, and optional Arg metadata.
        prog (str, optional): The name of the program. Defaults to os.path.basename(sys.argv[0]).
        description (str, optional): A brief description of the program. Defaults to None.

    Returns:
        T: An instance of the class with the parsed arguments.
    """
    if description is None:
        description = args.__doc__

    parser = argparse.ArgumentParser(prog=prog, description=description)

    for arg_name, ArgType in t.get_type_hints(args).items():
        arg: Arg = getattr(args, arg_name, None)

        optional = False
        function_args = []
        function_kwargs = {}

        if arg is not None:
            if arg.default is not None:
                function_kwargs['default'] = arg.default
                optional = True
            if arg.help is not None:
                function_kwargs['help'] = arg.help
            if arg.default_factory is not None:
                function_kwargs['default'] = arg.default_factory()
                optional = True
            if arg.nargs is not None:
                function_kwargs['nargs'] = arg.nargs
            if arg.choices is not None:
                function_kwargs['choices'] = arg.choices
            if arg.flags is not None:
                function_args = arg.flags
                optional = True

        # bools are special cased
        if ArgType == bool:
            function_args.append(f'--{arg_name}')
            function_kwargs['action'] = 'store_true'
        else:
            if optional:
                if f'--{arg_name}' not in function_args:
                    function_args.append(f'--{arg_name}')
            else:
                function_args.append(arg_name)

            if 'nargs' in function_kwargs:
                function_kwargs['type'] = t.get_args(ArgType)[0]
            else:
                function_kwargs['type'] = ArgType

        parser.add_argument(*function_args, **function_kwargs)

    args = parser.parse_args()
    return args
