from typing import Callable

from dyngle.error import DyngleError
from dyngle.safe_path import SafePath

from datetime import datetime as datetime, date, timedelta
import math
import json
import re
import yaml

from dyngle.template import Template


def formatted_datetime(dt: datetime, format_string=None) -> str:
    """Safe datetime formatting using string operations"""
    if format_string is None:
        format_string = "{year:04d}{month:02d}{day:02d}"
    components = {
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute,
        'second': dt.second,
        'microsecond': dt.microsecond,
        'weekday': dt.weekday(),  # Monday is 0
    }
    return format_string.format(**components)


GLOBALS = {
    "__builtins__": {
        # Basic data types and conversions
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,

        # Essential functions
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "reversed": reversed,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
    },

    # Mathematical operations
    "math": math,

    # Date and time handling
    "datetime": datetime,
    "date": date,
    "timedelta": timedelta,
    "formatted": formatted_datetime,

    # Data parsing and manipulation
    "json": json,
    "yaml": yaml,
    "re": re,

    # Safe Path-like operations (within cwd)
    "Path": SafePath
}


def _evaluate(expression: str, locals: dict) -> str:
    """Evaluate a Python expression with safe globals and user data context.

    Safely evaluates a Python expression string using a restricted set of
    global functions and modules, combined with user-provided data. The
    expression is evaluated in a sandboxed environment that includes basic
    Python built-ins, mathematical operations, date/time handling, and data
    manipulation utilities.

    Parameters
    ----------
    expression : str
        A valid Python expression string to be evaluated.
    data : dict
        Dictionary containing variables and values to be made available during
        expression evaluation. Note that hyphens in keys will be replaced by
        underscores to create valid Python names.

    Returns
    -------
    str
        String representation of the evaluated expression result. If the result
        is a tuple, returns the string representation of the last element.

    Raises
    ------
    DyngleError
        If the expression contains invalid variable names that are not found in
        the provided data dictionary or global context.
    """
    try:
        result = eval(expression, GLOBALS, locals)
    except KeyError:
        raise DyngleError(f"The following expression contains " +
                          f"at least one invalid name: {expression}")
    result = result[-1] if isinstance(result, tuple) else result
    return str(result)


def expression(text: str) -> Callable[[dict], str]:
    def evaluate(data: dict = None) -> str:
        items = data.items() if data else ()
        locals = {k.replace('-', '_'): v for k, v in items}
        def resolve(s): return Template.resolve(s, data)
        return _evaluate(text, locals | {'resolve': resolve})
    return evaluate
