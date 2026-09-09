import numpy as np
import pytest
import audit

@pytest.mark.parametrize('h',[.1,.05,.025])
def test_linear_unforced_prearrival_original_plant(h):
    t,x,p,u,d=audit.simulate(dt=h,T=5.)
    assert max(abs(x-(.1-.005*t)))<1e-12

def test_independent_exact_first_arrival():
    a=audit.initial_arithmetic()
    assert abs(a['linear_first_incoming_arrival_seconds']-10.3448275862)<1e-8

def test_nonlinear_zero_input_prearrival():
    t,x,p,u,d=audit.simulate(dt=.025,T=2.,nonlinear=True)
    assert max(abs(x-(-.15/(1+.15*t))))<1e-10

def test_future_issued_history_is_rejected():
    with pytest.raises(ValueError):audit.hist(np.zeros((10,2)),1.,0,.1,0,0.)

def test_initial_linear_gain_specialization_is_distinct():
    a=audit.simulate(dt=.05,T=.1,variant='printed_product')
    b=audit.simulate(dt=.05,T=.1,variant='gain_only')
    assert abs(a[2][0,1]-b[2][0,1])>5e-5
    assert a[2][0,0]==b[2][0,0]

def test_literal_composed_g1_identity_counterexample():
    r=audit.exact_algebra_counterexample()['rows']
    assert r[0]['printed_identity_error']>1e-5
    assert abs(r[0]['clock_consistent_identity_error'])<1e-12
    assert abs(r[0]['printed_identity_error']-r[2]['printed_identity_error'])<1e-10

def test_globally_ordered_positive_diagnostic_delays():
    x=np.linspace(-100,100,1001);d1=.3+.15*np.tanh(x);d2=.6+.3*np.tanh(x)
    assert np.all(d1>0) and np.all(d2>d1)

def test_output_history_independent_of_horizon():
    a=audit.simulate(dt=.05,T=1.)
    b=audit.simulate(dt=.05,T=2.)
    for x,y in zip(a,b):assert np.array_equal(x,y[:len(x)])

def test_reported_initial_nonlinear_delay_arithmetic():
    a=audit.initial_arithmetic()
    assert abs(a['nonlinear_initial_delays_km_second_interpretation'][0]-2.109375)<1e-12
    assert abs(a['nonlinear_initial_D1_meter_second_literal']-28.125)<1e-12

@pytest.mark.parametrize('params',[dict(dt=0),dict(variant='silent_fix'),dict(spatial_ratio=-1)])
def test_invalid_parameters_fail(params):
    with pytest.raises(ValueError):audit.simulate(**params)
