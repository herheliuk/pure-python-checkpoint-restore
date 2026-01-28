import ast
import sys

class LineNodePrinter(ast.NodeVisitor):
    def generic_visit(self, node):
        if hasattr(node, "lineno"):
            print()
            print(node.lineno)
            print(ast.dump(node, indent=4))
        super().generic_visit(node)

def main():
    if len(sys.argv) != 2:
        print("Usage: python map_ast_lines.py <script.py>")
        return
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    LineNodePrinter().visit(tree)

if __name__ == "__main__":
    main()
