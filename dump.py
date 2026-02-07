#!/usr/bin/env python3

from argparse import ArgumentParser
from os import _exit
from pathlib import Path
from dill import dump as dill_dump

from utils.ast_find import parse_triggers
from utils.frame_stack import walk_frames_to_root
from utils.tracing import yield_overhead_then_trace


block_stack: dict[int, dict[int, dict]] = {}
line_occurrences: dict[int, int] = {}

for_slices: dict[int, dict[int, int]] = {}
raise_exceptions: dict[int, Exception] = {}

generators: dict[int, int | dict] = {}
gen_ids = set()


def trace_function(frame, event, arg):
    line_number = frame.f_lineno

    #print(f"{f'  {event} {line_number} {line_occurrences.get(line_number, 0) + 1} ':-^50}")
    
    match event:
        case 'line':
            line_occurrences[line_number] = occurrence = line_occurrences.get(line_number, 0) + 1
            
            if trigger_data := _triggers.get(line_number):
                code_block, offset = trigger_data
                
                frame_id = id(frame)
                
                new_entry = (line_number, dict(frame.f_locals))
                
                _block_stack = block_stack.setdefault(frame_id, [])
                
                if offset >= len(_block_stack):
                    _block_stack.append(new_entry)
                else:
                    _block_stack[offset] = new_entry
                    del _block_stack[offset + 1:]
                
                for_slice_slot = for_slices[frame_id]
                
                for_slice_slot[line_number] = for_slice_slot.get(line_number, -1) + 1
            
            if (
                line_number == _dump_line
                and
                occurrence >= _dump_occurrence
            ):
                if __debug__:
                    print(f"{f'  DUMPING at line {line_number} ':-^50}")

                call_stack = []
                
                for frame in walk_frames_to_root(frame):
                    
                    _frame_id = id(frame)
                    
                    new_entry = (frame.f_lineno, dict(frame.f_locals))
                    
                    block_calls = block_stack.get(_frame_id, [])
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
                
                with open(_snapshot, 'wb') as file:
                    dill_dump((
                        call_stack,
                        _for_slices,
                        raise_exceptions,
                        _file
                    ), file)
                
                _exit(0)
        
        case 'call':
            frame_id = id(frame)
            
            for_slices[frame_id] = {}
            
            if line_number in _generators:
                print(f'GEN CALL {line_number}')
                gen_ids.add(frame_id)
                generators[frame.f_back.f_lineno] = frame_id
            
            return trace_function
        
        case 'return':
            if (frame_id := id(frame)) in gen_ids:
                print(f'GEN RET {line_number}')
                _block_stack = block_stack.setdefault(frame_id, [])
                _block_stack.append((line_number, dict(frame.f_locals)))
        
        case 'exception':
            exc_type, exc_value, exc_traceback = arg
            
            raise_exceptions[line_number] = exc_value # BUG use if(frame) as well!
            
            _block_stack = block_stack.setdefault(id(frame), [])
            _block_stack.append((line_number, dict(frame.f_locals)))
            
            if __debug__:
                print(f"{exc_type.__name__}" + f": {exc_value}" if str(exc_value) else "")


def main(file: Path, dump_line: int, dump_occurrence: int, snapshot: Path) -> None:
    global _triggers, _dump_line, _dump_occurrence, _snapshot, _file, _generators, TRACING_OVERHEAD
    
    try:
        source_code = file.read_text()
    except UnicodeDecodeError:
        raise RuntimeError('invalid file') from None
    
    if not dump_line in range(len(source_code.splitlines()) + 1):
        raise ValueError('dump_line is out of range')

    _triggers, _generators = parse_triggers(source_code)
    
    _dump_line, _dump_occurrence, _snapshot, _file = dump_line, dump_occurrence, snapshot, file
    
    tracer = yield_overhead_then_trace(file, source_code, trace_function)
    TRACING_OVERHEAD = next(tracer)
    next(tracer)
    
    print("\033[31m" + 'NERVER DUMPED' + "\033[0m")
    exit(1)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    
    arg_parser.add_argument("script_path", type=lambda path: Path(path).resolve())
    arg_parser.add_argument("dump_line", type=int)
    arg_parser.add_argument("dump_occurrence", type=int, nargs="?", default=1)
    arg_parser.add_argument(
        "snapshot_path",
        type=lambda path: Path(__file__).resolve().parent / path,
        nargs="?",
        default='snapshot'
    )
    
    args = list(vars(arg_parser.parse_args()).values())

    main(*args)