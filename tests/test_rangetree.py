"""Tests for the rangetree module"""
from collections import defaultdict

import pytest
from hypothesis import assume
from hypothesis.stateful import (RuleBasedStateMachine,
                                 run_state_machine_as_test, rule, precondition)
from hypothesis.strategies import (integers, tuples, just, sampled_from,
                                   one_of, text, data)
from rangetree import RangeTree


def test_rangetree_stateful():
    """A stateful Hypothesis property test for the RangeTree."""
    ranges = integers().flatmap(lambda s: tuples(just(s),
                                                 integers(min_value=s,
                                                          max_value=s+10000)))
    flipped_ranges = ranges.map(lambda t: (t[1], t[0]))

    all_ranges = one_of(ranges, flipped_ranges)

    inf_ranges = integers().flatmap(lambda i: tuples(just(i), sampled_from(['+', '-'])))

    class RangeTreeStateful(RuleBasedStateMachine):
        def __init__(self):
            super().__init__()
            self.rt = RangeTree()
            self.oracle = defaultdict(list)
            self.inf_plus = []
            self.inf_minus = []

        @rule(r=inf_ranges, val=integers())
        def add_open_interval(self, r, val):
            anchor, direction = r
            try:
                if direction == '+':
                    self.rt[anchor:] = val
                    self.inf_plus.append(anchor)
                else:
                    self.rt[:anchor] = val
                    self.inf_minus.append(anchor - 1)
            except Exception:
                pass

        @rule(r=all_ranges, val=integers(), type_=sampled_from(['slice', 'range']))
        def add_interval(self, r, val, type_):
            """Add a range or slice to a rangetree."""
            try:
                if type_ == 'slice':
                    self.rt[r[0]:r[1]] = val
                else:
                    self.rt[range(*r)] = val
            except KeyError:
                pass
            else:
                for i in range(min(*r), max(*r)):
                    self.oracle[i].append(val)

        @rule(r=all_ranges, val=integers(), type_=sampled_from(['slice', 'range']),
              step=integers())
        def add_interval_step(self, r, val, type_, step):
            """Add a range or slice with a non-default step to a rangetree."""
            assume(step != 1)
            with pytest.raises(ValueError):
                if type_ == 'slice':
                    self.rt[r[0]:r[1]:step] = val
                else:
                    self.rt[range(*r, step)] = val

        @rule()
        @precondition(lambda self: self.inf_plus or self.inf_minus)
        def assert_open_intervals(self):
            assert len(self.inf_plus) <= 1
            assert len(self.inf_minus) <= 1
            if self.inf_plus and self.inf_minus:
                assert self.inf_plus[0] > self.inf_minus[0]

        @rule(key=one_of(text(), integers()))
        def assert_only_slices_and_ranges(self, key):
            with pytest.raises(ValueError):
                self.rt[key] = 1

        @rule(key=integers())
        def assert_missing(self, key):
            assume(key not in self.oracle)
            assume(not self.inf_plus or self.inf_plus[0] > key)
            assume(not self.inf_minus or self.inf_minus[0] < key)

            with pytest.raises(KeyError):
                self.rt[key]

            assert self.rt.get(key) is None
            o = object()
            assert self.rt.get(key, o) is o
            assert key not in self.rt

        @rule()
        def assert_no_overlap(self):
            for k, v in self.oracle.items():
                assert len(v) == 1, "Overlap at {}".format(k)

        @rule()
        def assert_matches_oracle(self):
            for k, v in self.oracle.items():
                assert k in self.rt
                assert self.rt[k] == v[0]
                assert self.rt.get(k) == v[0]

        @rule(data=data())
        @precondition(lambda self: self.inf_plus and not self.oracle)
        def assert_open_overlap_plus_contains(self, data):
            anchor = self.inf_plus[0]
            value_in = data.draw(integers(min_value=anchor))
            assert value_in in self.rt
            assert self.rt[value_in] is not None
            assert self.rt.get(value_in) == self.rt[value_in]

            if self.inf_minus:
                anchor_minus = self.inf_minus[0]
                if anchor_minus + 1 == anchor:
                    return
                value_out = data.draw(integers(min_value=anchor_minus + 1,
                                               max_value=anchor-1))
            else:
                value_out = data.draw(integers(max_value=anchor-1))
            assert value_out not in self.rt
            with pytest.raises(KeyError):
                self.rt[value_out]
            assert self.rt.get(value_out, -1) == -1

        @rule(data=data())
        @precondition(lambda self: self.inf_minus and not self.oracle)
        def assert_open_overlap_minus_contains(self, data):
            anchor = self.inf_minus[0]
            value_in = data.draw(integers(max_value=anchor))
            assert value_in in self.rt
            assert self.rt[value_in] is not None
            assert self.rt.get(value_in) == self.rt[value_in]

            if self.inf_plus:
                anchor_plus = self.inf_plus[0]
                if anchor + 1 == anchor_plus:
                    return
                value_out = data.draw(integers(min_value=anchor+1,
                                               max_value=anchor_plus-1))
            else:
                value_out = data.draw(integers(min_value=anchor+1))
            assert value_out not in self.rt
            with pytest.raises(KeyError):
                self.rt[value_out]
            assert self.rt.get(value_out, -1) == -1

    run_state_machine_as_test(RangeTreeStateful)
