import ast
from sys import argv

FILE_TO_PARSE = argv[1] if len(argv) == 2 else __file__

def add_tag(line_tags, tag):
    if tag not in line_tags:
        line_tags.append(tag)

def mark(node, label):
    for line in range(node.lineno + 1, node.end_lineno + 1):
        yield line, f"{label}:{node.lineno}"

def walk(nodes):
    for node in nodes:
        yield from visit(node)

def visit(node):
    if isinstance(node, ast.ClassDef):
        yield from mark(node, "class")
        yield from walk(node.body)

    elif isinstance(node, ast.FunctionDef):
        yield from mark(node, "function")
        yield from walk(node.body)

    elif isinstance(node, ast.AsyncFunctionDef):
        yield from mark(node, "async_function")
        yield from walk(node.body)

    elif isinstance(node, ast.If):
        yield from mark(node, "if")
        yield from walk(node.body)

        orelse = node.orelse
        prev_lineno = node.lineno
        while orelse:
            first = orelse[0]
            if isinstance(first, ast.If):
                yield from mark(first, "elif")
                yield from walk(first.body)
                prev_lineno = first.lineno
                orelse = first.orelse
            else:
                start_lineno = first.lineno
                end_lineno = orelse[-1].end_lineno
                prev_lineno = orelse[0].lineno - 1
                for line in range(start_lineno, end_lineno + 1):
                    yield line, f"else:{prev_lineno}"
                for n in orelse:
                    yield from visit(n)
                break

    elif isinstance(node, ast.For):
        yield from mark(node, "for")
        yield from walk(node.body)
        yield from walk(node.orelse)

    elif isinstance(node, ast.AsyncFor):
        yield from mark(node, "async_for")
        yield from walk(node.body)
        yield from walk(node.orelse)

    elif isinstance(node, ast.Try):
        yield from mark(node, "try")
        yield from walk(node.body)

        for handler in node.handlers:
            for line, tag in mark(handler, f"except"):
                yield line, tag
            yield from walk(handler.body)

        if node.finalbody:
            finally_lineno = node.finalbody[0].lineno - 1
            for line in range(node.finalbody[0].lineno, node.finalbody[-1].end_lineno + 1):
                yield line, f"finally:{finally_lineno}"
            yield from walk(node.finalbody)

    elif isinstance(node, ast.With):
        yield from mark(node, "with")
        yield from walk(node.body)

    elif isinstance(node, ast.AsyncWith):
        yield from mark(node, "async_with")
        yield from walk(node.body)

    elif hasattr(node, "body"):
        yield from walk(node.body)

def parse_python_file(path = None, source = None):
    if not source:
        with open(path, encoding="utf8") as file:
            source = file.read()
    tree = ast.parse(source)

    line_tags = {}
    for lineno, tag in walk(tree.body):
        line_tags.setdefault(lineno, []).append(tag)

    for lineno in sorted(line_tags):
        yield lineno, line_tags[lineno]

if __name__ == "__main__":
    for lineno, tags in parse_python_file(FILE_TO_PARSE):
        print(f"Line {lineno}: {tags}")
