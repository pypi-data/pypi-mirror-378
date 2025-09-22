#!/usr/bin/env python3

"""Utils for the work module."""

import datetime as dt
import re
import textwrap
from collections import Counter
from fnmatch import fnmatch


def contains_capital_letter(value: str) -> bool:
    """Check if the given string contains at least one capital letter."""
    return value.casefold() != value


def fnmatch_smartcase(value: str, pattern: str) -> bool:
    """Proxy to `fnmatch` that supports smart case (from `fd`).

    If the given pattern contains at least one capital letter, the comparison is made
    case sensitively. Otherwise, it is case insensitive."""
    if not contains_capital_letter(pattern):
        value = value.casefold()
        pattern = pattern.casefold()
    return fnmatch(value, pattern)


def verify_date_arguments(
    year: int | None, month: int | None = None, day: int | None = None
):
    """Ensure only the allowed combinations are set and all values are valid."""

    if year is None and month is None and day is None:
        return

    if year is None or (month is None and day is not None):
        raise ValueError("Invalid combination of year, month and day")

    month = month or 1
    day = day or 1
    # datetime verifies the validity of the given date
    dt.datetime(year, month, day)


def minutes_difference(start: dt.datetime, end: dt.datetime) -> float:
    """Calculates the minutes between start and end time. If end < start, the result is
    negative!"""
    return (end - start) / dt.timedelta(minutes=1)


def get_period(period_start: dt.date, period_end: dt.date) -> list[dt.date]:
    """
    Return a period defined by two dates.

    Raises if `period_start` > `period_end`.
    """
    if period_start > period_end:
        raise ValueError("Period start lies after period end.")

    period_ends: list[dt.date] = [period_start, period_end]
    start_day, end_day = period_ends

    period: list[dt.date] = []
    iterated_day = start_day
    while iterated_day <= end_day:
        period.append(iterated_day)
        iterated_day += dt.timedelta(days=1)

    return period


def adjacent_dates(left: dt.date, right: dt.date) -> bool:
    """Check if the given dates are directly adjacent in ascending order."""
    return left + dt.timedelta(days=1) == right


def is_continuous_period(period: list[dt.date]) -> bool:
    """Check if the period given is uninterrupted. Does not sort input list!"""
    if len(period) <= 1:
        return True

    for i in range(1, len(period)):
        if not adjacent_dates(period[i - 1], period[i]):
            return False
    return True


def continuous_periods(dates: list[dt.date]) -> list[list[dt.date]]:
    """Split up the list of dates into lists of continuous periods contained within.

    Important: Does not sort input list!

    Returns a list of lists of dates."""
    if len(dates) <= 1:
        return [dates]

    periods: list[list[dt.date]] = [dates[:1]]

    for date in dates[1:]:
        if not adjacent_dates(periods[-1][-1], date):
            periods.append([date])
            continue
        periods[-1].append(date)

    return periods


def wrap_and_indent(*paragraphs: str, width=80, prefix="") -> str:
    """Wrap and indent the given paragraph(s) and return the joined strings."""
    result: list[str] = []
    for paragraph in paragraphs:
        result.append(
            textwrap.fill(
                paragraph,
                width=width,
                initial_indent=prefix,
                subsequent_indent=prefix,
                replace_whitespace=False,
            )
        )
    return "\n".join(result)


def pluralize(number: int | float, item: str) -> str:
    """Return "<number> <item>" and append "s" if the given number is not 1."""
    postfix: str = "s" if number != 1 else ""
    return f"{number} {item}{postfix}"


class Color:
    """See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit"""

    BLUE = 27
    GRAY = 242
    GREEN = 34
    ORANGE = 202
    RED = 9

    @staticmethod
    def color(text: str, clr_code: int, background: bool = False) -> str:
        """Color text with given color."""
        fg_bg_code = "38" if not background else "48"
        return Color._format(
            text=text, format_code="{};5;{}".format(fg_bg_code, clr_code)
        )

    @staticmethod
    def bold(text: str) -> str:
        """Format text as bold."""
        return Color._format(text=text, format_code="1")

    @staticmethod
    def _format(text: str, format_code: str) -> str:
        return "\x1b[{}m{}\x1b[0m".format(format_code, text)

    @staticmethod
    def clear(text: str) -> str:
        """Clear any applied escape sequences from the text."""
        return re.sub(r"\x1b\[[0-?]*[ -\/]*[@-~]", "", text)


class PrinTable:
    """Automatically justify strings in rows for a formatted table."""

    def __init__(self, padding: str = "") -> None:
        self.rows: list[list[str]] = []
        self.lines: dict[int, str] = {}
        self.padding: str = padding

    def add_row(self, row: list[str]) -> None:
        """Add a row, represented as a list of column entries."""
        padded_row = [f"{self.padding}{cell}{self.padding}" for cell in row]
        self.rows.append(padded_row)

    def add_line(self, char: str) -> None:
        """Add a line, e.g. below a heading. Fills a row with the given char(s)."""
        self.lines[len(self.rows)] = char

    def printable(self) -> list[list[str]]:
        """Return rows with each cell left-justified to match the column width."""
        # Remove outer padding from first and last column
        unpadded_rows: list[list[str]] = [self._unpad_row(row) for row in self.rows]

        # Calculate column widths for printing
        col_widths: Counter = Counter()
        for row in unpadded_rows:
            for i, col in enumerate(row):
                # Clear the col of color codes before computing the string length
                col_widths[i] = max(col_widths[i], self._actual_len(col))

        # Return justified rows
        formatted_rows: list[list[str]] = []
        for row in unpadded_rows:
            formatted_row: list[str] = []
            for i, col in enumerate(row):
                delta_len: int = col_widths[i] - self._actual_len(col)
                formatted_row.append(col.ljust(len(col) + delta_len))
            formatted_rows.append(formatted_row)

        offset: int = 0
        for insert_idx, char in self.lines.items():
            line_row: list[str] = []
            for width in col_widths.values():
                line_row.append((width * char)[:width])
            formatted_rows.insert(insert_idx + offset, line_row)
            offset += 1

        return formatted_rows

    def _unpad_row(self, row: list[str]) -> list[str]:
        """Remove outer padding from first and last column."""
        if len(row) == 0:
            return row
        if len(row) == 1:
            return [row[0].removeprefix(self.padding).removesuffix(self.padding)]
        return [
            row[0].removeprefix(self.padding),
            *row[1:-1],
            row[-1].removesuffix(self.padding),
        ]

    def printable_str(self) -> list[str]:
        """
        Return rows justified (see `printable()`), but additionally combines the rows
        and trims excess space on the right.
        """
        return ["".join(row).rstrip() for row in self.printable()]

    @staticmethod
    def _actual_len(col: str) -> int:
        """The length of the string not counting escape sequences."""
        return len(Color.clear(col))
