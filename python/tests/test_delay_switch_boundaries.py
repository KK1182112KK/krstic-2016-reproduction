"""Regression tests for right-continuous delayed-command output timestamps.

The oracle scans issued commands in physical arrival-time coordinates. It does
not subtract the delay or use a tolerance that could advance a command early.
"""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from direct_dde import simulate


@pytest.mark.parametrize('D,dt,end', [
    (1.0, .01, 3.0), (.735, .01, 1.0), (0.0, .01, .3),
    (2.0, .01, .3), (.006, .01, .053),
])
@pytest.mark.parametrize('prehistory', [0.0, -.4])
def test_delayed_output_uses_issued_command_arrivals(D, dt, end, prehistory):
    r = simulate(D=D, sample_dt=dt, t_end=end, history_value=prehistory)
    expected = np.full(len(r.t), prehistory)
    for k, now in enumerate(r.t):
        for j in range(k + 1):
            if r.t[j] + D <= now:
                expected[k] = r.U[j]
    np.testing.assert_array_equal(r.U_delayed, expected)


def test_subtraction_roundoff_at_1_point_2_does_not_select_previous_command():
    r = simulate(D=1.0, sample_dt=.01, t_end=1.2)
    j = int(np.flatnonzero(r.t == .2)[0])
    assert r.t[-1] == r.t[j] + r.D
    # IEEE float subtraction lands to the left; arrival-time lookup must not.
    assert r.t[-1] - r.D < r.t[j]
    assert r.U_delayed[-1] == r.U[j]


def test_no_epsilon_tolerance_advances_startup_command():
    D = np.nextafter(1.2, np.inf)
    r = simulate(D=D, sample_dt=.01, t_end=1.2, history_value=-.4)
    np.testing.assert_array_equal(r.U_delayed, -.4)
