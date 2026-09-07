import sys
from pathlib import Path
import numpy as np
import pytest
from scipy.optimize import brentq
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'state-delay-2012'))
from direct_state_delay import simulate


def test_oscillatory_initial_predictor_clock_identity():
    r=simulate(dt=.01,t_end=.02,factor=2)
    p0=brentq(lambda p:p-1.-.1*.3*np.sin(15*p)**2,1.,1.03,xtol=1e-14)
    assert r.P[0] == pytest.approx(p0,abs=2e-9)


def test_physical_state_before_first_arrival():
    r=simulate(dt=.002,t_end=.06)
    np.testing.assert_allclose(r.X[:,0],1.+.1*r.t,atol=3e-14)


def test_printed_and_corrected_are_not_silently_reconciled():
    a=simulate(dt=.01,t_end=.1,factor=1)
    b=simulate(dt=.01,t_end=.1,factor=2)
    assert abs(a.P[0]-b.P[0])>1e-5
    assert a.parameters['factor']==1 and b.parameters['factor']==2
    np.testing.assert_allclose(a.phi,a.t-.3*np.sin(15*a.X[:,0])**2)
    np.testing.assert_allclose(b.phi,b.t-.3*np.sin(15*b.X[:,0])**2)


def test_cooling_history_preserved():
    a=simulate(example='cooling',dt=.01,t_end=.02,x2_history=.2)
    b=simulate(example='cooling',dt=.01,t_end=.02,x2_history=.6)
    assert a.X[0,1]==.2 and b.X[0,1]==.6
    assert abs(a.U[0]-b.U[0])>.1


def test_continuous_target_residual_refines():
    errors=[]
    for dt in (.02,.01,.005):
        r=simulate(dt=dt,t_end=.4,factor=2)
        z=r.X[:,1]+.5*r.P
        # Postprocessing only, never used to evolve the physical states.
        errors.append(np.max(np.abs(z-z[0]*np.exp(-.5*r.t))))
    assert errors[1]<.7*errors[0] and errors[2]<.7*errors[1]


def test_no_horizon_anticipation():
    a=simulate(dt=.01,t_end=.1); b=simulate(dt=.01,t_end=.2)
    np.testing.assert_array_equal(a.X,b.X[:len(a.t)])


@pytest.mark.parametrize('kw',[{'dt':0},{'factor':3},{'example':'other'},
                              {'example':'cooling','x2_history':-.1}])
def test_invalid_parameters(kw):
    with pytest.raises(ValueError): simulate(**kw)
