import ast

SAVE_LOCALS_TRIGGERS = {
    ast.For: "for",
    ast.AsyncFor: "async_for",
    ast.Try: "try",
    ast.With: "with",
    ast.AsyncWith: "async_with",
    ast.ExceptHandler: "except",
    ast.GeneratorExp: "generator",
    ast.ListComp: "generator",
    ast.SetComp: "generator",
    ast.DictComp: "generator",
}

TRIGGERS_TUPLE = tuple(SAVE_LOCALS_TRIGGERS)

class Analyzer(ast.NodeVisitor):
    __slots__ = ("blocks",)

    def __init__(self):
        self.blocks = {}

    def visit(self, node):
        lineno = getattr(node, "lineno", None)

        if lineno is not None:
            for _class in TRIGGERS_TUPLE:
                if isinstance(node, _class):
                    self.blocks[lineno] = SAVE_LOCALS_TRIGGERS[_class]
                    break

        super().visit(node)

def parse_python_file(source):
    tree = ast.parse(source)
    analyzer = Analyzer()
    analyzer.visit(tree)
    return analyzer.blocks

if __name__ == "__main__":
    from sys import argv
    import json

    file_path = argv[1] if len(argv) == 2 else __file__

    with open(file_path, encoding="utf8") as f:
        source = f.read()

    triggers_map = parse_python_file(source)
    print(json.dumps(triggers_map, indent=4))
    