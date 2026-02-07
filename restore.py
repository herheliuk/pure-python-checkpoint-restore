#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from dill import (
    load as dill_load
)

from utils.tracing import yield_overhead_then_trace
from utils.ast_patches import (
    parse_tree,
    apply_patches
)


def trace_function(frame, event, arg):
    if call_stack:
        match event:
            case 'line': 
                next_line, required_locals = call_stack.pop()
                
                if __debug__:
                    print(f'{frame.f_lineno}..{next_line}')
                
                frame.f_locals.update(required_locals)
                if frame.f_lineno != next_line: # avoid RuntimeWarning
                    frame.f_lineno = next_line
            
            case 'call':
                if __debug__:
                    print(f'[{frame.f_lineno}]')
                    
                return trace_function


def main(snapshot: Path, file: Path):
    global call_stack
    
    with open(snapshot, 'rb') as open_file:
        call_stack, for_slices, exceptions, saved_file = dill_load(open_file)
    
    file = file or saved_file
    
    try:
        source_code = file.read_text()
    except UnicodeDecodeError:
        raise RuntimeError('invalid file') from None
    
    tree = parse_tree(source_code)
    tree = apply_patches(tree, for_slices, exceptions)
    
    tracer = yield_overhead_then_trace(file, tree, trace_function)
    TRACING_OVERHEAD = next(tracer)
    next(tracer)


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