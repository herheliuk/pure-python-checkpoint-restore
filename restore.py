#!/usr/bin/env python3

from utils.ast_functions import find_python_imports
from utils.context_managers import use_dir, use_trace

from sys import argv, exit
from pathlib import Path

import ast

# ⚠️ spaghetti code ahead! TODO: needs refactoring

def exception_to_ast(exc):
    exc_type = type(exc).__name__
    
    try:
        args = [ast.Constant(arg) for arg in exc.args]
    except Exception:
        args = []

    return ast.Call(
        func=ast.Name(id=exc_type, ctx=ast.Load()),
        args=args,
        keywords=[]
    )

class TransformAST(ast.NodeTransformer):
    def __init__(self, for_rewrites, raise_rewrites):
        self.for_rewrites = for_rewrites
        self.raise_rewrites = raise_rewrites

    def make_raise(self, lineno, col_offset):
        exc_obj = self.raise_rewrites[lineno]
        node = ast.Raise(
            exc=exception_to_ast(exc_obj),
            cause=None
        )
        node.lineno = lineno
        node.col_offset = col_offset
        return node

    def rewrite_body(self, body):
        new_body = []
        for stmt in body:
            if hasattr(stmt, "lineno") and stmt.lineno in self.raise_rewrites:
                new_body.append(self.make_raise(stmt.lineno, getattr(stmt, "col_offset", 0)))
            else:
                new_body.append(self.visit(stmt))
        return new_body

    def visit_For(self, node):
        if node.lineno in self.raise_rewrites:
            return self.make_raise(node.lineno, node.col_offset)

        node.body = self.rewrite_body(node.body)
        if node.orelse:
            node.orelse = self.rewrite_body(node.orelse)

        node.iter = self.visit(node.iter)
        node.target = self.visit(node.target)

        if node.lineno in self.for_rewrites:
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

    def generic_visit(self, node):
        if hasattr(node, "body") and isinstance(node.body, list):
            node.body = self.rewrite_body(node.body)
            return node
        return super().generic_visit(node)

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
                        print(f'{frame.f_lineno}..', end='')
                        frame.f_lineno, f_locals = call_stack.pop()
                        print(f'{frame.f_lineno}')
                        for key, value in f_locals.items():
                            frame.f_locals[key] = value
                    case 'call':
                        return trace_function
        
        source_code = debug_script_path.read_text()
        
        tree = ast.parse(source_code)

        tree = TransformAST(for_rewrites, raise_rewrites).visit(tree)
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
