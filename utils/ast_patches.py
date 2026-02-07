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

def code_to_tree(source_code: str) -> ast.AST:
    return ast.parse(source_code)

def tree_to_code(tree: ast.AST) -> str:
    return ast.unparse(tree)


class PreDumpTransformer(ast.NodeTransformer):
    def visit_For(self, node):
        node = self.generic_visit(node)

        node.iter = ast.NamedExpr(
            target=ast.Name(id=f"line_{node.lineno}", ctx=ast.Store()),
            value=node.iter
        )

        return node

    def visit_With(self, node):
        node = self.generic_visit(node)

        for i, item in enumerate(node.items):
            item.context_expr = ast.NamedExpr(
                target=ast.Name(
                    id=f"line_{node.lineno}_{i}",
                    ctx=ast.Store()
                ),
                value=item.context_expr
            )

        return node

def apply_pre_dump_patches(tree: ast.AST) -> ast.AST:
    tree = PreDumpTransformer().visit(tree)
    ast.fix_missing_locations(tree)
    return tree


class TransformAST(ast.NodeTransformer):
    def __init__(self, for_slices, raise_exceptions, code_block_parts):
        self.for_slices = for_slices
        self.raise_exceptions = raise_exceptions
        self.code_block_parts = code_block_parts

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

        if (_id := f"line_{node.lineno}") in self.code_block_parts:
            node.iter = ast.Name(id=_id, ctx=ast.Load())

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

    def visit_With(self, node):
        if raised := self.maybe_raise(node):
            return raised

        self.generic_visit(node)

        for i, item in enumerate(node.items):
            
            if (_id := f"line_{node.lineno}_{i}") in self.code_block_parts:
                item.context_expr = ast.Name(
                    id=_id,
                    ctx=ast.Load()
                )

        return node

    def generic_visit(self, node):
        if raised := self.maybe_raise(node):
            return raised
        return super().generic_visit(node)

def apply_restore_patches(
        tree: ast.AST,
        for_slices: dict[int, int],
        raise_exceptions: dict[int, Exception],
        code_block_parts: set[str]
    ) -> ast.AST:
     
    tree = TransformAST(for_slices, raise_exceptions, code_block_parts).visit(tree)
    ast.fix_missing_locations(tree)
    
    return tree
