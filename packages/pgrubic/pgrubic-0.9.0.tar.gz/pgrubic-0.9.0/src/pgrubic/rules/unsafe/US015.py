"""Primary key constraint creating index."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class PrimaryKeyConstraintCreatingIndex(linter.BaseChecker):
    """## **What it does**
    Checks primary key constraint creating index.

    ## **Why not?**
    Primary key constraint is supported by a unique index and a **NOT NULL** constraint
    in the background.
    Adding a primary key constraint to an already populated table will create a
    unique index in non-concurrent mode, scanning and validating that there are no
    violating records in the table. This causes the table to be locked, in which no other
    operations can be performed on the table for the duration of the validation. This will
    cause downtime if the table is concurrently being accessed by other clients.

    ## **When should you?**
    If the table is empty.
    If the table is not empty but is not being concurrently accessed.

    ## **Use instead:**
    1. Create a unique index in concurrent mode:
        **CREATE UNIQUE INDEX CONCURRENTLY .. ON .. (..)**.
    2. In case the primary key column(s) are nullable, create a non-validating check
       constraint: **CHECK (column(s) IS NOT NULL) NOT VALID**.
    3. Validate the constraint.
    4. Set the primary key column(s) as **NOT NULL**.
    5. Drop the constraint.
    6. Add the primary key constraint using the index created in step 1:
        **ALTER TABLE .. ADD CONSTRAINT .. PRIMARY KEY USING INDEX ..**
    """

    def visit_Constraint(
        self,
        ancestors: visitors.Ancestor,
        node: ast.Constraint,
    ) -> None:
        """Visit Constraint."""
        if (
            ancestors.find_nearest(ast.AlterTableCmd)
            and node.contype == enums.ConstrType.CONSTR_PRIMARY
            and not node.indexname
        ):
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Primary key constraint creating index",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Create a unique index in concurrent mode, have the primary key column(s) as NOT NULL, then add the primary key constraint using the index",  # noqa: E501
                ),
            )
