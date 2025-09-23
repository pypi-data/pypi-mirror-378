"""
Categorical Syllogisms
======================

This module's main exports are the ``Syllogism`` data structure and the
``Logic`` utility framework.

"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
# from os import PathLike
# from pathlib import Path
from typing import Any, Literal, TypeAlias


# ─── constants ──────────────────────────────────────────────────────────────────── ✦ ─
#
VALID_SYLLOGISTIC_FORMS: dict[str, Any] = {
    "AAA-1": "Barbara",
    "EAE-1": "Celarent",
    "AII-1": "Darii",
    "EIO-1": "Ferio",
    "AAI-1": "Barbari",
    "EAO-1": "Celeront",
    "EAE-2": "Cesare",
    "AEE-2": "Camestres",
    "EIO-2": "Festino",
    "AOO-2": "Baroco",
    "EAO-2": "Cesaro",
    "AEO-2": "Camestros",
    "AII-3": "Datisi",
    "IAI-3": "Disamis",
    "EIO-3": "Ferison",
    "OAO-3": "Bocardo",
    "EAO-3": "Felapton",
    "AAI-3": "Darapti",
    "AEE-4": "Calemes",
    "IAI-4": "Dimatis",
    "EIO-4": "Fresison",
    "AEO-4": "Calemos",
    "EAO-4": "Fesapo",
    "AAI-4": "Bamalip",
}


# ─── logger setup ───────────────────────────────────────────────────────────────── ✦ ─
logging.basicConfig(level="INFO", format="%(name)s – %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
logger.debug("Logger setup complete.")


# ─── type aliases ───────────────────────────────────────────────────────────────── ✦ ─
#
Figure: TypeAlias = Literal[1 | 2 | 3 | 4]
Mood: TypeAlias = tuple["Form", "Form", "Form"]


# ─── exceptions ─────────────────────────────────────────────────────────────────── ✦ ─
#
class LogicException(Exception):
    """Base class for Catsyl's logic exceptions."""
    pass


class UndefinedTermException(LogicException):
    """Base class for logic exceptions related to undefined terms."""
    pass


class MajorTermUndefined(UndefinedTermException):
    """
    An exception raised on attempts to access a syllogism's major term
    while it is undefined.

    """
    pass


class MiddleTermUndefined(UndefinedTermException):
    """
    An exception raised on attempts to access a syllogism's middle term
    while it is undefined.

    """
    pass


class MinorTermUndefined(UndefinedTermException):
    """
    An excepion raised on attempts to access a syllogism's minor term
    while it is undefined.

    """
    pass


# ─── data structures ────────────────────────────────────────────────────────────── ✦ ─
#
class Form(Enum):
    A = "universal affirmative"
    E = "universal negative"
    I = "particular affirmative"    # noqa: E741
    O = "particular negative"       # noqa: E741


@dataclass
class Term:
    """A type that represents a term in categorical logic."""
    content: str | None = ""


@dataclass
class Proposition:
    """A type that represents a categorical proposition."""
    antecedent: Term
    consequent: Term
    form: Form
    conclusive: bool = False


@dataclass
class Syllogism:
    major_premise: Proposition
    minor_premise: Proposition
    conclusion: Proposition


# ─── main logical interface ─────────────────────────────────────────────────────── ✦ ─
#
class Logic:
    """A reference utility interface for categorical logic."""

    def __init__(self) -> None:
        """Constructor.

        Parameters
        ----------
        ...

        """
        pass


    def __repr__(self) -> str:
        """Get a code literal representation of this ``Logic`` instance."""

        return "Logic()"


    @staticmethod
    def isvalid(syllogism: str) -> bool:
        """
        Get a boolean value that represents whether the given
        syllogistic form is canonically valid.

        Parameters
        ----------
        syllogism : str
            A string of the form 'VVV-#', where 'V' is any of the vowels
            'A', 'E', 'I', or 'O' and '#' is '1', '2', '3', or '4'.

        Returns
        -------
        A boolean value that represents whether ``syllogism`` corresponds
        to a form canonically considered to be valid in the Aristotelian
        school of logic.

        """
        # Validate the input string.
        mood, figure = syllogism.split("-")

        if not mood or not figure:
            raise ValueError("You must specify both syllogism's mood and figure.")

        if (
            len(syllogism) != 5
            or not (int(figure) >= 1 and int(figure) <= 4)
        ):
            raise ValueError("Argument `syllogism` must be a string of form 'VVV-#'.")

        for c in mood:
            # Ensure case insensitivity.
            if c.upper() not in "AEIO":
                return ValueError(
                    "Argument `syllogism` must have a mood component whose every\n"
                    "character is one of the values 'A', 'E', 'I', or 'O'."
                )

        return True if syllogism in VALID_SYLLOGISTIC_FORMS else False

