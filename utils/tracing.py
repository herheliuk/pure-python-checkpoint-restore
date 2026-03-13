#!/usr/bin/env python3

from ast import AST
from contextlib import contextmanager
from pathlib import Path
from sys import (
    path as sys_path,
    gettrace,
    settrace,
    _getframe
)
import sys # for sys.argv = ...

from utils.ast_functions import find_imports

@contextmanager
def use_args(filename: str, args: list[str] = None):
    old_argv = sys.argv
    new_argv = [filename]
    if args:
        new_argv.extend(args)
    sys.argv = new_argv
    try:
        yield
    finally:
        sys.argv = old_argv

@contextmanager
def use_path(target_dir: str):
    original_dir = sys_path[0]
    sys_path[0] = target_dir
    try:
        yield
    finally:
        sys_path[0] = original_dir

@contextmanager
def use_trace(trace_function):
    old_trace = gettrace()
    settrace(trace_function)
    try:
        yield
    finally:
        settrace(old_trace)

def yield_overhead_then_trace(file: Path, source: str | AST, trace_function: function, optimisation_level: int, args: list[str] = None):
    filename = str(file)
    
    paths_to_trace = { str(path) for path in find_imports(file) } | { filename }
    
    compiled = compile(
        source=source,
        filename=file,
        mode='exec',
        dont_inherit=True,
        optimize=optimisation_level
    )
    
    exec_globals = {
        '__name__': '__main__',
        '__file__': filename
    }
    
    def temporary_trace_function(frame, event, arg):
        if frame.f_code.co_filename in paths_to_trace:
            return trace_function(frame, event, arg)
    
    with use_trace(temporary_trace_function), use_args(filename, args):
        try:
            frame, overhead = _getframe(), 0
            while frame:
                overhead += 1
                frame = frame.f_back
            
            yield overhead
            
            exec(
                compiled,
                globals=exec_globals,
                locals=None
            )
        except KeyboardInterrupt:
            exit(1)
