import ast

TRIGGERS = (
    ast.For, ast.AsyncFor, ast.Try,
    ast.With, ast.AsyncWith, ast.ExceptHandler
)

SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef)

def parse_triggers(source: str) -> dict[int, tuple[str, int]]:
    tree = ast.parse(source)
    blocks = {}

    def walk(node, depth):
        if isinstance(node, SCOPES):
            depth = 0

        if isinstance(node, ast.Try):
            blocks[node.lineno] = ("Try", depth)

            for child in node.body:
                walk(child, depth + 1)

            for handler in node.handlers:
                blocks[handler.lineno] = ("ExceptHandler", depth)
                for child in handler.body:
                    walk(child, depth + 1)

            for child in node.finalbody:
                walk(child, depth + 1)

            return

        if isinstance(node, TRIGGERS):
            blocks[node.lineno] = (type(node).__name__, depth)
            depth += 1

        for child in ast.iter_child_nodes(node):
            walk(child, depth)

    walk(tree, 0)
    return blocks
