#!/usr/bin/env python3

from os import _exit
from pathlib import Path
from dill import dump as dill_dump

from utils.ast_find import parse_triggers
from utils.frame_stack import walk_frames_to_root
from utils.tracing import use_path, yield_overhead_then_trace
from utils.ast_patches import (
    code_to_tree,
    apply_pre_dump_patches
)

block_stack: dict[int, dict[int, dict]] = {}
line_occurrences: dict[int, int] = {}

for_slices: dict[int, dict[int, int]] = {}
raise_exceptions: dict[int, Exception] = {}

generators: dict[int, int | dict] = {}
gen_ids = set()

block_code_var_promisses: dict[int, int] = {}

code_block_parts: set[str] = set()

def trace_function(frame, event, arg):
    line_number = frame.f_lineno

    #print(f"{f'  {event} {line_number} {line_occurrences.get(line_number, 0) + 1} ':-^50}")
    
    match event:
        case 'line':
            line_occurrences[line_number] = occurrence = line_occurrences.get(line_number, 0) + 1
            
            frame_id = id(frame)
            
            if promise_data := block_code_var_promisses.pop(frame_id, None):
                entry_line, offset = promise_data
                name_start = f'line_{entry_line}'
                
                filrered_locals = {}
                
                for name, value in dict(frame.f_locals).items():
                    if name.startswith(name_start):
                        filrered_locals[name] = value
                        code_block_parts.add(name)
                
                block_stack[frame_id][offset][1].update(filrered_locals)
            
            if trigger_data := _triggers.get(line_number):
                code_block, offset = trigger_data

                new_entry = (line_number, dict(frame.f_locals))
                
                _block_stack = block_stack.setdefault(frame_id, [])
                
                if offset >= len(_block_stack):
                    _block_stack.append(new_entry)
                else:
                    _block_stack[offset] = new_entry
                    del _block_stack[offset + 1:]
                    
                match code_block:
                    case 'For':
                        for_slice_slot = for_slices[frame_id]
                        
                        slice_index = for_slice_slot.get(line_number, -1) + 1
                        
                        for_slice_slot[line_number] = slice_index
                        
                        if not slice_index: # slice_index == 0
                            block_code_var_promisses[frame_id] = line_number, offset
                    
                    case 'With':
                        block_code_var_promisses[frame_id] = line_number, offset
            
            if (
                line_number == _dump_line
                and
                occurrence >= _dump_occurrence
            ):
                if __debug__:
                    print(f"{f'  DUMPING at line {line_number} ':-^50}")

                call_stack = []
                
                for frame in walk_frames_to_root(frame):
                    
                    frame_id = id(frame)
                    
                    new_entry = (frame.f_lineno, dict(frame.f_locals))
                    
                    block_calls = block_stack.get(frame_id, [])
                    block_calls.reverse()
                    
                    if (
                        not block_calls
                        or
                        block_calls[-1] != new_entry
                    ):
                        call_stack.append(new_entry)
                    
                    call_stack.extend(block_calls)

                del call_stack[-TRACING_OVERHEAD:]
                
                _for_slices: dict[int, int] = {
                    inner_key: inner_value
                    for outer in for_slices.values()
                    for inner_key, inner_value in outer.items()
                }
                
                with _snapshot.open('wb') as file:
                    dill_dump((
                        call_stack,
                        _for_slices,
                        raise_exceptions,
                        code_block_parts,
                        _optimisation_level
                    ), file)
                
                if __debug__:
                    print(f"{f'  DUMPING COMPLETE ':-^50}")
                
                _exit(0)
        
        case 'call':
            frame_id = id(frame)
            
            for_slices[frame_id] = {}
            
            if line_number in _generators:
                gen_ids.add(frame_id)
                generators[frame.f_back.f_lineno] = frame_id
            
            return trace_function
        
        case 'return':
            if (frame_id := id(frame)) in gen_ids:
                _block_stack = block_stack.setdefault(frame_id, [])
                _block_stack.append((line_number, dict(frame.f_locals)))
        
        case 'exception':
            exc_type, exc_value, exc_traceback = arg
            
            raise_exceptions[line_number] = exc_value # BUG use if(frame) as well!
            
            _block_stack = block_stack.setdefault(id(frame), [])
            _block_stack.append((line_number, dict(frame.f_locals)))
            
            if __debug__:
                str_exc_value = str(exc_value)
                print(exc_type.__name__ + (f": {str_exc_value}" if str_exc_value else ""))


def main(file: Path, dump_line: int, dump_occurrence: int, snapshot: Path, optimisation_level: int) -> None:
    global _triggers, _dump_line, _dump_occurrence, _snapshot, _generators, TRACING_OVERHEAD, _optimisation_level
    
    try:
        source_code = file.read_text()
    except UnicodeDecodeError, FileNotFoundError:
        raise RuntimeError('invalid file')
    
    lines = source_code.splitlines()

    if dump_line not in range(len(lines) + 1):
        raise ValueError("dump_line is out of range")

    if not lines[dump_line - 1].strip():
        raise ValueError("requested line is empty")
    # TODO: check if the line is accessible with AST

    _triggers, _generators = parse_triggers(source_code)
    
    _dump_line, _dump_occurrence, _snapshot, _optimisation_level = dump_line, dump_occurrence, snapshot, optimisation_level
    
    tree = code_to_tree(source_code)
    tree = apply_pre_dump_patches(tree)

    with use_path(str(file.parent)):
        tracer = yield_overhead_then_trace(file, tree, trace_function, optimisation_level)
        TRACING_OVERHEAD = next(tracer)
        next(tracer, None)
    
    print("\033[31m" + 'NERVER DUMPED' + "\033[0m")
    exit(1)


if __name__ == "__main__":
    from argparse import ArgumentParser
    
    arg_parser = ArgumentParser()
    
    arg_parser.add_argument("script_path", type=lambda path: Path(path).resolve())
    arg_parser.add_argument("dump_line", type=int)
    arg_parser.add_argument("dump_occurrence", type=int, nargs="?", default=1)
    arg_parser.add_argument(
        "snapshot_path",
        type=lambda path: Path(path).resolve(),
        nargs="?",
        default=Path(__file__).parent / "snapshot"
    )
    
    arg_parser.add_argument(
        "-O",
        dest="optimisation_level",
        action="count",
        default=0,
        help="Disable debug and enable optimisation with -O or -OO"
    )
    
    args = arg_parser.parse_args()
    
    main(
        args.script_path,
        args.dump_line,
        args.dump_occurrence,
        args.snapshot_path,
        args.optimisation_level
    )