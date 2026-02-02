#!/usr/bin/env python3

from ast import AST
from pathlib import Path

from utils.ast_functions import find_imports
from utils.context_managers import use_dir, use_trace

def exec_under_trace(file: Path, source: str | AST, trace_function: function):
    """faking"""
    
    paths_to_trace = { str(path) for path in find_imports(file) }
    
    compiled = compile(
        source=source,
        filename=file,
        mode='exec',
        dont_inherit=True
    )
    
    exec_globals = {
        '__name__': '__main__',
        '__file__': str(file)
    }
    
    def inner_trace_function(frame, event, arg):
        if frame.f_code.co_filename in paths_to_trace:
            return trace_function(frame, event, arg)
    
    with use_dir(file.parent), use_trace(inner_trace_function):
        try:
            exec(
                compiled,
                globals=exec_globals,
                locals=None
            )
        except KeyboardInterrupt:
            exit(1)