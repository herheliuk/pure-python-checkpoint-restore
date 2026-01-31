import ast

TRIGGERS = (
    ast.For, ast.AsyncFor, ast.Try,
    ast.With, ast.AsyncWith, ast.ExceptHandler
)

def parse_triggers(source: str) -> dict[dict]:
    tree = ast.parse(source)

    blocks = {}

    for node in ast.walk(tree):
        if isinstance(node, TRIGGERS):
            blocks[node.lineno] = type(node).__name__
    
    return blocks

if __name__ == "__main__":
    from sys import argv
    from json import dumps as json_dumps

    path = argv[1] if len(argv) == 2 else __file__

    with open(path, encoding="utf8") as file:
        source_code = file.read()
        
    triggers = parse_triggers(source=source_code)

    print(json_dumps(triggers, indent=4))
