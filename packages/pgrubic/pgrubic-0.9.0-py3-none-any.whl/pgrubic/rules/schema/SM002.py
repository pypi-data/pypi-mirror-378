"""Checker for usage of disallowed schemas."""

from pglast import ast, visitors

from pgrubic.core import config, linter


class DisallowedSchema(linter.BaseChecker):
    """## **What it does**
    Checks for usage of disallowed schemas.

    ## **Why not?**
    If a schema has been included in the disallowed_schemas config, it is not allowed.

    ## **When should you?**
    Do you really want to use a disallowed schema?

    ## **Use instead:**
    Allowed schemas.

    ## **Configuration**
    `disallowed-schemas`: List of disallowed schemas.
    """

    is_auto_fixable: bool = True

    help: str = "Do not use disallowed schema"

    def visit_RangeVar(
        self,
        ancestors: visitors.Ancestor,
        node: ast.RangeVar,
    ) -> None:
        """Visit RangeVar."""
        # We are only interested in object creation
        if isinstance(
            abs(ancestors).node,
            ast.CreateStmt
            | ast.ViewStmt
            | ast.CompositeTypeStmt
            | ast.CreateSeqStmt
            | ast.IntoClause,
        ):
            for schema in self.config.lint.disallowed_schemas:
                if node.schemaname == schema.name:
                    self.violations.add(
                        linter.Violation(
                            rule_code=self.code,
                            rule_name=self.name,
                            rule_category=self.category,
                            line_number=self.line_number,
                            column_offset=self.column_offset,
                            line=self.line,
                            statement_location=self.statement_location,
                            description=f"Schema '{node.schemaname}' is disallowed in"
                            f" config with reason: '{schema.reason}'"
                            f", use '{schema.use_instead}' instead",
                            is_auto_fixable=self.is_auto_fixable,
                            is_fix_enabled=self.is_fix_enabled,
                            help=self.help,
                        ),
                    )

                    self._fix_range_var(node, schema)

    def _fix_range_var(
        self,
        node: ast.RangeVar,
        schema: config.DisallowedSchema,
    ) -> None:
        """Fix violation."""
        node.schemaname = schema.use_instead

    def visit_CreateEnumStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.CreateEnumStmt,
    ) -> None:
        """Visit CreateEnumStmt."""
        schema_name: str | None = (
            node.typeName[0].sval if len(node.typeName) > 1 else None
        )

        for schema in self.config.lint.disallowed_schemas:
            if schema_name == schema.name:
                self.violations.add(
                    linter.Violation(
                        rule_code=self.code,
                        rule_name=self.name,
                        rule_category=self.category,
                        line_number=self.line_number,
                        column_offset=self.column_offset,
                        line=self.line,
                        statement_location=self.statement_location,
                        description=f"Schema '{schema_name}' is disallowed in"
                        f" config with reason: '{schema.reason}'"
                        f", use '{schema.use_instead}' instead",
                        is_auto_fixable=self.is_auto_fixable,
                        is_fix_enabled=self.is_fix_enabled,
                        help=self.help,
                    ),
                )

                self._fix_enum(node, schema)

    def _fix_enum(
        self,
        node: ast.CreateEnumStmt,
        schema: config.DisallowedSchema,
    ) -> None:
        """Fix violation."""
        node.typeName[0].sval = schema.use_instead

    def visit_CreateFunctionStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.CreateFunctionStmt,
    ) -> None:
        """Visit CreateFunctionStmt."""
        schema_name: str | None = (
            node.funcname[0].sval if len(node.funcname) > 1 else None
        )

        for schema in self.config.lint.disallowed_schemas:
            if schema_name == schema.name:
                self.violations.add(
                    linter.Violation(
                        rule_code=self.code,
                        rule_name=self.name,
                        rule_category=self.category,
                        line_number=self.line_number,
                        column_offset=self.column_offset,
                        line=self.line,
                        statement_location=self.statement_location,
                        description=f"Schema '{schema_name}' is disallowed in"
                        f" config with reason: '{schema.reason}'"
                        f", use '{schema.use_instead}' instead",
                        is_auto_fixable=self.is_auto_fixable,
                        is_fix_enabled=self.is_fix_enabled,
                        help=self.help,
                    ),
                )

                self._fix_function(node, schema)

    def _fix_function(
        self,
        node: ast.CreateFunctionStmt,
        schema: config.DisallowedSchema,
    ) -> None:
        """Fix violation."""
        node.funcname[0].sval = schema.use_instead
