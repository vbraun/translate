"""
Tests for the format string checks on plural units.

For a plural unit every translated form has to be consistent with the source:
the first form follows the singular source, and may also follow the plural
source where the language uses it for numbers other than one (e.g. Russian 21
or French 0). The remaining forms have to follow the plural source.
"""

import pytest

from translate.filters import checks
from translate.filters.checks.checker import CheckFailures
from translate.storage import po

SINGULAR = "This is one %(thing)s"
PLURAL = "These are %(num)d %(thing)s"


def run_check(
    checkname: str, source: list[str], target: list[str], targetlanguage: str = "de"
) -> CheckFailures:
    unit = po.pounit("")
    unit.source = source
    unit.target = target
    checker = checks.StandardChecker(
        checks.CheckerConfig(targetlanguage=targetlanguage),
        limitfilters=[checkname],
    )
    return checker.run_filters(unit)


@pytest.mark.parametrize(
    "target",
    [
        # Same variables as the respective source form
        ["Das ist ein %(thing)s", "Das sind %(num)d %(thing)s"],
        # Reordered named variables
        ["Ein %(thing)s", "%(thing)s: %(num)d"],
    ],
)
def test_printf_plural_passes(target: list[str]) -> None:
    assert "printf" not in run_check("printf", [SINGULAR, PLURAL], target)


@pytest.mark.parametrize(
    ("targetlanguage", "target"),
    [
        # First form is also used for 21, 31, ...
        (
            "ru",
            ["Это %(num)d %(thing)s", "Это %(num)d %(thing)s", "Это %(num)d %(thing)s"],
        ),
        # First form is also used for 0
        ("fr", ["C'est %(num)d %(thing)s", "Ce sont %(num)d %(thing)s"]),
        # Only one form for all numbers
        ("ja", ["%(num)d %(thing)s"]),
    ],
)
def test_printf_plural_first_form_with_count(
    targetlanguage: str, target: list[str]
) -> None:
    assert "printf" not in run_check(
        "printf", [SINGULAR, PLURAL], target, targetlanguage=targetlanguage
    )


@pytest.mark.parametrize(
    "target",
    [
        # Singular form uses the count, German uses it for one only
        ["Das ist %(num)d %(thing)s", "Das sind %(num)d %(thing)s"],
        # Plural form lacks the count
        ["Das ist ein %(thing)s", "Das sind viele %(thing)s"],
        # Plural form lacks the thing
        ["Das ist ein %(thing)s", "Das sind %(num)d Dinge"],
        # Singular form lacks the thing present in both sources
        ["Das ist eins", "Das sind %(num)d %(thing)s"],
        # Variable not present in any source
        ["Das ist ein %(thing)s", "Das sind %(num)d %(thing)s %(bogus)s"],
        ["Das ist ein %(thing)s %(bogus)s", "Das sind %(num)d %(thing)s"],
        # Different variable type
        ["Das ist ein %(thing)d", "Das sind %(num)d %(thing)s"],
        ["Das ist ein %(thing)s", "Das sind %(num)s %(thing)s"],
        # No variables at all
        ["Das ist eins", "Das sind viele"],
    ],
)
def test_printf_plural_fails(target: list[str]) -> None:
    assert "printf" in run_check("printf", [SINGULAR, PLURAL], target)


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (["One file", "%d files"], ["Eine Datei", "%d Dateien"]),
        (["%d file", "%d files"], ["%d Datei", "%d Dateien"]),
        (
            ["One file in %s", "%d files in %s"],
            ["Eine Datei in %s", "%d Dateien in %s"],
        ),
    ],
)
def test_printf_plural_positional_passes(source: list[str], target: list[str]) -> None:
    assert "printf" not in run_check("printf", source, target)


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (["One file", "%d files"], ["Eine Datei", "Dateien"]),
        (["One file", "%d files"], ["Eine Datei", "%s Dateien"]),
        (["One file", "%d files"], ["Eine Datei %s", "%d Dateien"]),
        (["%d file", "%d files"], ["%d Datei", "%d Dateien %d"]),
    ],
)
def test_printf_plural_positional_fails(source: list[str], target: list[str]) -> None:
    assert "printf" in run_check("printf", source, target)


BRACE_SINGULAR = "This is one {thing}"
BRACE_PLURAL = "These are {num} {thing}"


@pytest.mark.parametrize(
    "target",
    [
        # Same variables as the respective source form
        ["Das ist ein {thing}", "Das sind {num} {thing}"],
        # Reordered named variables
        ["Ein {thing}", "{thing}: {num}"],
    ],
)
def test_pythonbraceformat_plural_passes(target: list[str]) -> None:
    assert "pythonbraceformat" not in run_check(
        "pythonbraceformat", [BRACE_SINGULAR, BRACE_PLURAL], target
    )


@pytest.mark.parametrize(
    ("targetlanguage", "target"),
    [
        # First form is also used for 21, 31, ...
        ("ru", ["Это {num} {thing}", "Это {num} {thing}", "Это {num} {thing}"]),
        # First form is also used for 0
        ("fr", ["C'est {num} {thing}", "Ce sont {num} {thing}"]),
        # Only one form for all numbers
        ("ja", ["{num} {thing}"]),
    ],
)
def test_pythonbraceformat_plural_first_form_with_count(
    targetlanguage: str, target: list[str]
) -> None:
    assert "pythonbraceformat" not in run_check(
        "pythonbraceformat",
        [BRACE_SINGULAR, BRACE_PLURAL],
        target,
        targetlanguage=targetlanguage,
    )


@pytest.mark.parametrize(
    "target",
    [
        # Singular form uses the count, German uses it for one only
        ["Das ist {num} {thing}", "Das sind {num} {thing}"],
        # Plural form lacks the count
        ["Das ist ein {thing}", "Das sind viele {thing}"],
        # Plural form lacks the thing
        ["Das ist ein {thing}", "Das sind {num} Dinge"],
        # Singular form lacks the thing present in both sources
        ["Das ist eins", "Das sind {num} {thing}"],
        # Variable not present in any source
        ["Das ist ein {thing}", "Das sind {num} {thing} {bogus}"],
        ["Das ist ein {thing} {bogus}", "Das sind {num} {thing}"],
        # No variables at all
        ["Das ist eins", "Das sind viele"],
    ],
)
def test_pythonbraceformat_plural_fails(target: list[str]) -> None:
    assert "pythonbraceformat" in run_check(
        "pythonbraceformat", [BRACE_SINGULAR, BRACE_PLURAL], target
    )


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (["One file", "{} files"], ["Eine Datei", "{} Dateien"]),
        (["{} file", "{} files"], ["{} Datei", "{} Dateien"]),
        (
            ["One file in {}", "{} files in {}"],
            ["Eine Datei in {}", "{} Dateien in {}"],
        ),
        (
            ["One file in {1}", "{0} files in {1}"],
            ["Eine Datei in {1}", "In {1} sind {0} Dateien"],
        ),
    ],
)
def test_pythonbraceformat_plural_positional_passes(
    source: list[str], target: list[str]
) -> None:
    assert "pythonbraceformat" not in run_check("pythonbraceformat", source, target)


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (["One file", "{} files"], ["Eine Datei", "Dateien"]),
        (["One file", "{} files"], ["Eine Datei {} {}", "{} Dateien"]),
        (["{} file", "{} files"], ["{} Datei", "{} Dateien {}"]),
        (
            ["One file in {1}", "{0} files in {1}"],
            ["Eine Datei in {2}", "{0} Dateien in {1}"],
        ),
    ],
)
def test_pythonbraceformat_plural_positional_fails(
    source: list[str], target: list[str]
) -> None:
    assert "pythonbraceformat" in run_check("pythonbraceformat", source, target)
