#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from utils.block_stack_parser import parse_python_file
from utils.stack import get_frame_stack

from sys import argv, exit
from pathlib import Path

from dill import (
    dump as dill_dump,
    dumps as dill_dumps
)

for_counters: dict[int, int] = {}

def main(debug_script_path: Path, dump_line: int):
    global for_lines, block_map
    paths_to_trace = find_python_imports(debug_script_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    if True:
        def trace_function(frame, event, arg):
            global for_counters
            str_code_filepath = frame.f_code.co_filename
            if str_code_filepath not in str_paths_to_trace: return

            line_number = frame.f_lineno

            print(f"{f'  {event} {line_number} ':-^50}")
            
            match event:
                case 'line':
                    if line_number in for_lines:
                        if not line_number in for_counters:
                            for_counters[line_number] = 1
                        else:
                            for_counters[line_number] += 1
                    
                    if line_number == dump_line:
                        
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
                    
                    print(f'{exc_type.__name__}: {exc_value}')
                    import json
                    print(json.dumps(block_map.get(line_number), indent=4))
        
        source_code = debug_script_path.read_text()
        
        for_lines, block_map = parse_python_file(source=source_code)
        
        import json
        print(json.dumps(block_map, indent=4))
        
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
