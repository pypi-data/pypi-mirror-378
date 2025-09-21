"""Checker for identifiers prefix with pg_."""

from pgrubic.core import linter
from pgrubic.rules.naming import CheckIdentifier


class PgPrefixIdentifier(CheckIdentifier):
    """## **What it does**
    Checks for identifiers prefix with **pg_**.

    ## **Why not?**
    From the documentation:

    Schema names beginning with **pg_** are reserved for system purposes and cannot be
    created by users.

    Since system table names begin with **pg_**, it is best to avoid such names to ensure
    that you won't suffer a conflict if some future version defines a system table named
    the same as your table. (With the default search path, an unqualified reference to
    your table name would then be resolved as the system table instead.)
    System tables will continue to follow the convention of having names beginning with
    **pg_**, so that they will not conflict with unqualified user-table names so long as
    users avoid the **pg_** prefix.

    Same thing applies to other objects such as functions, views, sequences etc.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Remove prefix **pg_** from identifier.
    """

    def _check_identifier(
        self,
        identifier: str,
        line_number: int,
        column_offset: int,
        line: str,
        statement_location: int,
    ) -> None:
        """Checks for identifiers prefix with pg_."""
        if identifier and identifier.strip().startswith("pg_"):
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=line_number,
                    column_offset=column_offset,
                    line=line,
                    statement_location=statement_location,
                    description="Identifier should not use prefix `pg_`",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Remove prefix `pg_` from identifier",
                ),
            )
