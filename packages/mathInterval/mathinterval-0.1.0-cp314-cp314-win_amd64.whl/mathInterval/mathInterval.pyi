"""

mathInterval
============

C++ interval arithmetic exposed to Python.

This module provides classes and algorithms for working
with mathematical multitudes. It supports:

- Construction of multitudes with finite or infinite bounds.
- Smart search algorithms using user-provided lambdas.
- Conversion and custom transfer of interval data.
- Executing multiple operators between multitudes.

All classes and functions are documented with Python-style docstrings.
"""
from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['mathInterval', 'mathInterval_float', 'mathInterval_int', 'mathInterval_str']
class _mathInterval_float_maximal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_float_minimal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_int_maximal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_int_minimal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_maximal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_minimal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_str_maximal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class _mathInterval_str_minimal:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class mathInterval:
    maximal: typing.ClassVar[_mathInterval_maximal]  # value = <maximal>
    minimal: typing.ClassVar[_mathInterval_minimal]  # value = <minimal>
    def __add__(self, arg0: mathInterval) -> mathInterval:
        """
        returns a new multitude containing the union of the elements of the previous multitudes
        """
    def __contains__(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        return true if this point in multitude, else return false
        """
    def __iadd__(self, arg0: mathInterval) -> mathInterval:
        """
        adds elements of another multitude
        """
    def __imul__(self, arg0: mathInterval) -> mathInterval:
        """
        intersect elements with another multitude
        """
    def __init__(self) -> None:
        ...
    def __isub__(self, arg0: mathInterval) -> mathInterval:
        """
        remove elements of another multitude
        """
    def __mul__(self, arg0: mathInterval) -> mathInterval:
        """
        returns a new multitude containing the intersection of the elements of the previous multitudes
        """
    def __str__(self) -> str:
        """
        return string with all data in mathematical style
        """
    def __sub__(self, arg0: mathInterval) -> mathInterval:
        """
        returns a new multitude containing the difference of the elements of the previous multitudes
        """
    def add_interval(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any], arg1: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        returns false if all this interval was inside this multitude, else return true
        """
    def add_point(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        returns false if this point was inside this multitude, else return true
        """
    @typing.overload
    def any(self) -> typing.Any | None:
        """
        ### any
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        ---
        
        - If there is any point, it will be returned.
        - If there is an interval `(-INF; +INF)`, the function will return `None`.
        - If it is `mathInterval_int` or `mathInterval_float`,
          a smart algorithm will try to find any number in the intervals.
        - If it is `mathInterval_str`,
          a smart algorithm will try to find any string in the intervals,
          considering that a string may contain only **capital English letters**.
        - If it is standard `mathInterval`, or if the algorithm does not find any element in data,
          the function will return `None`.
        
        ---
        
        For custom types and algorithms, consider using this function with additional arguments.
        """
    @typing.overload
    def any(self, arg0: collections.abc.Callable[[typing.Any], typing.Any | None], arg1: collections.abc.Callable[[typing.Any], typing.Any | None], arg2: collections.abc.Callable[[typing.Any, typing.Any], typing.Any | None], arg3: typing.Any) -> typing.Any | None:
        """
        ### any()
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        This function takes **three lambda functions** and **one value**:
        
        ---
        
        - **First lambda** – called if there is an interval `(-INF; x)`,
          receives one argument (x).
        - **Second lambda** – called if there is an interval `(x; +INF)`,
          receives one argument (x).
        - **Third lambda** – called if there is an interval `(x; y)`,
          receives two arguments (x, y).
        - **Value** - result for interval `(-INF, +INF)`
        
        ---
        
        A lambdas may return `None`, if the interval has no integer value.
        
        ⚠️ **Warning:**
        You must yourself detect that the returning value lies inside the interval.
        """
    def clear(self) -> None:
        """
        clear multitude data
        """
    def contains(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any], arg1: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        return true if interval (a, b) in multitude, else return false
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.Any], typing.Any]) -> mathInterval:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**.
        `-INF` and `+INF` remain unchanged.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.Any], typing.Any], arg1: typing.Any, arg2: typing.Any) -> mathInterval:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**
        and **two values** – the converted values of `-INF` and `+INF`.
        New values cannot themselves be `-INF` or `+INF`.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        - **First value** – new value of the border of the interval, that begins from `-INF` - old value of a border of an interval.
        - **Second value** – new value of the border of the interval, that ends with `+INF` - old value of a border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    def empty(self) -> bool:
        """
        return true if this multitude is empty, else return false
        """
    def inverse(self) -> mathInterval:
        """
        returns the multitude that is the inverse of the given one
        """
    def remove_interval(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any], arg1: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        returns false if all this interval was not inside this multitude, else return true
        """
    def remove_point(self, arg0: mathInterval._mathInterval_minimal | mathInterval._mathInterval_maximal | typing.Any | tuple[typing.SupportsInt, typing.Any]) -> bool:
        """
        returns false if this point was not inside this multitude, else return true
        """
class mathInterval_float:
    maximal: typing.ClassVar[_mathInterval_float_maximal]  # value = <maximal>
    minimal: typing.ClassVar[_mathInterval_float_minimal]  # value = <minimal>
    @typing.overload
    def __add__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        returns a new multitude containing the union of the elements of the previous multitudes
        """
    @typing.overload
    def __add__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        returns a new multitude with the points shifted forward by the distance val
        """
    def __contains__(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        return true if this point in multitude, else return false
        """
    @typing.overload
    def __iadd__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        adds elements of another multitude
        """
    @typing.overload
    def __iadd__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        shift the points forward by a distance of val
        """
    @typing.overload
    def __imul__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        intersect elements with another multitude
        """
    @typing.overload
    def __imul__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        multiplies the points of a multitude by a factor of val
        """
    def __init__(self) -> None:
        ...
    @typing.overload
    def __isub__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        remove elements of another multitude
        """
    @typing.overload
    def __isub__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        shift the points backward by a distance of val
        """
    def __itruediv__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        divides the points of a multitude by a factor of val
        """
    @typing.overload
    def __mul__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        returns a new multitude containing the intersection of the elements of the previous multitudes
        """
    @typing.overload
    def __mul__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        returns a new multitude with the points multiplied by a factor of val
        """
    def __str__(self) -> str:
        """
        return string with all data in mathematical style
        """
    @typing.overload
    def __sub__(self, arg0: mathInterval_float) -> mathInterval_float:
        """
        returns a new multitude containing the difference of the elements of the previous multitudes
        """
    @typing.overload
    def __sub__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        returns a new multitude with the points shifted backward by the distance val
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> mathInterval_float:
        """
        returns a new multitude with the points divided by a factor of val
        """
    def add_interval(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat], arg1: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        returns false if all this interval was inside this multitude, else return true
        """
    def add_point(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        returns false if this point was inside this multitude, else return true
        """
    @typing.overload
    def any(self) -> float | None:
        """
        ### any
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        ---
        
        - If there is any point, it will be returned.
        - If there is an interval `(-INF; +INF)`, the function will return `None`.
        - If it is `mathInterval_int` or `mathInterval_float`,
          a smart algorithm will try to find any number in the intervals.
        - If it is `mathInterval_str`,
          a smart algorithm will try to find any string in the intervals,
          considering that a string may contain only **capital English letters**.
        - If it is standard `mathInterval`, or if the algorithm does not find any element in data,
          the function will return `None`.
        
        ---
        
        For custom types and algorithms, consider using this function with additional arguments.
        """
    @typing.overload
    def any(self, arg0: collections.abc.Callable[[typing.SupportsFloat], float | None], arg1: collections.abc.Callable[[typing.SupportsFloat], float | None], arg2: collections.abc.Callable[[typing.SupportsFloat, typing.SupportsFloat], float | None], arg3: typing.SupportsFloat) -> float | None:
        """
        ### any()
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        This function takes **three lambda functions** and **one value**:
        
        ---
        
        - **First lambda** – called if there is an interval `(-INF; x)`,
          receives one argument (x).
        - **Second lambda** – called if there is an interval `(x; +INF)`,
          receives one argument (x).
        - **Third lambda** – called if there is an interval `(x; y)`,
          receives two arguments (x, y).
        - **Value** - result for interval `(-INF, +INF)`
        
        ---
        
        A lambdas may return `None`, if the interval has no integer value.
        
        ⚠️ **Warning:**
        You must yourself detect that the returning value lies inside the interval.
        """
    def clear(self) -> None:
        """
        clear multitude data
        """
    def contains(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat], arg1: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        return true if interval (a, b) in multitude, else return false
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.SupportsFloat], float]) -> mathInterval_float:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**.
        `-INF` and `+INF` remain unchanged.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.SupportsFloat], float], arg1: typing.SupportsFloat, arg2: typing.SupportsFloat) -> mathInterval_float:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**
        and **two values** – the converted values of `-INF` and `+INF`.
        New values cannot themselves be `-INF` or `+INF`.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        - **First value** – new value of the border of the interval, that begins from `-INF` - old value of a border of an interval.
        - **Second value** – new value of the border of the interval, that ends with `+INF` - old value of a border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    def empty(self) -> bool:
        """
        return true if this multitude is empty, else return false
        """
    def inverse(self) -> mathInterval_float:
        """
        returns the multitude that is the inverse of the given one
        """
    def remove_interval(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat], arg1: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        returns false if all this interval was not inside this multitude, else return true
        """
    def remove_point(self, arg0: mathInterval._mathInterval_float_minimal | mathInterval._mathInterval_float_maximal | typing.SupportsFloat | tuple[typing.SupportsInt, typing.SupportsFloat]) -> bool:
        """
        returns false if this point was not inside this multitude, else return true
        """
class mathInterval_int:
    maximal: typing.ClassVar[_mathInterval_int_maximal]  # value = <maximal>
    minimal: typing.ClassVar[_mathInterval_int_minimal]  # value = <minimal>
    @typing.overload
    def __add__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        returns a new multitude containing the union of the elements of the previous multitudes
        """
    @typing.overload
    def __add__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        returns a new multitude with the points shifted forward by the distance val
        """
    def __contains__(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        return true if this point in multitude, else return false
        """
    def __floordiv__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        returns a new multitude with the points divided by a factor of val
        """
    @typing.overload
    def __iadd__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        adds elements of another multitude
        """
    @typing.overload
    def __iadd__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        shift the points forward by a distance of val
        """
    def __ifloordiv__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        divides the points of a multitude by a factor of val
        """
    def __imod__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        replaces the points with the remainder of the division by val
        """
    @typing.overload
    def __imul__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        intersect elements with another multitude
        """
    @typing.overload
    def __imul__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        multiplies the points of a multitude by a factor of val
        """
    def __init__(self) -> None:
        ...
    @typing.overload
    def __isub__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        remove elements of another multitude
        """
    @typing.overload
    def __isub__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        shift the points backward by a distance of val
        """
    def __mod__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        returns a new multitude with points taken as the remainder of the division by val
        """
    @typing.overload
    def __mul__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        returns a new multitude containing the intersection of the elements of the previous multitudes
        """
    @typing.overload
    def __mul__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        returns a new multitude with the points multiplied by a factor of val
        """
    def __str__(self) -> str:
        """
        return string with all data in mathematical style
        """
    @typing.overload
    def __sub__(self, arg0: mathInterval_int) -> mathInterval_int:
        """
        returns a new multitude containing the difference of the elements of the previous multitudes
        """
    @typing.overload
    def __sub__(self, arg0: typing.SupportsInt) -> mathInterval_int:
        """
        returns a new multitude with the points shifted backward by the distance val
        """
    def add_interval(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt], arg1: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        returns false if all this interval was inside this multitude, else return true
        """
    def add_point(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        returns false if this point was inside this multitude, else return true
        """
    @typing.overload
    def any(self) -> int | None:
        """
        ### any
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        ---
        
        - If there is any point, it will be returned.
        - If there is an interval `(-INF; +INF)`, the function will return `None`.
        - If it is `mathInterval_int` or `mathInterval_float`,
          a smart algorithm will try to find any number in the intervals.
        - If it is `mathInterval_str`,
          a smart algorithm will try to find any string in the intervals,
          considering that a string may contain only **capital English letters**.
        - If it is standard `mathInterval`, or if the algorithm does not find any element in data,
          the function will return `None`.
        
        ---
        
        For custom types and algorithms, consider using this function with additional arguments.
        """
    @typing.overload
    def any(self, arg0: collections.abc.Callable[[typing.SupportsInt], int | None], arg1: collections.abc.Callable[[typing.SupportsInt], int | None], arg2: collections.abc.Callable[[typing.SupportsInt, typing.SupportsInt], int | None], arg3: typing.SupportsInt) -> int | None:
        """
        ### any()
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        This function takes **three lambda functions** and **one value**:
        
        ---
        
        - **First lambda** – called if there is an interval `(-INF; x)`,
          receives one argument (x).
        - **Second lambda** – called if there is an interval `(x; +INF)`,
          receives one argument (x).
        - **Third lambda** – called if there is an interval `(x; y)`,
          receives two arguments (x, y).
        - **Value** - result for interval `(-INF, +INF)`
        
        ---
        
        A lambdas may return `None`, if the interval has no integer value.
        
        ⚠️ **Warning:**
        You must yourself detect that the returning value lies inside the interval.
        """
    def clear(self) -> None:
        """
        clear multitude data
        """
    def contains(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt], arg1: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        return true if interval (a, b) in multitude, else return false
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.SupportsInt], int]) -> mathInterval_int:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**.
        `-INF` and `+INF` remain unchanged.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[typing.SupportsInt], int], arg1: typing.SupportsInt, arg2: typing.SupportsInt) -> mathInterval_int:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**
        and **two values** – the converted values of `-INF` and `+INF`.
        New values cannot themselves be `-INF` or `+INF`.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        - **First value** – new value of the border of the interval, that begins from `-INF` - old value of a border of an interval.
        - **Second value** – new value of the border of the interval, that ends with `+INF` - old value of a border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    def empty(self) -> bool:
        """
        return true if this multitude is empty, else return false
        """
    def inverse(self) -> mathInterval_int:
        """
        returns the multitude that is the inverse of the given one
        """
    def remove_interval(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt], arg1: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        returns false if all this interval was not inside this multitude, else return true
        """
    def remove_point(self, arg0: mathInterval._mathInterval_int_minimal | mathInterval._mathInterval_int_maximal | typing.SupportsInt | tuple[typing.SupportsInt, typing.SupportsInt]) -> bool:
        """
        returns false if this point was not inside this multitude, else return true
        """
class mathInterval_str:
    maximal: typing.ClassVar[_mathInterval_str_maximal]  # value = <maximal>
    minimal: typing.ClassVar[_mathInterval_str_minimal]  # value = <minimal>
    def __add__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        returns a new multitude containing the union of the elements of the previous multitudes
        """
    def __contains__(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        return true if this point in multitude, else return false
        """
    def __iadd__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        adds elements of another multitude
        """
    def __imul__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        intersect elements with another multitude
        """
    def __init__(self) -> None:
        ...
    def __isub__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        remove elements of another multitude
        """
    def __mul__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        returns a new multitude containing the intersection of the elements of the previous multitudes
        """
    def __str__(self) -> str:
        """
        return string with all data in mathematical style
        """
    def __sub__(self, arg0: mathInterval_str) -> mathInterval_str:
        """
        returns a new multitude containing the difference of the elements of the previous multitudes
        """
    def add_interval(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str], arg1: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        returns false if all this interval was inside this multitude, else return true
        """
    def add_point(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        returns false if this point was inside this multitude, else return true
        """
    @typing.overload
    def any(self) -> str | None:
        """
        ### any
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        ---
        
        - If there is any point, it will be returned.
        - If there is an interval `(-INF; +INF)`, the function will return `None`.
        - If it is `mathInterval_int` or `mathInterval_float`,
          a smart algorithm will try to find any number in the intervals.
        - If it is `mathInterval_str`,
          a smart algorithm will try to find any string in the intervals,
          considering that a string may contain only **capital English letters**.
        - If it is standard `mathInterval`, or if the algorithm does not find any element in data,
          the function will return `None`.
        
        ---
        
        For custom types and algorithms, consider using this function with additional arguments.
        """
    @typing.overload
    def any(self, arg0: collections.abc.Callable[[str], str | None], arg1: collections.abc.Callable[[str], str | None], arg2: collections.abc.Callable[[str, str], str | None], arg3: str) -> str | None:
        """
        ### any()
        
        Return any element that is in data.
        
        The function can return `None`, because the returning value does not always exist.
        
        This function takes **three lambda functions** and **one value**:
        
        ---
        
        - **First lambda** – called if there is an interval `(-INF; x)`,
          receives one argument (x).
        - **Second lambda** – called if there is an interval `(x; +INF)`,
          receives one argument (x).
        - **Third lambda** – called if there is an interval `(x; y)`,
          receives two arguments (x, y).
        - **Value** - result for interval `(-INF, +INF)`
        
        ---
        
        A lambdas may return `None`, if the interval has no integer value.
        
        ⚠️ **Warning:**
        You must yourself detect that the returning value lies inside the interval.
        """
    def clear(self) -> None:
        """
        clear multitude data
        """
    def contains(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str], arg1: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        return true if interval (a, b) in multitude, else return false
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[str], str]) -> mathInterval_str:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**.
        `-INF` and `+INF` remain unchanged.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    @typing.overload
    def custom_transfer(self, arg0: collections.abc.Callable[[str], str], arg1: str, arg2: str) -> mathInterval_str:
        """
        ### custom_transfer()
        
        Transfer all elements that are in this multitude and return a new multitude.
        
        The function takes **one lambda function**
        and **two values** – the converted values of `-INF` and `+INF`.
        New values cannot themselves be `-INF` or `+INF`.
        
        ---
        
        - **Lambda** – returns a new value of a point/border of an interval,
          receives one argument - old value of a point/border of an interval.
        - **First value** – new value of the border of the interval, that begins from `-INF` - old value of a border of an interval.
        - **Second value** – new value of the border of the interval, that ends with `+INF` - old value of a border of an interval.
        
        ---
        
        If the first value of an interval becomes greater than the second,
        the function will swap them automatically.
        """
    def empty(self) -> bool:
        """
        return true if this multitude is empty, else return false
        """
    def inverse(self) -> mathInterval_str:
        """
        returns the multitude that is the inverse of the given one
        """
    def remove_interval(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str], arg1: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        returns false if all this interval was not inside this multitude, else return true
        """
    def remove_point(self, arg0: mathInterval._mathInterval_str_minimal | mathInterval._mathInterval_str_maximal | str | tuple[typing.SupportsInt, str]) -> bool:
        """
        returns false if this point was not inside this multitude, else return true
        """
