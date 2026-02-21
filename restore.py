#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from dill import (
    load as dill_load
)

from utils.tracing import use_path, yield_overhead_then_trace
from utils.ast_patches import (
    code_to_tree,
    apply_restore_patches
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


def main(file: Path, snapshot: Path):
    global call_stack
    
    with use_path(str(file.parent)): # because dill_load reapplies imports & fds.
        with open(snapshot, 'rb') as open_file:
            call_stack, for_slices, exceptions, code_block_parts, optimisation_level = dill_load(open_file)

        try:
            source_code = file.read_text()
        except UnicodeDecodeError, FileNotFoundError:
            raise RuntimeError('invalid file') from None

        tree = code_to_tree(source_code)
        tree = apply_restore_patches(tree, for_slices, exceptions, code_block_parts)

        tracer = yield_overhead_then_trace(file, tree, trace_function, optimisation_level)
        TRACING_OVERHEAD = next(tracer)
        next(tracer, None)


if __name__ == "__main__":
    arg_parser = ArgumentParser()

    arg_parser.add_argument(
        "script_path",
        type=lambda path: Path(path).resolve()
    )
    
    arg_parser.add_argument(
        "snapshot_path",
        type=lambda path: Path(path).resolve(),
        nargs="?",
        default=Path(__file__).resolve().parent / 'snapshot'
    )
    
    args = arg_parser.parse_args()
    
    main(
        args.script_path,
        args.snapshot_path
    )