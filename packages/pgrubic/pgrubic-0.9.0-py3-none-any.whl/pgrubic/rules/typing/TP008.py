"""Checker for json."""

from pglast import ast, visitors

from pgrubic.core import linter


class Json(linter.BaseChecker):
    """## **What it does**
    Checks for usage of json.

    ## **Why not?**
    From the manual:
    > The json and jsonb data types accept almost identical sets of values as input.
    > The major practical difference is one of efficiency. The json data type stores an
    > exact copy of the input text, which processing functions must reparse on each
    > execution; while jsonb data is stored in a decomposed binary format that makes it
    > slightly slower to input due to added conversion overhead, but significantly
    > faster to process, since no reparsing is needed. jsonb also supports indexing,
    > which can be a significant advantage.

    ## **When should you?**
    In general, most applications should prefer to store JSON data as jsonb, unless
    there are quite specialized needs, such as legacy assumptions about ordering of
    object keys.

    ## **Use instead:**
    jsonb.
    """

    is_auto_fixable: bool = True

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        if node.typeName.names[-1].sval == "json":
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Prefer jsonb over json",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use jsonb",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.ColumnDef) -> None:
        """Fix violation."""
        node.typeName = ast.TypeName(
            names=(
                {
                    "@": "String",
                    "sval": "jsonb",
                },
            ),
        )
