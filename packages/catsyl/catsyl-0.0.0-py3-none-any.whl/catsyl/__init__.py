"""
Catsyl
======

A reference utility for categorical syllogisms.

"""

from . import syllogisms
from .syllogisms import (
    Form,
    Logic,
    Proposition,
    Syllogism,
    Term,
    VALID_SYLLOGISTIC_FORMS
)


__all__ = [
    # ─── modules ──────────────────────────────────────────────────────────────────────
    #
    "syllogisms",

    # ─── classes ──────────────────────────────────────────────────────────────────────
    #
    "Form",
    "Logic",
    "Proposition",
    "Syllogism",
    "Term",

    # : constants
    #
    VALID_SYLLOGISTIC_FORMS
]
