#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from dill import (
    load as dill_load
)

from utils.tracing import exec_under_trace
from utils.ast_patches import (
    parse_tree,
    apply_patches
)


def trace_function(frame, event, arg):
    if _call_stack:
        match event:
            case 'line':
                print(f'{frame.f_lineno}..', end='')
                frame.f_lineno, f_locals = _call_stack.pop()
                print(f'{frame.f_lineno}')
                for key, value in f_locals.items():
                    frame.f_locals[key] = value
            case 'call':
                return trace_function


def main(snapshot: Path, file: Path):
    global _call_stack
    
    with open(snapshot, 'rb') as _file:
        _call_stack, for_slices, raise_exceptions, _file = dill_load(_file)
    
    file = file or _file
    
    source_code = file.read_text()
    
    tree = parse_tree(source_code)
    tree = apply_patches(tree, for_slices, raise_exceptions)
    
    exec_under_trace(file, tree, trace_function)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    
    arg_parser.add_argument(
        "snapshot_path",
        type=lambda path: Path(__file__).resolve().parent / path,
        nargs="?",
        default=Path('snapshot').resolve()
    )
    arg_parser.add_argument(
        "script_path",
        type=lambda path: Path(path).resolve(),
        nargs="?"
    )
    
    args = list(vars(arg_parser.parse_args()).values())

    main(*args)