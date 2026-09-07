"""Tests for the direct original-plant solver; no paper figures are assumed."""
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from direct_dde import simulate, held_value, predictor_from_history, identity_residual


def test_zero_state_stays_zero():
    r = simulate(t_end=2, X0=(0, 0))
    np.testing.assert_array_equal(r.X, 0)
    np.testing.assert_array_equal(r.U, 0)


def test_startup_no_interpolation_ramp():
    assert held_value(-1e-10, np.array([0.]), np.array([-9.]), 0.) == 0
    assert held_value(0., np.array([0.]), np.array([-9.]), 0.) == -9
    with pytest.raises(ValueError, match='Future'):
        held_value(1.1, np.array([0., 1.]), np.array([2., 3.]), 1.)


def test_initial_predictor_against_closed_form():
    r = simulate(t_end=.1)
    np.testing.assert_allclose(r.Z[0], [2*np.e-1, np.e], rtol=2e-14)
    assert r.U[0] == pytest.approx(1-4*np.e)


def test_constant_history_spatial_ivp():
    u, D, x = -.4, .73, np.array([.5, -.2])
    z = predictor_from_history(0., x, D, np.array([]), np.array([]), u)
    sol = solve_ivp(lambda t, p: [2*p[1], (p[1]+u)/(1+u*u)],
                    (0, D), x, rtol=1e-12, atol=1e-14)
    assert sol.success
    np.testing.assert_allclose(z, sol.y[:, -1], atol=2e-12)


def test_predictor_piecewise_history_against_independent_ivps():
    times=np.array([0., .13, .37, .61]); u=np.array([-1., .2, -.5, .8])
    z=predictor_from_history(.8, np.array([1., -.3]), 1., times, u, .1)
    p=np.array([1., -.3])
    for a,b,v in zip([-.2,0.,.13,.37,.61],[0.,.13,.37,.61,.8],[.1,*u]):
        sol=solve_ivp(lambda t,y: [2*y[1],(y[1]+v)/(1+v*v)],
                      (a,b),p,rtol=1e-12,atol=1e-14)
        assert sol.success
        p=sol.y[:,-1]
    np.testing.assert_allclose(z,p,atol=2e-11)


def test_before_delay_arrival_physical_x2_is_uncontrolled():
    r = simulate(D=.73, sample_dt=.01, t_end=.73)
    np.testing.assert_allclose(r.X[:,1], np.exp(r.t), atol=2e-9)
    assert np.all(r.U_delayed[r.t < .73] == 0)
    assert r.U_delayed[-1] == pytest.approx(r.U[0])


def test_noninteger_delay_not_rounded():
    r=simulate(D=.735, sample_dt=.01, t_end=.8)
    assert np.all(r.U_delayed[r.t < .735] == 0)
    assert r.U_delayed[np.searchsorted(r.t,.74)] == pytest.approx(r.U[0])
    exact=simulate(D=.735, sample_dt=.01, t_end=.8, plant_method='exact-held')
    np.testing.assert_allclose(r.X,exact.X,atol=5e-8)


def test_rk4_original_rhs_matches_independent_exact_plant_flow():
    r=simulate(sample_dt=.01,t_end=5)
    e=simulate(sample_dt=.01,t_end=5,plant_method='exact-held')
    np.testing.assert_allclose(r.X,e.X,atol=5e-8)
    np.testing.assert_allclose(r.U,e.U,atol=2e-7)


def test_prefix_is_independent_of_future_simulation_horizon():
    short=simulate(sample_dt=.01,t_end=.5)
    long=simulate(sample_dt=.01,t_end=1.)
    np.testing.assert_array_equal(short.X,long.X[:len(short.t)])
    np.testing.assert_array_equal(short.U,long.U[:len(short.t)])


def test_refinement_against_independent_continuous_target():
    errors=[]; defects=[]
    for dt in (.02,.01,.005):
        r=simulate(sample_dt=dt,t_end=4.)
        # The reference is calculated ONLY AFTER the original plant simulation.
        def target(t,z):
            u=-z[0]-2*z[1]
            return [2*z[1]+u,(z[1]+u)/(1+u*u)]
        ref=solve_ivp(target,(0,4),r.Z[0],t_eval=r.t,rtol=1e-11,atol=1e-13)
        assert ref.success
        errors.append(np.max(np.abs(r.Z-ref.y.T)))
        defects.append(np.max(np.abs(identity_residual(r))))
    assert errors[1] < .7*errors[0] and errors[2] < .7*errors[1]
    assert defects[1] < .5*defects[0] and defects[2] < .5*defects[1]


def test_delay_changes_physical_trajectory():
    a=simulate(D=.5,t_end=1); b=simulate(D=1.,t_end=1)
    assert np.max(np.abs(a.X-b.X)) > .1


def test_partial_final_step():
    r=simulate(sample_dt=.03,t_end=.101)
    assert r.t[-1] == .101
    assert np.all(np.diff(r.t)>0)


@pytest.mark.parametrize('kwargs',[{'D':-1},{'sample_dt':0},{'t_end':0},
                                    {'X0':[1]}, {'history_value':float('nan')}])
def test_invalid_parameters(kwargs):
    with pytest.raises(ValueError):
        simulate(**kwargs)
