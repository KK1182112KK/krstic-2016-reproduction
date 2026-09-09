import numpy as np
import pytest
from scipy.integrate import solve_ivp
import audit

def test_exact_held_unicycle_flow_against_ivp():
 x=np.array([.5,-.2,.3]);w=.8;v=-.9;h=.31
 y=audit.flow(x,w,v,h)
 r=solve_ivp(lambda t,z:[v*np.cos(z[2]),v*np.sin(z[2]),w],(0,h),x,rtol=1e-12,atol=1e-14,method='DOP853')
 assert abs(y-r.y[:,-1]).max()<1e-11
@pytest.mark.parametrize('h',[.02,.01,.005])
def test_zero_input_prearrival_state(h):
 r=audit.simulate(dt=h,T=2.);assert abs(r[1][r[0]<=.5]-.5).max()<1e-13

def test_first_predictor_known_initial_state():
 r=audit.simulate(T=2.);assert np.array_equal(r[3][0],[.5,.5,.5])

def test_second_initial_predictor_against_separate_ivp():
 r=audit.simulate(dt=.01,T=2.)
 sol=solve_ivp(lambda t,x:[0.,0.,audit.nominal(t,x)[0]],(.5,1.),[.5,.5,.5],rtol=1e-12,atol=1e-14,method='DOP853')
 assert abs(r[4][0]-sol.y[:,-1]).max()<1e-10

def test_initial_feedback_not_history_compatible():
 r=audit.simulate(T=2.);assert min(abs(r[2][0]))>.6

def test_first_predictor_identity_offgrid():
 r=audit.simulate(dt=.01,T=3.,D1=.503,D2=1.007)
 m=audit.metrics(r,.503,1.007);assert m['P1_identity_max_component']<1e-11

def test_second_predictor_identity_refines():
 a=audit.metrics(audit.simulate(dt=.02,T=4.),.5,1.)
 b=audit.metrics(audit.simulate(dt=.01,T=4.),.5,1.)
 assert b['P2_identity_max_component']<.51*a['P2_identity_max_component']

def test_nominal_post_delay_reference_refines():
 a=audit.metrics(audit.simulate(dt=.02,T=4.),.5,1.)
 b=audit.metrics(audit.simulate(dt=.01,T=4.),.5,1.)
 assert b['post_D2_nominal_reference_error']<.51*a['post_D2_nominal_reference_error']

def test_future_command_rejected():
 with pytest.raises(ValueError):audit.lookup(np.zeros((5,2)),.3,.1,1)

def test_prefix_independence():
 a=audit.simulate(T=2.);b=audit.simulate(T=3.)
 for x,y in zip(a,b):assert np.array_equal(x,y[:len(x)])

def test_wrong_clock_is_separate_negative_control():
 r=audit.simulate(dt=.005,T=5.,wrong_clock=True)
 m=audit.metrics(r,.5,1.);assert m['P2_identity_max_component']>.005
@pytest.mark.parametrize('kw',[{'dt':0},{'D1':2.,'D2':1.},{'x0':[1.,2.]},{'ratio':0}])
def test_invalid_parameters(kw):
 with pytest.raises(ValueError):audit.simulate(**kw)
