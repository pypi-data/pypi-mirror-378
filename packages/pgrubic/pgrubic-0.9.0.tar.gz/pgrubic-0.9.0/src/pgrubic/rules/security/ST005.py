"""Checker for non-temp schema in search path of security definer functions."""

import typing

from pglast import ast, enums as pglast_enums, visitors

from pgrubic.core import enums, linter


class SecurityDefinerFunctionNonTempSchema(linter.BaseChecker):
    """## **What it does**
    Checks that a security definer function has non-temporary schema in the
    search path.

    ## **Why not?**
    Because a **SECURITY DEFINER** function is executed with the privileges of the user
    that owns it, care is needed to ensure that the function cannot be misused.
    For security, **search_path** should be set to exclude any schemas writable by
    untrusted users. This prevents malicious users from creating objects (e.g., tables,
    functions, and operators) that mask objects intended to be used by the function.
    A secure arrangement can be obtained by forcing the temporary schema to be searched
    last. To do this, write **pg_temp** as the last entry in search_path.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Include non-temporary schema in the **search_path** of a SECURITY
    DEFINER functions.
    """

    is_auto_fixable = True

    def visit_CreateFunctionStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.CreateFunctionStmt,
    ) -> None:
        """Visit a CreateFunctionStmt."""
        is_security_definer = False
        has_explicit_search_path = False
        has_non_temp_schema = False

        for option in typing.cast(tuple[ast.DefElem], node.options):
            name = option.defname

            if name == enums.FunctionOption.SECURITY and option.arg.boolval:
                is_security_definer = True

            if (
                name == enums.FunctionOption.SET
                and isinstance(option.arg, ast.VariableSetStmt)
                and option.arg.name == "search_path"
                and option.arg.kind == pglast_enums.VariableSetKind.VAR_SET_VALUE
            ):
                has_explicit_search_path = True

                if option.arg.args and any(
                    schema.val.sval != "pg_temp"
                    for schema in typing.cast(tuple[ast.A_Const], option.arg.args)
                ):
                    has_non_temp_schema = True

        if is_security_definer and has_explicit_search_path and not has_non_temp_schema:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Security definer function should have non-temp schema in the search path",  # noqa: E501
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Include non-temp schema in the search path",
                ),
            )

            self._fix(node)

    def _fix(self, node: ast.CreateFunctionStmt) -> None:
        """Fix violation."""
        for option in typing.cast(tuple[ast.DefElem], node.options):
            if (
                option.defname == enums.FunctionOption.SET
                and isinstance(option.arg, ast.VariableSetStmt)
                and option.arg.name == "search_path"
            ):
                option.arg.args = (
                    ast.A_Const(isnull=False, val=ast.String(sval="")),
                    ast.A_Const(isnull=False, val=ast.String(sval="pg_temp")),
                )
