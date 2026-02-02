import ast

def exception_to_raise(exception):
    return ast.Raise(
        exc=ast.Call(
            func=ast.Name(id=type(exception).__name__, ctx=ast.Load()),
            args=[ast.Constant(arg) for arg in getattr(exception, "args", [])],
            keywords=[]
        ),
        cause=None
    )
    
    ''' is there any difference ? -> optimise
    ast.Raise(
        exc=ast.Name(id=type(exception).__name__, ctx=ast.Load()),
        cause=None
    )
    '''


class TransformAST(ast.NodeTransformer):
    def __init__(self, for_slices, raise_exceptions):
        self.for_slices = for_slices
        self.raise_exceptions = raise_exceptions

    def maybe_raise(self, node):
        if (
            (line_number := getattr(node, "lineno", None))
            and
            (exception := self.raise_exceptions.get(line_number))
        ):
            raise_node = exception_to_raise(exception)
            
            raise_node.lineno = line_number
            raise_node.col_offset = getattr(node, "col_offset", 0)
            
            return raise_node

    def visit_For(self, node):
        if raised := self.maybe_raise(node):
            return raised

        self.generic_visit(node)

        if _slice := self.for_slices.get(node.lineno):
            node.iter = ast.Subscript(
                value=node.iter,
                slice=ast.Slice(
                    lower=ast.Constant(_slice),
                    upper=None,
                    step=None
                ),
                ctx=ast.Load()
            )

        return node

    def generic_visit(self, node):
        if raised := self.maybe_raise(node):
            return raised
        
        return super().generic_visit(node)


def parse_tree(source_code: str) -> ast.AST:
    return ast.parse(source_code)

def apply_patches(
        tree: ast.AST,
        for_slices: dict[int, int],
        raise_exceptions: dict[int, Exception]
    ) -> ast.AST:
     
    tree = TransformAST(for_slices, raise_exceptions).visit(tree)
    ast.fix_missing_locations(tree)
    
    return tree
