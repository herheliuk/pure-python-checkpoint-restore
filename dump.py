#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from utils.block_stack_parser import parse_python_file
from utils.stack import walk_stack_backwards, get_frame_stack

from sys import argv, exit
from pathlib import Path

from dill import (
    dump as dill_dump,
    dumps as dill_dumps
)

for_counters: dict[int, int] = {}

for_rewrites = {}
block_locals = {}
raise_rewrites = {}

def main(debug_script_path: Path, dump_line: int, iteration: int = 1):
    global triggers
    paths_to_trace = find_python_imports(debug_script_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    if True:
        def trace_function(frame, event, arg):
            global for_rewrites, raise_rewrites, block_locals
            str_code_filepath = frame.f_code.co_filename
            if str_code_filepath not in str_paths_to_trace: return

            line_number = frame.f_lineno

            print(f"{f'  {event} {line_number} ':-^50}")
            
            match event:
                case 'line':
                    if code_block := triggers.get(line_number):
                        frame_id = id(frame)
                        match code_block:
                            case 'for':
                                func_id = id(frame.f_code)
                                try:
                                    for_rewrites[func_id][line_number] += 1
                                except:
                                    for_rewrites[func_id] = {
                                        line_number: 1
                                    }
                            case _:
                                pass
                        try:
                            block_locals[frame_id].append({
                                line_number: len(dict(frame.f_locals))
                            })
                        except:
                            block_locals[frame_id] = [{
                                line_number: len(dict(frame.f_locals))
                            }]
                    
                    if (
                        line_number == dump_line
                    ):
                        print(f"{f'  DUMPING at line {line_number} ':-^50}")
                        
                        """for frame in list(get_frame_stack(frame))[2:]:
                            print(frame.f_lineno)
                        
                        exit()"""
                        
                        call_stack = []
                        
                        for frame in list(get_frame_stack(frame))[2:]:
                            if (frame_id := id(frame)) in block_locals:
                                block_entries = block_locals[frame_id]
                                call_stack.extend(block_entries)
                            
                            if block_entries and block_entries[-1] != (call_entry := {
                                frame.f_lineno: len(dict(frame.f_locals))
                            }):
                                call_stack.append(call_entry)
                            
                        print(f'{call_stack=}', '\n\n', f'{for_rewrites=}', '\n\n', f'{block_locals=}', '\n\n', f'{raise_rewrites=}')
                        
                        exit()
                        snapshot = []
                        
                        for frame in get_frame_stack(frame):
                            snapshot.append({
                                "lineno": line_number,
                                "locals": dict(frame.f_locals)
                            })
                        
                        with open('snapshot', 'wb') as file:
                            dill_dump((snapshot[2:], for_counters, block_map), file)
                        
                        exit()
                
                case 'call':
                    return trace_function
                
                case 'exception':
                    exc_type, exc_value, exc_traceback = arg
                    to_raise: bytes = dill_dumps(exc_value)
                    
                    frame_id = id(frame)
                    
                    try:
                        raise_rewrites[frame_id][line_number] = to_raise
                    except:
                        raise_rewrites[frame_id] = {
                            line_number: to_raise
                        }
        
        source_code = debug_script_path.read_text()
        
        triggers = parse_python_file(source=source_code)
        
        import json
        print(json.dumps(triggers, indent=4))
        
        if dump_line not in range(len(source_code.splitlines()) + 1):
            print(f'dump_line is out of the range')
        
        compiled = compile(
            source_code,
            filename=debug_script_path,
            mode='exec',
            dont_inherit=True
        )
        
        exec_globals = {
            '__name__': '__main__',
            '__file__': str(debug_script_path)
        }
        
        with use_dir(debug_script_path.parent), use_trace(trace_function):
            try:
                exec(
                    compiled,
                    exec_globals,
                    None
                )
            except KeyboardInterrupt:
                print()
                exit(1)

if True:
    debug_script_path = Path(argv[1]).resolve()
    
    try:
        dump_line = int(argv[2])
    except:
        dump_line = 10_000
        
    try:
        iteration = int(argv[3])
    except:
        iteration = 1
        
    main(debug_script_path, dump_line, iteration)
    
    
    print(f'{for_rewrites=}', '\n\n', f'{block_locals=}', '\n\n', f'{raise_rewrites=}')
    
    raise Exception("dump_line was never hit.")
