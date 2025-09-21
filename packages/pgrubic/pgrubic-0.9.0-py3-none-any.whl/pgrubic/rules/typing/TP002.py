"""Checker for time with time zone."""

from pglast import ast, visitors

from pgrubic.core import linter


class TimeWithTimeZone(linter.BaseChecker):
    """## **What it does**
    Checks for usage of time with time zone.

    ## **Why not?**
    Even the manual tells you it is only implemented for SQL compliance:

    > The type time with time zone is defined by the SQL standard, but the definition
    > exhibits properties which lead to questionable usefulness. In most cases,
    > a combination of date, time, timestamp without time zone, and
    > timestamp with time zone should provide a complete range of date/time
    > functionality required by any application.

    ## **When should you?**
    Never.

    ## **Use instead:**
    timestamptz (also known as timestamp with time zone).
    """

    is_auto_fixable: bool = True

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        if node.typeName.names[-1].sval == "timetz":
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Prefer timestamp with timezone over time with timezone",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use timestamptz",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.ColumnDef) -> None:
        """Fix violation."""
        node.typeName = ast.TypeName(
            names=(
                {
                    "@": "String",
                    "sval": "timestamptz",
                },
            ),
        )
