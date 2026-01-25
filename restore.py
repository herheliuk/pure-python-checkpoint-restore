#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from sys import argv, exit
from pathlib import Path

import ast

class SliceForLoops(ast.NodeTransformer):
    def __init__(self, for_rewrites):
        self.for_rewrites = for_rewrites

    def visit_For(self, node):
        self.generic_visit(node)

        if node.lineno not in self.for_rewrites:
            return node

        node.iter = ast.Subscript(
            value=node.iter,
            slice=ast.Slice(
                lower=ast.Constant(self.for_rewrites[node.lineno]),
                upper=None,
                step=None
            ),
            ctx=ast.Load()
        )

        return node

from dill import (
    load as dill_load
)

with open('snapshot', 'rb') as file:
    call_stack, for_rewrites, block_stack, raise_rewrites = dill_load(file)

def main(debug_script_path: Path):
    paths_to_trace = find_python_imports(debug_script_path)
    
    str_paths_to_trace = {
        str(path)
        for path in paths_to_trace
    }
    
    if True:
        def trace_function(frame, event, arg):
            str_code_filepath = frame.f_code.co_filename
            if str_code_filepath not in str_paths_to_trace: return
            
            if call_stack:
                match event:
                    case 'line':
                        print(f'FROM {frame.f_lineno}')
                        frame.f_lineno, f_locals = call_stack.pop()
                        for key, value in f_locals.items():
                            frame.f_locals[key] = value
                    case 'call':
                        return trace_function
        
        source_code = debug_script_path.read_text()
        
        tree = ast.parse(source_code)

        tree = SliceForLoops(for_rewrites).visit(tree)
        ast.fix_missing_locations(tree)
        
        compiled = compile(
            source=tree,
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
    debug_script_path = Path(argv[1]).resolve()

    main(debug_script_path)
