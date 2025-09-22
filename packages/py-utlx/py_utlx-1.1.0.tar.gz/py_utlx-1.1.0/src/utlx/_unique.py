# Copyright (c) 2012 Adam Karpierz
# SPDX-License-Identifier: Zlib

from typing import Any
from collections.abc import Callable, Iterable, Iterator
from itertools import filterfalse

__all__ = ('unique', 'iter_unique')


def unique(iterable: Iterable[Any]) -> list[Any]:
    """List unique elements, preserving order."""
    return list(dict.fromkeys(iterable))


def iter_unique(iterable: Iterable[Any],
                key: Callable[[Any], Any] | None = None) -> Iterator[Any]:
    # Borroweed from: https://docs.python.org/3/library/itertools.html
    """List unique elements, preserving order. \
    Remember all elements ever seen."""
    # iter_unique('AAAABBBCCDAABBB') --> A B C D
    # iter_unique('ABBCcAD', str.lower) --> A B C D
    seen: set[Any] = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element
