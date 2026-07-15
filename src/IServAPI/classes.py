from typing import TypedDict, Literal, Union, Optional, Dict


# Classes for typing
class Recurring(TypedDict, total=False):
    intervalType: Literal["NO", "DAILY", "WEEKDAYS", "WEEKLY", "MONTHLY", "YEARLY"]
    interval: Literal[
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
    ]
    monthDayInMonth: Literal[
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
    ]
    monthlyIntervalType: Literal["BYMONTHDAY", "BYDAY"]
    monthInterval: Literal[1, 2, 3, 4, -1]
    monthDay: Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
    recurrenceDays: list[Literal["MO", "TU", "WE", "TH", "FR", "SA", "SU"]]
    endType: Literal["NEVER", "COUNT", "UNTIL"]
    endInterval: Optional[int]
    untilDate: Optional[str]


class CustomDateTime(TypedDict):
    dateTime: str


# Interval structure
class Interval(TypedDict):
    days: int
    hours: int
    minutes: int


class CustomInterval(TypedDict):
    interval: Interval
    before: bool


# Main type
AlarmType = Union[
    Literal["0M", "5M", "15M", "30M", "1H", "2H", "12H", "1D", "2D", "7D"],
    Dict[str, CustomDateTime],  # {"custom_date_time": {...}}
    Dict[str, CustomInterval],  # {"custom_interval": {...}}
]
