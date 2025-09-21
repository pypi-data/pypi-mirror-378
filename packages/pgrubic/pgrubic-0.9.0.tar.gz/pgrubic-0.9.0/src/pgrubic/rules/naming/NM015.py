"""Checker for timestamp columns without defined suffix, by default `_at`."""

from pglast import ast, visitors

from pgrubic.core import linter


class TimestampColumnWithoutSuffix(linter.BaseChecker):
    """## **What it does**
    Checks that timestamp columns are suffixed with the defined suffix, by default `_at`.

    ## **Why not?**
    Adding `_at` to a timestamp column name makes it clear that the value represents the
    time when something happened. For example, `created_at` indicates the time when a
    record was created, and `updated_at` indicates the time when a record was last
    updated.

    Timestamp columns could easily be confused with other types of data if not clearly
    named. For example, a column named created might be unclear — does it represent a
    boolean flag, a date, or something else? `created_at` removes this ambiguity by
    specifying that it's a timestamp.

    ## **When should you?**
    Almost Never.

    ## **Use instead:**
    Add the defined suffix or the default `_at` to to the timestamp column name.

    ## **Configuration**
    `timestamp-column-suffix`: Specify the suffix for timestamp columns.
    """

    is_auto_fixable: bool = True

    def visit_ColumnDef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnDef,
    ) -> None:
        """Visit ColumnDef."""
        if (
            node.typeName.names[-1].sval
            in [
                "timestamptz",
                "timestamp",
            ]
            and node.colname
            and node.colname
            not in [column.name for column in self.config.lint.required_columns]
            and not node.colname.endswith(self.config.lint.timestamp_column_suffix)
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
                    description="Timestamp column name should be suffixed with"
                    f" `{self.config.lint.timestamp_column_suffix}`",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Add the set suffix to the timestamp column",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.ColumnDef) -> None:
        """Fix violation."""
        node.colname += self.config.lint.timestamp_column_suffix
