"""Checker for integer."""

from pglast import ast, visitors

from pgrubic.core import linter


class Integer(linter.BaseChecker):
    """## **What it does**
    Checks for usage of integer.

    ## **Why not?**
    Integer can store values up to 2.147 Billion which can lead to integer overflow once
    the max value is reached. The fire drill when you run out of integers is not cheap.

    ## **When should you?**
    Tables that store limited lookup options.

    ## **Use instead:**
    bigint.
    """

    is_auto_fixable: bool = True

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        if node.typeName.names[-1].sval == "int4":
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Prefer bigint over integer",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use bigint",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.ColumnDef) -> None:
        """Fix violation."""
        node.typeName = ast.TypeName(
            names=(
                {
                    "@": "String",
                    "sval": "bigint",
                },
            ),
        )
