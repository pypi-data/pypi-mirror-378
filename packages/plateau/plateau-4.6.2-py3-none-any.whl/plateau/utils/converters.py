"""Helper module to convert user inputs into normalized forms."""

from collections.abc import Iterable

import pandas as pd
import pyarrow as pa

__all__ = (
    "converter_str",
    "converter_str_set",
    "converter_str_set_optional",
    "converter_str_tupleset",
    "converter_tuple",
    "get_str_to_python_converter",
)


def converter_str_set(obj) -> frozenset:
    """Convert input to a set of unicode strings. ``None`` will be converted to
    an empty set.

    Parameters
    ----------
    obj: Optional[Union[Iterable[str], str]]
        Object to convert.

    Returns
    -------
    obj: FrozenSet[str]
        String set.

    Raises
    ------
    TypeError
        If passed object is not string/byte-like.
    """
    result = converter_tuple(obj)
    result_set = {converter_str(x) for x in result}
    return frozenset(result_set)


def converter_str_set_optional(obj):
    """Convert input to a set of unicode strings. ``None`` will be preserved.

    Parameters
    ----------
    obj: Optional[Union[Iterable[str], str]]
        Object to convert.

    Returns
    -------
    obj: Optional[FrozenSet[str]]
        String set.

    Raises
    ------
    ValueError
        If an element in the passed object is not string/byte/like.
    """
    if obj is None:
        return None
    return converter_str_set(obj)


def converter_str_tupleset(obj: Iterable[str] | str | None) -> tuple[str, ...]:
    """Convert input to tuple of unique unicode strings. ``None`` will be
    converted to an empty set.

    The input must not contain duplicate entries.

    Parameters
    ----------
    obj
        Object to convert.

    Raises
    ------
    TypeError
        If passed object is not string/byte-like, or if ``obj`` is known to have an unstable iteration order.
    ValueError
        If passed set contains duplicates.
    """
    if isinstance(obj, dict | frozenset | set):
        raise TypeError(
            f"{obj} which has type {type(obj).__name__} has an unstable iteration order"
        )
    result = converter_tuple(obj)
    result = tuple(converter_str(x) for x in result)
    if len(set(result)) != len(result):
        raise ValueError("Tuple-set contains duplicates: {}".format(", ".join(result)))
    return result


def converter_tuple(obj) -> tuple:
    """Convert input to a tuple. ``None`` will be converted to an empty tuple.

    Parameters
    ----------
    obj: Any
        Object to convert.

    Returns
    -------
    obj: Tuple[Any]
        Tuple.
    """
    if obj is None:
        return ()
    elif hasattr(obj, "__iter__") and not isinstance(obj, str | bytes):
        return tuple(x for x in obj)
    else:
        return (obj,)


def converter_str(obj) -> str:
    """Ensures input is a unicode string.

    Parameters
    ----------
    obj: str
        Object to convert.

    Returns
    -------
    obj: str
        String.

    Raises
    ------
    TypeError
        If passed object is not string/byte-like.
    """
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    else:
        raise TypeError(f"Object of type {type(obj).__name__} is not a string: {obj}")


def get_str_to_python_converter(pa_type):
    """Get converter to parse string into python object.

    Parameters
    ----------
    pa_type: pyarrow.DataType
        Data type.

    Returns
    -------
    converter: Callable[[str], Any]
        Converter.
    """
    if pa.types.is_boolean(pa_type):

        def var_f(x):
            if x.lower() in ("0", "f", "n", "false", "no"):
                return False
            elif x.lower() in ("1", "t", "y", "true", "yes"):
                return True
            else:
                raise ValueError(f"Cannot parse bool: {x}")

        return var_f
    elif pa.types.is_floating(pa_type):
        return float
    elif pa.types.is_integer(pa_type):
        return int
    elif pa.types.is_string(pa_type):

        def var_f(x):
            if len(x) > 1:
                for char in ('"', "'"):
                    if x.startswith(char) and x.endswith(char):
                        return x[1:-1]
            return x

        return var_f
    elif pa.types.is_timestamp(pa_type):
        return pd.Timestamp
    else:
        raise ValueError(f"Cannot handle type {pa_type}")
