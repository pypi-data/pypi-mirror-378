"""Checker for mismatch column in data type change."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class MismatchColumnInDataTypeChange(linter.BaseChecker):
    """## **What it does**
    Checks for mismatch column in data type change.

    ## **Why not?**
    For certain column data type changes, a **USING** clause must be provided if there is
    no implicit or assignment cast from old to new type.
    Logically, the expression in the USING should reference the original column otherwise
    it is most likely a mistake.

    ## **When should you?**
    Almost never. When you are sure that the expression in the USING is indeed correct.

    ## **Use instead:**
    The right column in the USING clause.
    """

    def visit_ColumnRef(
        self,
        ancestors: visitors.Ancestor,
        node: ast.ColumnRef,
    ) -> None:
        """Visit ColumnRef."""
        alter_table_cmd: visitors.Ancestor = ancestors.find_nearest(ast.AlterTableCmd)

        if (
            alter_table_cmd
            and alter_table_cmd.node.subtype == enums.AlterTableType.AT_AlterColumnType
            and alter_table_cmd.node.name != node.fields[-1].sval
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
                    description=f"Column `{alter_table_cmd.node.name}` in data type"
                    f" change does not match column `{node.fields[-1].sval}`"
                    " in USING clause",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use the right column in the USING clause",
                ),
            )
