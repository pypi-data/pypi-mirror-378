"""Checker for missing replace in procedure."""

from pglast import ast, visitors

from pgrubic.core import linter


class MissingReplaceInProcedure(linter.BaseChecker):
    """## **What it does**
    Checks for replace in procedure creation.

    ## **Why not?**
    `CREATE OR REPLACE PROCEDURE` simplifies the process of modifying existing procedures,
    as you don't need to manually drop and recreate them.

    If you drop and then recreate a procedure, the new procedure is not the same entity as
    the old; you will have to drop existing rules, views, triggers, etc. that refer to the
    old procedure. Use CREATE OR REPLACE PROCEDURE to change a procedure definition
    without breaking objects that refer to the procedure. It also maintains data integrity
    and consistency.

    ## **When should you?**
    If you don't need to modify an existing procedure.

    ## **Use instead:**
    CREATE OR REPLACE PROCEDURE.
    """

    is_auto_fixable: bool = True

    def visit_CreateFunctionStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.CreateFunctionStmt,
    ) -> None:
        """Visit CreateFunctionStmt."""
        if not node.replace and node.is_procedure:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Prefer create or replace for procedure",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use create or replace",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.CreateFunctionStmt) -> None:
        """Fix violation."""
        node.replace = True
