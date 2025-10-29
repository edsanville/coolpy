import typing as t
import argparse
import os
import sys
from dataclasses import dataclass, _MISSING_TYPE, Field


def parse_args(ArgsClass, prog: str=os.path.basename(sys.argv[0]), description: str=None):
    if description is None:
        description = ArgsClass.__doc__

    parser = argparse.ArgumentParser(prog=prog, description=description)

    for arg_name, ArgType in t.get_type_hints(ArgsClass).items():
        optional = False
        function_args = []
        function_kwargs = {}

        # Get dataclass field info if available
        field_info: Field = getattr(ArgsClass, '__dataclass_fields__', {}).get(arg_name)
        if field_info is not None:
            if not isinstance(field_info.default, _MISSING_TYPE):
                function_kwargs['default'] = field_info.default
                optional = True
            if 'help' in field_info.metadata:
                function_kwargs['help'] = field_info.metadata['help']
            if not isinstance(field_info.default_factory, _MISSING_TYPE):
                function_kwargs['default'] = field_info.default_factory()
                optional = True
            if 'nargs' in field_info.metadata:
                function_kwargs['nargs'] = field_info.metadata['nargs']
            if 'choices' in field_info.metadata:
                function_kwargs['choices'] = field_info.metadata['choices']
            if 'flags' in field_info.metadata:
                function_args = field_info.metadata['flags']
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

        print(function_args, function_kwargs)
        parser.add_argument(*function_args, **function_kwargs)

    args = parser.parse_args()
    return args
