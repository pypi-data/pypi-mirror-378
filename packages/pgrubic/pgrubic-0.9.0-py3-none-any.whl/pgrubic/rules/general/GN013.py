"""Checker for existence of not null constraint on required columns."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class NullableRequiredColumn(linter.BaseChecker):
    """## **What it does**
    Checks for existence of not null constraint on required columns.

    ## **Why not?**
    If a column has been specified as required then it should not be nullable.
    Having a required column as nullable is an anti-pattern and should be avoided.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Set the required column as **Not Null**.

    ## **Configuration**
    `required-columns`: List of required columns along with their data types.
    """

    is_auto_fixable: bool = True

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        for column in self.config.lint.required_columns:
            if node.colname == column.name:
                is_not_null = bool(
                    (
                        [
                            constraint
                            for constraint in node.constraints
                            if constraint.contype == enums.ConstrType.CONSTR_NOTNULL
                        ]
                        if node.constraints is not None
                        else []
                    ),
                )

                if not is_not_null:
                    self.violations.add(
                        linter.Violation(
                            rule_code=self.code,
                            rule_name=self.name,
                            rule_category=self.category,
                            line_number=self.line_number,
                            column_offset=self.column_offset,
                            line=self.line,
                            statement_location=self.statement_location,
                            description=f"Column `{node.colname}` is marked as required"
                            " in config",
                            is_auto_fixable=self.is_auto_fixable,
                            is_fix_enabled=self.is_fix_enabled,
                            help="Set the required column as Not Null",
                        ),
                    )

                    self._fix(node)

    def _fix(self, node: ast.ColumnDef) -> None:
        """Fix violation."""
        node.constraints = (
            *(node.constraints or []),
            ast.Constraint(
                contype=enums.ConstrType.CONSTR_NOTNULL,
            ),
        )
