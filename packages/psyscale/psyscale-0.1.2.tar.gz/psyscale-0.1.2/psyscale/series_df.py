"""
Wrapper Class for Timeseries Dataframes.
Class Standardizes Column Names & uses pandas_market_calendars
to determine the Trading Hours session.
"""

from importlib import import_module
import logging
from functools import partial
from types import ModuleType
from typing import TYPE_CHECKING, Dict, Optional

import pandas as pd


log = logging.getLogger("psyscale_log")

# Trading Hours Integer Encoding
EXT_MAP = {
    "pre": 1,
    "rth_pre_break": 0,
    "rth": 0,
    "break": 3,
    "rth_post_break": 0,
    "post": 2,
    "closed": -1,
}

# pylint: disable=line-too-long, invalid-name
# region ------------------------------ DataFrame Functions ------------------------------ #


def determine_timedelta(series: pd.DatetimeIndex | pd.Series) -> pd.Timedelta:
    "Returns the most frequent Timedelta within the first 250 indices of the data given"
    if isinstance(series, pd.DatetimeIndex):
        # .diff() Unknown-attribute False Alarm Error.
        return pd.Timedelta(series[0:250].diff().value_counts().idxmax())  # type: ignore
    else:
        return pd.Timedelta(series.iloc[0:250].diff().value_counts().idxmax())


def _standardize_names(df: pd.DataFrame):
    """
    Standardize the column names of the given dataframe to a consistent format for
    OHLC and Single Value Time-series. Changes are made inplace.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        # In the event the timestamp is the index, reset it for naming
        df.reset_index(inplace=True, names="time")

    rename_map = {}
    df.columns = list(map(str.lower, df.columns))
    column_names = set(df.columns)

    # |= syntax merges the returned mapping into rename_map
    rename_map |= _column_name_check(
        column_names,
        ["dt", "t", "time", "date", "datetime", "timestamp"],
        True,
    )

    # These names are mostly chosen to match what Lightweight-Charts expects as input data
    rename_map |= _column_name_check(column_names, ["open", "o", "first"])
    rename_map |= _column_name_check(column_names, ["close", "c", "last"])
    rename_map |= _column_name_check(column_names, ["high", "h", "max"])
    rename_map |= _column_name_check(column_names, ["low", "l", "min"])
    rename_map |= _column_name_check(column_names, ["volume", "v", "vol"])
    rename_map |= _column_name_check(column_names, ["price", "val", "data", "value"])
    rename_map |= _column_name_check(column_names, ["vwap", "vw"])
    rename_map |= _column_name_check(column_names, ["ticks", "tick", "count", "trade_count", "n"])

    if len(rename_map) > 0:
        return df.rename(columns=rename_map, inplace=True)


def _column_name_check(
    column_names: set[str],
    aliases: list[str],
    required: bool = False,
) -> Dict[str, str]:
    """
    Checks the column names for any of the expected aliases.
    If required and not present, an Attribute Error is thrown.

    Returns a mapping of the {'aliases[0]': 'Found Alias'} if necessary
    """
    intersection = list(column_names.intersection(aliases))

    if len(intersection) == 0:
        if required:
            raise AttributeError(f'Given data must have a "{" | ".join(aliases)}" column')
        return {}

    if len(intersection) > 1:
        raise AttributeError(f'Given data can have only one "{" | ".join(aliases)}" type of column')

    return {intersection[0]: aliases[0]}


# endregion

# region --------------------------- Pandas Dataframe Object Wrappers --------------------------- #


class Series_DF:
    "Used to standardize column names and Mark EXT Session using pandas market calendars."

    def __init__(
        self,
        pandas_df: pd.DataFrame,
        exchange: Optional[str] = None,
    ):
        _standardize_names(pandas_df)
        # Set Consistent Time format (Pd.Timestamp, UTC, TZ Aware)
        pandas_df["dt"] = pd.to_datetime(pandas_df["dt"], utc=True)
        self.timedelta = determine_timedelta(pandas_df["dt"])
        self.calendar = CALENDARS.request_calendar(exchange, pandas_df["dt"].iloc[0], pandas_df["dt"].iloc[-1])

        self.df = pandas_df.set_index("dt", drop=False)
        self._mark_ext()

    # region --------- Properties --------- #

    @property
    def columns(self) -> set[str]:
        "Column Names within the Dataframe"
        return set(self.df.columns)

    @property
    def ext(self) -> bool | None:
        "True if data has Extended Trading Hours Data, False if no ETH Data, None if undefined."
        return self._ext

    @property
    def _dt_index(self) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(self.df.index)  # type:ignore

    # endregion

    def _mark_ext(self, force_rth: bool = False):
        if "rth" in self.columns:
            # In case only part of the df has ext classification, fill the remainder
            missing_rth = self._dt_index[self.df["rth"].isna()]
            rth_col = CALENDARS.mark_session(self.calendar, missing_rth)
            if rth_col is not None:
                self.df.loc[rth_col.index, "rth"] = rth_col
        else:
            # Calculate the Full Trading Hours Session
            rth_col = CALENDARS.mark_session(self.calendar, self._dt_index)
            if rth_col is not None:
                self.df["rth"] = rth_col

        if "rth" not in self.columns:
            self._ext = None
        elif force_rth:
            self.df = self.df[self.df["rth"] == EXT_MAP["rth"]]
            self._ext = False
        elif (self.df["rth"] == 0).all():
            # Only RTH Sessions
            self._ext = False
        else:
            # Some RTH, Some ETH Sessions
            self._ext = True


# endregion

# region --------------------------- Pandas_Market_Calendars Adapter --------------------------- #

if TYPE_CHECKING:
    import pandas_market_calendars as mcal
    from pandas_market_calendars import MarketCalendar
else:
    mcal: Optional[ModuleType] = None


class Calendars:
    """
    Class abstracts and contains the functionality of pandas_market_calendars.

    Instantiating only a single instance reduces unnecessary redundancy by making
    market schedules shared across all dataframes that utilize them. Considering that generating
    schedules is easily the slowest part of analyzing a Market's Open/Close Session this equates
    to a significant performance improvement.
    """

    EXCHANGE_NAMES = {}
    ALT_EXCHANGE_NAMES = {
        "xnas": "NASDAQ",
        "arca": "NYSE",
        "forex": "24/5",
        "crypto": "24/7",
    }

    def __init__(self):
        self.mkt_cache: Dict[str, MarketCalendar] = {}
        self.schedule_cache: Dict[str, pd.DataFrame] = {}

    def _import_mcal(self):
        # Lazy load Pandas_market_calendars
        # pylint: disable-next='global-statement'
        global mcal
        mcal = import_module("pandas_market_calendars")
        self.EXCHANGE_NAMES = dict([(val.lower(), val) for val in mcal.get_calendar_names()])

    def request_calendar(self, exchange: Optional[str], start: pd.Timestamp, end: pd.Timestamp) -> str:
        "Request a Calendar & Schedule be Cached. Returns a token to access the cached calendar"
        if mcal is None:
            self._import_mcal()

        if exchange is None:
            return "24/7"
        exchange = exchange.lower()
        if exchange in self.ALT_EXCHANGE_NAMES:
            cal = mcal.get_calendar(self.ALT_EXCHANGE_NAMES[exchange])
        elif exchange in self.EXCHANGE_NAMES:
            cal = mcal.get_calendar(self.EXCHANGE_NAMES[exchange])
        else:
            cal = None
            log.warning(
                "Exchange '%s' doesn't match any exchanges. Using 24/7 Calendar.",
                exchange,
            )

        if cal is None or cal.name == "24/7":
            return "24/7"

        start = start - pd.Timedelta("1W")
        end = end + pd.Timedelta("1W")

        if cal.name not in self.mkt_cache:  # New Calendar Requested
            # Bind the Market_times & special_times arguments to the schedule function
            cal.schedule = partial(  # type:ignore
                cal.schedule, market_times="all", force_special_times=False
            )
            self.mkt_cache[cal.name] = cal
            # Generate a Schedule with buffer dates on either side.
            self.schedule_cache[cal.name] = cal.schedule(start, end)
            return cal.name

        # Cached Calendar Requested
        extra_dates = None
        cal = self.mkt_cache[cal.name]
        sched = self.schedule_cache[cal.name]
        if sched.index[0] > start.tz_localize(None):
            # Extend Start of Schedule with an additional buffer
            extra_dates = cal.schedule(start, sched.index[0] - pd.Timedelta("1D"))
            sched = pd.concat([extra_dates, sched])
        if sched.index[-1] < end.normalize().tz_localize(None):
            # Extend End of Schedule with an additional buffer
            extra_dates = cal.schedule(sched.index[-1] + pd.Timedelta("1D"), end)
            sched = pd.concat([sched, extra_dates])

        if extra_dates is not None:
            self.schedule_cache[cal.name] = sched

        return cal.name

    def mark_session(self, calendar: str, time_index: pd.DatetimeIndex) -> pd.Series | None:
        "Return a Series that denotes the appropriate Trading Hours Session for the given Calendar"
        if mcal is None or calendar == "24/7":
            return None

        return mcal.mark_session(self.schedule_cache[calendar], time_index, label_map=EXT_MAP, closed="left")


# Prep the shared Calendars sudo-singleton, will init when needed
CALENDARS = Calendars()

# endregion
