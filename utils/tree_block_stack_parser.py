import ast

SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef)
BLOCKS = SCOPES + (
    ast.For, ast.AsyncFor, ast.Try,
    ast.With, ast.AsyncWith, ast.ExceptHandler
)

class Analyzer:
    __slots__ = ("roots", "stack")

    def __init__(self):
        self.roots = {0: {}}
        self.stack = []

    def walk(self, node):
        if isinstance(node, BLOCKS):
            self.enter_block(node)

        for child in ast.iter_child_nodes(node):
            self.walk(child)

        if isinstance(node, BLOCKS):
            self.stack.pop()

    def enter_block(self, node):
        lineno = node.lineno
        body = {}

        if isinstance(node, SCOPES):
            self.roots[lineno] = body
        elif self.stack:
            self.stack[-1][lineno] = body
        else:
            self.roots[0][lineno] = body

        self.stack.append(body)

def parse_triggers(source: str) -> dict[dict]:
    tree = ast.parse(source)
    analyzer = Analyzer()
    analyzer.walk(tree)
    return analyzer.roots

if __name__ == "__main__":
    from sys import argv
    from json import dumps as json_dumps

    path = argv[1] if len(argv) == 2 else __file__

    with open(path, encoding="utf8") as file:
        source_code = file.read()
        
    triggers = parse_triggers(source=source_code)

    print(json_dumps(triggers, indent=4))
