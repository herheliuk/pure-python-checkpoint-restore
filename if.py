import ast

def replace_if_with_true(source_code, target_line):
    tree = ast.parse(source_code)

    class IfReplacer(ast.NodeTransformer):
        def visit_If(self, node):
            if node.lineno == target_line:
                node.test = ast.Constant(value=True)
            return node

    new_tree = IfReplacer().visit(tree)
    return ast.unparse(new_tree)

from sys import argv

file_path = argv[1]
target_line = int(argv[2])

with open(file_path) as f:
    source = f.read()

new_source_code = replace_if_with_true(source, target_line)
exec(new_source_code)
