"""Checker for UPDATE without a WHERE clause."""

from pglast import ast, visitors

from pgrubic.core import linter


class UpdateWithoutWhereClause(linter.BaseChecker):
    """## **What it does**
    Checks for **UPDATE** without a **WHERE** clause.

    ## **Why not?**
    Executing an **UPDATE** line without a **WHERE** clause will update all the rows
    in the table which is most likely an accidental mistake and not what you want.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Add necessary **WHERE** clause.
    """

    def visit_UpdateStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.UpdateStmt,
    ) -> None:
        """Visit UpdateStmt."""
        if not node.whereClause:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Found UPDATE without a WHERE clause",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Add WHERE clause",
                ),
            )
