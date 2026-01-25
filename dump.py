#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from sys import argv, exit
from pathlib import Path

from dill import (
    dump as dill_dump
)

from types import FrameType
from typing import Iterator

from function_stack_parser import parse_python_file

def get_stack(frame: FrameType) -> Iterator[FrameType]:
    """Yield frames from the root frame to the given frame."""
    stack: list[FrameType] = []
    stack_append = stack.append
    
    while frame:
        stack_append(frame)
        frame = frame.f_back
    
    yield from reversed(stack)

hh = {}

def main(debug_script_path: Path, dump_line: int):
    global lines, mapping
    paths_to_trace = find_python_imports(debug_script_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    if True:
        def trace_function(frame, event, arg):
            global hh
            str_code_filepath = frame.f_code.co_filename
            if str_code_filepath not in str_paths_to_trace: return

            lineno = frame.f_lineno

            print(f"{f'  {event} {lineno} ':-^50}")

            if event == 'line':
                
                if lineno in lines:
                    if not lineno in hh.keys():
                        hh[lineno] = 1
                    else:
                        hh[lineno] += 1
                
                if lineno == dump_line and hh[lineno] == 3:
                    
                    snapshot = []
                    
                    for frame in get_stack(frame):
                        snapshot.append({
                            "lineno": lineno,
                            "locals": dict(frame.f_locals)
                        })
                    
                    with open('snapshot', 'wb') as file:
                        dill_dump((snapshot[2:], hh), file)
                    
                    exit()

            elif event == 'call':
                return trace_function
        
        source_code = debug_script_path.read_text()
        
        lines, mapping = parse_python_file(source=source_code)
        
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
        dump_line = 9999 * 9999
    
    main(debug_script_path, dump_line)
    
    raise Exception("dump_line was never hit.")
