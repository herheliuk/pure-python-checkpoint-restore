import ast

def replace_for_with_slice(source_code, target_line, start_index):
    tree = ast.parse(source_code)

    class ForSlicer(ast.NodeTransformer):
        def visit_For(self, node):
            if node.lineno == target_line:
                node.iter = ast.Subscript(
                    value=node.iter,
                    slice=ast.Slice(
                        lower=ast.Constant(value=start_index),
                        upper=None
                    ),
                    ctx=ast.Load()
                )
            return node

    new_tree = ForSlicer().visit(tree)
    return ast.unparse(new_tree)

from sys import argv

file_path = argv[1]
target_line = int(argv[2])
start_index = int(argv[3])

with open(file_path) as f:
    source = f.read()

new_source_code = replace_for_with_slice(source, target_line, start_index)
print(new_source_code)
print()
exec(new_source_code)
