"""Checker for unlogged table."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class CurrentTime(linter.BaseChecker):
    """## **What it does**
    Checks for use of **CURRENT_TIME** function.

    ## **Why not?**
    It returns a value of type **time with time zone**.

    The manual has more to say about this type:

    > The type time with time zone is defined by the SQL standard, but the definition
    > exhibits properties which lead to questionable usefulness. In most cases,
    > a combination of date, time, timestamp without time zone, and
    > timestamp with time zone should provide a complete range of date/time
    > functionality required by any application.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Do not use the CURRENT_TIME function. Use whichever of these is appropriate:

    - CURRENT_TIMESTAMP or now() if you want a timestamp with time zone,
    - LOCALTIMESTAMP if you want a timestamp without time zone,
    - CURRENT_DATE if you want a date,
    - LOCALTIME if you want a time
    """

    is_auto_fixable: bool = True

    def visit_SQLValueFunction(
        self,
        ancestors: visitors.Ancestor,
        node: ast.SQLValueFunction,
    ) -> None:
        """Visit SQLValueFunction."""
        if node.op == enums.SQLValueFunctionOp.SVFOP_CURRENT_TIME:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Prefer functions that return timestamptz"
                    " instead of timetz",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use functions that return timestamptz",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.SQLValueFunction) -> None:
        """Fix violation."""
        node.op = enums.SQLValueFunctionOp.SVFOP_CURRENT_TIMESTAMP
