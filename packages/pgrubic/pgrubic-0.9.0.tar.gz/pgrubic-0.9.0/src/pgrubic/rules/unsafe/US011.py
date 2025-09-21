"""Checker for new not-null column with volatile default."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class NewNotNullColumnWithVolatileDefault(linter.BaseChecker):
    """## **What it does**
    Checks new not-null column with volatile default.

    ## **Why not?**
    Adding a new column with **NOT NULL** constraint and a volatile default to an already
    populated table will have to backfill the newly added column with the default, causing
    the table to be locked, in which no other operations can be performed on the table for
    the duration of the backfill. This will cause downtime if the table is concurrently
    being accessed by other clients.

    ## **When should you?**
    If the table is empty.
    If the table is not empty but is not being concurrently accessed.

    ## **Use instead:**
    1. Create the new column, nullable.
    2. Set the default value for the newly created column.
    3. Backfill the newly created column for all existing rows.
    4. Create a check constraint: **CHECK (column IS NOT NULL) NOT VALID**.
    5. Validate the constraint.
    6. Set the column as NOT NULL.
    7. Drop the check constraint.
    """

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        if ancestors.find_nearest(ast.AlterTableCmd) and node.constraints:
            is_not_null = False
            has_volatile_default = False

            constraints: tuple[ast.Constraint] = node.constraints

            for constraint in constraints:
                if constraint.contype == enums.ConstrType.CONSTR_NOTNULL:
                    is_not_null = True

                if (
                    constraint.contype == enums.ConstrType.CONSTR_DEFAULT
                    and not isinstance(
                        constraint.raw_expr,
                        ast.A_Const,
                    )
                ):
                    has_volatile_default = True

            if is_not_null and has_volatile_default:
                self.violations.add(
                    linter.Violation(
                        rule_code=self.code,
                        rule_name=self.name,
                        rule_category=self.category,
                        line_number=self.line_number,
                        column_offset=self.column_offset,
                        line=self.line,
                        statement_location=self.statement_location,
                        description="New not-null column with volatile default",
                        is_auto_fixable=self.is_auto_fixable,
                        is_fix_enabled=self.is_fix_enabled,
                        help="Split the operation into multiple steps",
                    ),
                )
