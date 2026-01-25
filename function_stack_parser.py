import ast
from sys import argv

FILE_TO_PARSE = argv[1] if len(argv) == 2 else __file__

def visit(node):
    match node:
        case ast.For():
            yield node.lineno, "for"

        case ast.AsyncFor():
            yield node.lineno, "async_for"

        case ast.GeneratorExp():
            yield node.lineno, "generator"

        case ast.ListComp() | ast.SetComp() | ast.DictComp():
            yield node.lineno, "generator"

    for child in ast.iter_child_nodes(node):
        yield from visit(child)

def parse_python_file(path=None, source=None):
    if not source:
        with open(path, encoding="utf8") as file:
            source = file.read()

    tree = ast.parse(source)

    lines = []
    mapping = {}

    for lineno, kind in visit(tree):
        if lineno not in mapping:
            lines.append(lineno)
            mapping[lineno] = kind

    return lines, mapping

if __name__ == "__main__":
    lines, mapping = parse_python_file(FILE_TO_PARSE)
    print(lines)
    print(mapping)
