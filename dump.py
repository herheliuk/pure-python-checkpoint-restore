#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from utils.code_blocks import parse_triggers
from utils.frame_stack import walk_frames_to_root

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

def main(script_to_debug_path: Path, dump_line: int, dump_occurance: int = 1):
    global triggers
    paths_to_trace = find_python_imports(script_to_debug_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    def trace_function(frame, event, arg):
        global for_rewrites, raise_rewrites, block_stack
        
        if frame.f_code.co_filename not in str_paths_to_trace: return

        line_number = frame.f_lineno

        if event != 'opcode':
            print(f"{f'  {event} {line_number} {line_occurances.get(line_number, 0) + 1} ':-^50}")
        
        match event:
            case 'opcode':
                instruction = frame.f_code.co_code[frame.f_lasti]
                opcode = dis_opname[instruction]
                
                match opcode:
                    case 'FOR_ITER':
                        print(opcode)
                        for_rewrites[line_number] += 1

                    case 'GET_ITER':
                        print(opcode)
                        for_rewrites[line_number] = -1
                    
                    case 'POP_ITER':
                        print(opcode)
                        frame.f_trace_opcodes = False

            case 'line':
                line_occurances[line_number] = line_occurances.get(line_number, 0) + 1
                
                if trigger_data := triggers.get(line_number):
                    code_block, offset = trigger_data
                    
                    stack = block_stack.setdefault(id(frame), [])
                    new_entry = (line_number, dict(frame.f_locals))
                    
                    if offset >= len(stack):
                        stack.append(new_entry)
                    else:
                        stack[offset] = new_entry
                        del stack[offset + 1:]
                    
                    match code_block:
                        case 'For':
                            frame.f_trace_opcodes = True
                
                if (
                    line_number == dump_line
                    and
                    line_occurances.get(line_number) >= dump_occurance
                ):
                    print(f"{f'  DUMPING at line {line_number} ':-^50}")

                    call_stack = []
                    
                    for frame in walk_frames_to_root(frame):
                        
                        new_entry = (frame.f_lineno, dict(frame.f_locals))
                        
                        block_calls = block_stack.get(id(frame), [])
                        block_calls.reverse()
                        
                        if (
                            not block_calls
                            or
                            block_calls[-1] != new_entry
                        ):
                            call_stack.append(new_entry)
                        
                        call_stack.extend(block_calls)

                    del call_stack[-2:]
                    
                    with open(script_dir / 'snapshot', 'wb') as file:
                        dill_dump((
                            call_stack,
                            for_rewrites,
                            block_stack,
                            raise_rewrites
                        ), file)
                    
                    exit(0)
            
            case 'call':
                # Classes BUG solution needed. here?
                return trace_function
            
            case 'exception':
                stack = block_stack.setdefault(id(frame), [])
                stack.append((line_number, dict(frame.f_locals)))
                
                exc_type, exc_value, exc_traceback = arg
                
                print(f"{exc_type.__name__}" + (f": {exc_value}" if str(exc_value) else ""))
                
                to_raise: bytes = dill_dumps(exc_value)
                raise_rewrites[line_number] = to_raise
    
    source_code = script_to_debug_path.read_text()
    
    triggers = parse_triggers(source=source_code)
    
    import json
    print(json.dumps(triggers, indent=4))
    
    if dump_line not in range(len(source_code.splitlines()) + 1):
        print(f'dump_line is out of the range')
    
    compiled = compile(
        source_code,
        filename=script_to_debug_path,
        mode='exec',
        dont_inherit=True
    )
    
    exec_globals = {
        '__name__': '__main__',
        '__file__': str(script_to_debug_path)
    }
    
    with use_dir(script_to_debug_path.parent), use_trace(trace_function):
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
    
    script_to_debug_path = Path(argv[1]).resolve()
    
    try:
        dump_line = int(argv[2])
    except:
        dump_line = 10_000
        
    try:
        dump_occurance = int(argv[3])
    except:
        dump_occurance = 1
        
    main(script_to_debug_path, dump_line, dump_occurance)
    
    print(f'{for_rewrites=}', '\n\n', f'{block_stack=}', '\n\n', f'{raise_rewrites=}')
    
    raise Exception("dump_line was never hit.")
