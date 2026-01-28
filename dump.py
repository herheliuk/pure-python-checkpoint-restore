#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from utils.triggers_parser import parse_triggers
from utils.stack import (
    walk_stack_backwards,
    get_frame_stack
)

from sys import argv
from os import _exit as exit
from pathlib import Path

from dis import (
    opname as dis_opname
)

from dill import (
    dump as dill_dump,
    dumps as dill_dumps
)

for_counters: dict[int, int] = {}

for_rewrites = {}
block_stack = {}
raise_rewrites = {}

line_occurances: dict[int, int] = {}

def main(debug_script_path: Path, dump_line: int, dump_occurance: int = 1):
    global triggers
    paths_to_trace = find_python_imports(debug_script_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    def trace_function(frame, event, arg):
        global for_rewrites, raise_rewrites, block_stack
        
        if frame.f_code.co_filename not in str_paths_to_trace: return

        line_number = frame.f_lineno

        if event != 'opcode':
            print(f"{f'  {event} {line_number} ':-^50}")
        
        match event:
            case 'opcode':
                instruction = frame.f_code.co_code[frame.f_lasti]
                opcode = dis_opname[instruction]
                
                frame_id = id(frame)
                
                match opcode:
                    case 'FOR_ITER':
                        for_rewrites[line_number] += 1

                    case 'GET_ITER':
                        stack = block_stack.setdefault(frame_id, [])
                        stack.append((line_number, dict(frame.f_locals)))

                        for_rewrites[line_number] = -1
                    
                    case 'POP_ITER':
                        frame.f_trace_opcodes = False
                    
            case 'line':
                line_occurances[line_number] = line_occurances.get(line_number, 0) + 1
                
                if code_block := triggers.get(line_number):
                    match code_block:
                        case 'For':
                            frame.f_trace_opcodes = True
                        case _:
                            frame_id = id(frame)
                            
                            stack = block_stack.setdefault(frame_id, [])
                            stack.append((line_number, dict(frame.f_locals)))
                
                if (
                    line_number == dump_line
                    and
                    line_occurances.get(line_number) >= dump_occurance
                ):
                    print(f"{f'  DUMPING at line {line_number} ':-^50}")
                    
                    """for frame in list(get_frame_stack(frame))[2:]:
                        print(frame.f_lineno)
                    
                    exit()"""
                    
                    """real_call_stack = []
                    
                    for frame in list(get_frame_stack(frame))[2:]:
                        real_call_stack.append(frame.f_lineno)"""
                    
                    call_stack = []
                    
                    for frame in list(get_frame_stack(frame))[2:]:
                        block_entries = None
                        if (frame_id := id(frame)) in block_stack:
                            block_entries = block_stack[frame_id]
                            call_stack.extend(block_entries)
                        
                        call_entry = (frame.f_lineno, dict(frame.f_locals))
                        
                        if not block_entries or block_entries[-1] != call_entry:
                            call_stack.append(call_entry)
                    
                    # f'{real_call_stack=}', '\n\n', 
                    print(f'{call_stack=}', '\n\n', f'{for_rewrites=}', '\n\n', f'{block_stack=}', '\n\n', f'{raise_rewrites=}')

                    with open(script_dir / 'snapshot', 'wb') as file:
                        dill_dump((
                            list(reversed(call_stack)),
                            for_rewrites,
                            block_stack,
                            raise_rewrites
                        ), file)
                    
                    exit(0)
            
            case 'call':
                """last_call_line = line_number
                try:
                    block_body = triggers[line_number]['body']
                    block_end = triggers[line_number]['end']
                except KeyError:
                    block_body = {}
                    block_end = None
                #print(block_body, block_end)"""
                return trace_function
            
            case 'exception':
                exc_type, exc_value, exc_traceback = arg
                to_raise: bytes = dill_dumps(exc_value)
                
                print(f"{exc_type.__name__}" + (f": {exc_value}" if str(exc_value) else ""))
                
                frame_id = id(frame)
                
                try:
                    raise_rewrites[frame_id][line_number] = to_raise
                except:
                    raise_rewrites[frame_id] = {
                        line_number: to_raise
                    }
    
    source_code = debug_script_path.read_text()
    
    triggers = parse_triggers(source=source_code)
    
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

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    
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
    
    print(f'{for_rewrites=}', '\n\n', f'{block_stack=}', '\n\n', f'{raise_rewrites=}')
    
    raise Exception("dump_line was never hit.")
