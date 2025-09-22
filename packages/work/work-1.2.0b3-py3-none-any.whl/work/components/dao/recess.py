#!/usr/bin/env python3

"""The DAO for the recess files."""

import datetime as dt
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Literal, cast

from work.components.consts import RECESS_DIRECTORY_NAME, RECESS_FILE_EXTENSION

# Each recess file is a JSON dictionary with three elements:
# holidays          = []  --  a list of holidays
# reduced_hour_days = {}  --  a dictionary of reduced hour days (value: reduced hour value)
# vacations         = {}  --  a dictionary of vacation days (value: factor)
#
# For example:
# {
#   "holidays" : [
#     "2021-01-05"
#   ],
#   "reduced_hour_days" : {
#     "2021-01-05": 4.0
#   },
#   "vacations" : {
#     "2025-09-03": "1",
#     "2025-09-16": "0,5"
#   }
# }
#
# Each list needs to be unique, but days may be in multiple.


# TODO:
# 1.) Prevent duplicates (or handle smartly)
# 2.) Rename directory?

DATE_FORMAT: str = "%Y-%m-%d"
Factor = Literal["1", "0,5"]


@dataclass
class Recess:
    """A generic recess day."""

    date: dt.date

    def __init__(self, date: dt.date):
        self.date = date

    def __str__(self) -> str:
        return self.date.strftime(DATE_FORMAT)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Recess):
            return False
        return other.date == self.date

    def __lt__(self, other) -> bool:
        return self.date < other.date


@dataclass
class Holiday(Recess):
    """A public holiday."""


@dataclass
class Vacation(Recess):
    """A vacation, representing paid-time-off."""

    factor: Factor

    @property
    def half_day(self) -> bool:
        """Return if the vacation is only for a half day."""
        return {"0,5": True, "1": False}[self.factor]


@dataclass
class ReducedHourDay(Recess):
    """A reduced day, denoting a day where less hours need to be worked."""

    hours: float = 0

    def __init__(self, date: dt.date, hours: float):
        super().__init__(date=date)
        self.hours = hours


class ExistsError(Exception):
    """Exception that denotes that a recess day exists already."""


class RecessFile:
    """Writes to file on update. Creates directory and file if nonexistent."""

    holidays_k: str = "holidays"
    reduceds_k: str = "reduced_hour_days"
    vacations_k: str = "vacations"

    half_day_to_str: dict[bool, str] = {False: "1", True: "0,5"}
    str_to_half_day: dict[str, bool] = {v: k for k, v in half_day_to_str.items()}

    # work_directory (see work.components/consts.py)
    # |- recess/
    #    |- 2020.wvac
    #    |- 2021.wvac
    def __init__(self, recess_directory: Path, year: int) -> None:
        self.recess_directory = recess_directory
        self.file: Path = Path(recess_directory, f"{year}.{RECESS_FILE_EXTENSION}")
        self.holidays: list[Holiday] = []
        self.reduced_hour_days: list[ReducedHourDay] = []
        self.vacations: list[Vacation] = []
        if not self.file.exists():
            return

        with self.file.open(mode="r", encoding="utf-8") as v_file:
            try:
                vf_json = json.load(v_file)
            except Exception as exc:
                raise IOError(f"Invalid free days file {self.file}: {exc}") from exc

        # We intentionally do not check for an erroneous file here,
        # as this should not be edited by the user.

        self.holidays = [
            Holiday(date=dt.datetime.strptime(holi_day, DATE_FORMAT).date())
            for holi_day in vf_json[RecessFile.holidays_k]
        ]
        self.reduced_hour_days = [
            ReducedHourDay(
                date=dt.datetime.strptime(redu_day, DATE_FORMAT).date(), hours=hours
            )
            for redu_day, hours in vf_json[RecessFile.reduceds_k].items()
        ]

        # <MIGRATE-vacations> To be removed in v1.4 #
        try:
            parsed_vacations = vf_json[RecessFile.vacations_k].items()
        except AttributeError:
            parsed_vacations = [(d, "1") for d in vf_json[RecessFile.vacations_k]]
        assert all(f in ["0,5", "1"] for (_, f) in parsed_vacations)
        parsed_vacations = cast(list[tuple[str, Factor]], parsed_vacations)
        self.vacations = [
            Vacation(
                date=dt.datetime.strptime(vaca_day, DATE_FORMAT).date(),
                factor=factor,
            )
            for vaca_day, factor in parsed_vacations
        ]

    @property
    def recess(self) -> Iterable[Recess]:
        """Iterate over stored recess containers of any type."""
        yield from chain(self.holidays, self.reduced_hour_days, self.vacations)

    def add_any(self, container: list, add_us: list):
        """Add any type of recess day."""
        if container and add_us:
            assert isinstance(add_us[0], type(container[0]))

        if exist := [
            rec.date
            for rec in self.recess
            if rec.date in list(map(lambda obj: obj.date, add_us))
        ]:
            raise ExistsError(
                "Free day(s) already stored: "
                f"{', '.join([e_date.strftime('%d.%m.%Y') for e_date in exist])}"
            )
        container.extend(add_us)
        self._write_out()

    def remove(self, date: dt.date) -> None:
        """Remove a recess day. If the date is present in more than one list, raises."""
        in_holidays: list[Holiday] = [h for h in self.holidays if h.date == date]
        in_reduceds: list[ReducedHourDay] = [
            r for r in self.reduced_hour_days if r.date == date
        ]
        in_vacations: list[Vacation] = [v for v in self.vacations if v.date == date]
        all_found = in_holidays + in_reduceds + in_vacations

        if len(all_found) == 0:
            raise ValueError(
                f"Free day {date.strftime('%d.%m.%Y')} could not be "
                "removed, as it does not exist."
            )

        if any(len(found) > 1 for found in (in_holidays, in_reduceds, in_vacations)):
            raise RuntimeError(
                "Error in data file. Found multiple options within a single category"
                "of free days."
            )

        # XOR (^) is only True if exactly one of the arguments is True.
        if len(all_found) > 1:
            raise NotImplementedError(
                "Ambiguous! Date is present in multiple free days lists. "
                "Please remove manually."
            )

        # At this point, we know that there is exactly one match in exactly one list.
        assert len(all_found) == 1
        found: Recess = all_found[0]

        if isinstance(found, Holiday):
            self._remove_any(self.holidays, found)
        elif isinstance(found, ReducedHourDay):
            for rhd in self.reduced_hour_days:
                if rhd.date == date:
                    self._remove_any(self.reduced_hour_days, rhd)
        elif isinstance(found, Vacation):
            self._remove_any(self.vacations, found)

    def _remove_any(self, container: list, remove_me):
        if container:
            assert isinstance(remove_me, type(container[0]))
        try:
            container.remove(remove_me)
        except ValueError as val_err:
            raise RuntimeError("Could not delete nonexistent free day.") from val_err
        self._write_out()

    def _write_out(self):
        """Write cached days to file. Creates directory and file if nonexistent."""

        # Create recess directory if it does not exist.
        self.recess_directory.mkdir(exist_ok=True)

        out_dict = {
            RecessFile.holidays_k: [str(h) for h in sorted(self.holidays)],
            RecessFile.reduceds_k: {
                str(rhd): rhd.hours for rhd in sorted(self.reduced_hour_days)
            },
            RecessFile.vacations_k: {str(v): v.factor for v in sorted(self.vacations)},
        }

        with self.file.open(mode="w", encoding="utf-8", newline="\n") as v_file:
            json.dump(out_dict, v_file, indent="\t", ensure_ascii=False)


class RecessDao:
    """Interface to manage recess. Handles `RecessFile`s internally."""

    def __init__(self, work_directory: Path) -> None:
        self.directory: Path = work_directory.joinpath(RECESS_DIRECTORY_NAME)
        self.recess_files: dict[int, RecessFile] = {}

    def _get(self, year: int) -> RecessFile:
        """Load RecessFile from cache. If not cached, load from disk."""
        if year not in self.recess_files:
            self.recess_files[year] = RecessFile(self.directory, year)
        return self.recess_files[year]

    def get_holidays(self, year: int) -> list[Holiday]:
        """Return stored holidays in the given year."""
        return self._get(year=year).holidays

    def get_reduced_hour_days(self, year: int) -> list[ReducedHourDay]:
        """Return stored reduced days in the given year."""
        return self._get(year=year).reduced_hour_days

    def get_vacations(self, year: int) -> list[Vacation]:
        """Return stored vacations in the given year."""
        # TODO: We could return these as ranges of continuous days
        return self._get(year=year).vacations

    def has_days(self, year: int) -> bool:
        """Return if the given year has any recess days."""
        r_file: RecessFile = self._get(year=year)
        return (
            len(r_file.holidays) > 0
            or len(r_file.reduced_hour_days) > 0
            or len(r_file.vacations) > 0
        )

    def add_holiday(self, date: dt.date) -> None:
        """Add holiday on the given date."""
        r_file: RecessFile = self._get(year=date.year)
        r_file.add_any(r_file.holidays, [Holiday(date=date)])

    def add_reduced_hour_day(self, date: dt.date, hours: float) -> None:
        """Add reduced day on the given date with the given hours."""
        r_file: RecessFile = self._get(year=date.year)
        r_file.add_any(
            r_file.reduced_hour_days, [ReducedHourDay(date=date, hours=hours)]
        )

    def add_vacation(self, period: list[dt.date], factor: Factor) -> None:
        """Add vacation for the period between the given dates."""
        vacations_by_year: defaultdict[int, list[Vacation]] = defaultdict(list)
        for date in period:
            vacations_by_year[date.year].append(Vacation(date=date, factor=factor))
        for year in vacations_by_year:
            r_file: RecessFile = self._get(year=year)
            r_file.add_any(r_file.vacations, vacations_by_year[year])

    def remove(self, dates: list[dt.date]) -> None:
        """Remove recess day(s). If any date is present in more than one list, raises."""
        for date in dates:
            self._get(year=date.year).remove(date=date)

    def get_recess_for(self, date: dt.date) -> Recess | None:
        """Return the associated recess for the given date if it exists."""
        r_file: RecessFile = self._get(year=date.year)

        its_recess: list[Recess] = [day for day in r_file.recess if day.date == date]

        # We assume that each day can have at most one associated recess.
        if len(its_recess) > 1:
            raise ExistsError(f"Multiple free days found for {date}")

        return its_recess[0] if its_recess else None

    def minutes_after_reduction(self, date: dt.date, normal_minutes: float) -> float:
        """
        Get the reduced minutes for a given date.

        If the day is not a (partially) free day, `normal_minutes` is returned.
        """
        associated_recess: Recess | None = self.get_recess_for(date)
        if associated_recess is None:
            return normal_minutes

        if isinstance(associated_recess, ReducedHourDay):
            return associated_recess.hours * 60.0

        if isinstance(associated_recess, Vacation):
            if associated_recess.half_day:
                return normal_minutes * 0.5
            return 0

        # Only remaining option is a holiday
        assert isinstance(associated_recess, Holiday)
        return 0
