import numpy as np
import pytest
from audit import *

def test_gauss_quadrature_independent_polynomial():
 assert abs(integ(lambda t:t**4,0,1)-.2)<1e-13
@pytest.mark.parametrize('k',[1.,2.])
def test_oscillator_general_reduction(k):
 _,m=oscillator(h=.02,kappa=k);assert m['derived_error']<3e-8

def test_printed_oscillator_missing_inverse_kappa():
 _,m=oscillator(h=.02,kappa=2.);assert m['printed_error']>1.

def test_population_original_memory_equations():
 _,m=population(h=.01);assert m['x_error']<2e-6 and m['y_error']<2e-6

def test_mixed_measure_reduction():
 _,m=mixed(h=.02);assert m['identity_error']<1e-8

def test_mixed_quadrature_independence():
 a,_=mixed(h=.04,nq=24);b,_=mixed(h=.04,nq=48);assert abs(a-b).max()<1e-12

def test_time_varying_source_arguments_kept_separate():
 _,m=time_varying(h=.02);assert m['derived_error']<1e-9 and m['printed_error']>.6

def test_proportional_delay_transform():
 _,m=proportional(h=.02);assert m['identity_error']<1e-8

def test_folded_map_general_vs_printed_example():
 _,m=folded(h=.005);assert m['derived_error']<1e-9 and m['printed_error']>.28

def test_folded_inverse_roots_directly():
 t=.1;correct=np.array([(1-np.sqrt(1-4*t))/2,(1+np.sqrt(1-4*t))/2]);printed=np.array([.5-np.sqrt(1-4*t),.5+np.sqrt(1-4*t)])
 assert abs(correct*(1-correct)-t).max()<1e-14
 assert abs(printed*(1-printed)-t).min()>.1
@pytest.mark.parametrize('delay',[.6,.613])
def test_sampled_scalar_same_command_identity(delay):
 _,m=closed_loop(h=.02,delay=delay);assert m['same_input_identity_error']<1e-7

def test_feedback_sampling_refines():
 _,a=closed_loop(h=.04);_,b=closed_loop(h=.02)
 assert b['continuous_feedback_reference_error']<.51*a['continuous_feedback_reference_error']

def test_sample_hold_even_multiple_counterexample():
 a,m=sampled_oscillator();r=m['ranks'][3]
 assert r['continuous_rank']==2 and r['sampled_rank']==0
 assert np.linalg.norm(np.array(m['final_physical_state'])-[1.,0.])<1e-12

def test_oscillator_step_refinement():
 _,a=oscillator(h=.04,kappa=2.);_,b=oscillator(h=.02,kappa=2.)
 assert a['derived_error']/b['derived_error']>14
