"""Rangetrees are binary trees for fast lookups in ranges."""
from enum import Enum, unique
from typing import Union, TypeVar, Generic

from bintrees import FastAVLTree

V = TypeVar('V')
D = TypeVar('D')


@unique
class InfinityMarker(Enum):
    INF_PLUS = "inf_plus"
    INF_MINUS = "inf_minus"


class RangeTree(Generic[V]):
    """A specialized tree dealing with ranges."""

    def __init__(self) -> None:
        self._tree = FastAVLTree()  # Map ints to tuples (val, Union[end, InfinityMarker])

    def __setitem__(self, key: Union[slice, range], value: V) -> None:
        """Set a value to the given interval.

        If the interval is already occupied, a ValueError will be thrown.

        Only slices and ranges with the default step (1) are supported.

        If the slice or range is inverted (end < start), the interval will be
        flipped.

        Open slices and ranges ([:1], [1:]) are supported.
        """
        if isinstance(key, (slice, range)):
            if key.step is not None and key.step != 1:
                m = 'Intervals with custom steps ({}) not' \
                    ' supported.'.format(key)
                raise ValueError(m)
        else:
            raise ValueError('Only slices and ranges supported.')
        s, e = key.start, key.stop
        if s is not None and e is not None and s > e:
            s, e = e, s

        # The check for an empty space is a little complex.
        # First check the lower bound.
        anchor = s if s is not None else e - 1
        try:
            lower_item = self._tree.floor_item(anchor)
        except KeyError:
            lower_item = None
        if lower_item is not None:
            if (s is None or
                lower_item[1][1] is InfinityMarker.INF_PLUS or
                (lower_item[1][1] is not InfinityMarker.INF_MINUS and
                 lower_item[1][1] > s)):
                raise KeyError('Overlapping intervals.')

        # Now the higher bound.
        try:
            higher_item = self._tree.ceiling_item(anchor)
        except KeyError:
            higher_item = None
        if higher_item is not None:
            if e is None or higher_item[1][1] is InfinityMarker.INF_MINUS or higher_item[0] < e:
                raise KeyError('Overlapping intervals')

        if e is None:
            e = InfinityMarker.INF_PLUS
        elif s is None:
            e = InfinityMarker.INF_MINUS

        self._tree[anchor] = (value, e)

    def __getitem__(self, key: int) -> V:
        try:
            res = self._tree.floor_item(key)
        except KeyError:
            res = self._tree.ceiling_item(key)
            val, e = res[1]
            if e is InfinityMarker.INF_MINUS:
                return val
            else:
                raise KeyError(key)

        val, e = res[1]
        if (e is InfinityMarker.INF_PLUS or
            (e is InfinityMarker.INF_MINUS and res[0] == key) or
            (e is not InfinityMarker.INF_MINUS and key < e)):
            return val
        else:
            raise KeyError(key)

    def get(self, key, default: D=None) -> Union[V, D]:
        try:
            res = self._tree.floor_item(key)
        except KeyError:
            try:
                res = self._tree.ceiling_item(key)
            except KeyError:
                return default
            val, e = res[1]
            if e is InfinityMarker.INF_MINUS:
                return val
            else:
                return default

        val, e = res[1]
        if (e is InfinityMarker.INF_PLUS or
                (e is InfinityMarker.INF_MINUS and res[0] == key) or
                (e is not InfinityMarker.INF_MINUS and key < e)):
            return val
        else:
            return default

    def __contains__(self, key: int) -> bool:
        try:
            existing = self._tree.floor_item(key)
        except KeyError:
            try:
                existing = self._tree.ceiling_item(key)
            except KeyError:
                return False
            else:
                return existing[1][1] is InfinityMarker.INF_MINUS
        else:
            start, (_, end) = existing
            if end is InfinityMarker.INF_MINUS:
                return start == key
            elif end is InfinityMarker.INF_PLUS:
                return True
            else:
                return key < end
