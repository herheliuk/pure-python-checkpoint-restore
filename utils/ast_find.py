import ast

def parse_triggers(source: str) -> tuple[dict[int, tuple[str, int]], set[int]]:
    tree = ast.parse(source)
    blocks = {}
    generators = set()
    function_stack = []

    def walk(node, depth):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_stack.append(child.lineno)
                walk(child, 0)
                function_stack.pop()
                continue

            match child:
                case ast.Try():
                    blocks[child.lineno] = ("Try", depth)
                    for stmt in child.body:
                        walk(stmt, depth + 1)
                    except_depth = depth + 2
                    for handler in child.handlers:
                        blocks[handler.lineno] = ("ExceptHandler", except_depth)
                        for stmt in handler.body:
                            walk(stmt, except_depth + 1)
                    for stmt in child.finalbody:
                        walk(stmt, depth + 1)

                case (
                    ast.For() | ast.AsyncFor() |
                    ast.While() |
                    ast.With() | ast.AsyncWith()
                ):
                    blocks[child.lineno] = (type(child).__name__, depth)
                    walk(child, depth + 1)

                case ast.Yield() | ast.YieldFrom():
                    generators.add(function_stack[-1])

                case _:
                    walk(child, depth)

    walk(tree, 0)
    return blocks, generators
