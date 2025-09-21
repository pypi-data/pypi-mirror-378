"""Checker for usage of select into to create a new table."""

from pglast import ast, enums, visitors

from pgrubic.core import linter


class SelectInto(linter.BaseChecker):
    """## **What it does**
    Checks for usage of select into to create a new table.

    ## **Why not?**
    The SQL standard uses SELECT INTO to represent selecting values into scalar
    variables of a host program, rather than creating a new table.

    The PostgreSQL usage of SELECT INTO to represent table creation is historical.
    Some other SQL implementations also use SELECT INTO in this way (but most SQL
    implementations support CREATE TABLE AS instead). Apart from such compatibility
    considerations, it is best to use CREATE TABLE AS for this purpose in new code.

    ## **When should you?**
    Never.

    ## **Use instead:**
    CREATE TABLE AS.
    """

    is_auto_fixable: bool = True

    def visit_SelectStmt(
        self,
        ancestors: visitors.Ancestor,
        node: ast.SelectStmt,
    ) -> ast.CreateTableAsStmt | None:
        """Visit SelectStmt."""
        if node.intoClause:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=self.line_number,
                    column_offset=self.column_offset,
                    line=self.line,
                    statement_location=self.statement_location,
                    description="Use CREATE TABLE AS instead of SELECT INTO",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Use CREATE TABLE AS",
                ),
            )

            return self._fix(node)

        return None

    def _fix(self, node: ast.SelectStmt) -> ast.CreateTableAsStmt:
        """Fix violation."""
        into_clause = node.intoClause

        # delete into clause
        node.intoClause = None

        return ast.CreateTableAsStmt(
            query=node,
            into=into_clause,
            objtype=enums.ObjectType.OBJECT_TABLE,
        )
