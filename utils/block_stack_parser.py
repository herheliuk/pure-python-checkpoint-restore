import ast

KINDS = {
    ast.For: "for",
    ast.AsyncFor: "async_for",
    ast.GeneratorExp: "generator",
    ast.ListComp: "generator",
    ast.SetComp: "generator",
    ast.DictComp: "generator",
    ast.Try: "try",
    ast.With: "with",
    ast.AsyncWith: "async_with",
    ast.ExceptHandler: "except",
}

FRAME_NODES = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Lambda,
    ast.GeneratorExp,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
)

KIND_CLASSES = tuple(KINDS)


class Analyzer(ast.NodeVisitor):
    __slots__ = ("for_lines", "block_map", "stack", "in_frame")

    def __init__(self):
        self.for_lines = set()
        self.block_map = {}
        self.stack = []
        self.in_frame = False

    def visit_Module(self, node):
        # Treat the top-level module as a frame
        prev_in_frame = self.in_frame
        self.in_frame = True
        saved_stack = self.stack
        self.stack = []

        for child in node.body:
            self.visit(child)

        # Add remaining stack to block_map
        if self.stack:
            self.block_map[1] = [{line_number: key} for line_number, key in self.stack]

        self.stack = saved_stack
        self.in_frame = prev_in_frame

    def visit(self, node):
        is_frame = isinstance(node, FRAME_NODES)
        prev_in_frame = self.in_frame

        if is_frame:
            self.in_frame = True
            saved_stack = self.stack
            self.stack = []
            super().visit(node)
            self.stack = saved_stack
            self.in_frame = prev_in_frame
            return

        if not self.in_frame:
            super().visit(node)
            return

        lineno = getattr(node, "lineno", None)
        if lineno and self.stack and lineno != self.stack[-1][0]:
            self.block_map[lineno] = [{line_number: key} for line_number, key in self.stack]

        kind = None
        for _class in KIND_CLASSES:
            if isinstance(node, _class):
                kind = KINDS[_class]
                break

        if kind:
            if kind in ("for", "async_for"):
                self.for_lines.add(node.lineno)
            self.stack.append((node.lineno, kind))
            super().visit(node)
            self.stack.pop()
            return

        super().visit(node)


def parse_python_file(source):
    tree = ast.parse(source)
    analyzer = Analyzer()
    analyzer.visit(tree)
    return analyzer.for_lines, analyzer.block_map


if __name__ == "__main__":
    from sys import argv
    import json
    
    file_path = argv[1] if len(argv) == 2 else __file__

    with open(file_path, encoding="utf8") as f:
        source = f.read()

    for_lines, block_map = parse_python_file(source)

    print(for_lines, end="\n\n")
    print(json.dumps(block_map, indent=4))
