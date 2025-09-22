# SPDX-FileCopyrightText: 2023 Carmen Bianca BAKKER <carmen@carmenbianca.eu>
#
# SPDX-License-Identifier: EUPL-1.2+

"""Some typing definitions."""

from datetime import date, datetime
from os import PathLike
from typing import Literal, Mapping, TypeAlias

# pylint: disable=invalid-name

#: Anything that looks like a path.
StrPath: TypeAlias = str | PathLike

#: The supported markup languages.
SupportedMarkup: TypeAlias = Literal["markdown", "restructuredtext"]

#: A TOML dictionary.
TOMLType: TypeAlias = Mapping[str, "TOMLValue"]
#: All possible types for a value in a TOML dictionary.
TOMLValue: TypeAlias = (
    str
    | int
    | float
    | bool
    | datetime
    | date
    | None
    | TOMLType
    | list["TOMLType"]
)
#: Like :data:`TOMLValue`, but using only Python primitives.
TOMLValueType: TypeAlias = (
    str | int | float | bool | datetime | date | None | dict | list
)
