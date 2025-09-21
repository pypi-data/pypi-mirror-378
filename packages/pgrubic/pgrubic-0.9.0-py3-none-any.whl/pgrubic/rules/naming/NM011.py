"""Checker for keywords used as identifiers."""

from pglast import keywords

from pgrubic.core import linter
from pgrubic.rules.naming import CheckIdentifier


class KeywordIdentifier(CheckIdentifier):
    """## **What it does**
    Checks for keywords used as identifiers.

    ## **Why not?**
    According to the standard, reserved key words are the only real key words; they are
    never allowed as identifiers. Non-reserved key words only have a special meaning in
    particular contexts and can be used as identifiers in other contexts.

    PostgreSQL won't allow reserved keywords as identifiers without double quotes.
    This means that if you use reserved keywords as identifiers, you have to always double
    quote them. That is annoying enough by hand and error-prone.

    Eventhough, non-reserved keywords can be used as identifiers in certain contexts,
    it can be confusing and ambiguious. Also, there is nothing stopping non-reserved
    keywords from becoming reserved keywords in the future. So, it is best to avoid them
    altogether.

    ## **When should you?**
    Never.

    ## **Use instead:**
    Choose a name that is not a keyword.
    """

    def _check_identifier(
        self,
        identifier: str,
        line_number: int,
        column_offset: int,
        line: str,
        statement_location: int,
    ) -> None:
        """Check for keywords used as identifiers."""
        full_keywords: set[str] = (
            set(keywords.RESERVED_KEYWORDS)
            .union(
                set(keywords.UNRESERVED_KEYWORDS),
            )
            .union(keywords.COL_NAME_KEYWORDS)
            .union(keywords.TYPE_FUNC_NAME_KEYWORDS)
        )

        if identifier and identifier.strip().lower() in full_keywords:
            self.violations.add(
                linter.Violation(
                    rule_code=self.code,
                    rule_name=self.name,
                    rule_category=self.category,
                    line_number=line_number,
                    column_offset=column_offset,
                    line=line,
                    statement_location=statement_location,
                    description=f"Keyword `{identifier}` used as an identifier",
                    is_auto_fixable=self.is_auto_fixable,
                    is_fix_enabled=self.is_fix_enabled,
                    help="Choose a name that is not a keyword",
                ),
            )
