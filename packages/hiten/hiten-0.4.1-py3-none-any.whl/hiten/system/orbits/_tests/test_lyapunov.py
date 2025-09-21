import numpy as np
import pytest

from hiten.system.base import System
from hiten.system.body import Body
from hiten.system.orbits.lyapunov import LyapunovOrbit
from hiten.utils.constants import Constants


@pytest.fixture
def system():
    earth_mass = Constants.get_mass("earth")
    earth_radius = Constants.get_radius("earth")
    moon_mass = Constants.get_mass("moon")
    moon_radius = Constants.get_radius("moon")
    distance = Constants.get_orbital_distance("earth", "moon")

    earth = Body("Earth", earth_mass, earth_radius, color="blue")
    moon = Body("Moon", moon_mass, moon_radius, color="gray", _parent_input=earth)

    return System(earth, moon, distance)

@pytest.fixture
def l1_orbit(system):
    return LyapunovOrbit(system.get_libration_point(1), amplitude_x=4e-3)

@pytest.fixture
def l2_orbit(system):
    return LyapunovOrbit(system.get_libration_point(2), amplitude_x=4e-3)

def test_lyapunov_orbit_ic(l1_orbit, l2_orbit):
    assert l1_orbit.initial_state.shape == (6,), "Initial state should be a 6-element vector"
    assert l2_orbit.initial_state.shape == (6,), "Initial state should be a 6-element vector"
    
    l1_position = l1_orbit.libration_point.position[0]
    assert abs(l1_orbit.initial_state[0] - l1_position) < 0.1, f"L1 orbit x ({l1_orbit.initial_state[0]}) should be near L1 position ({l1_position})"
    
    l2_position = l2_orbit.libration_point.position[0]
    assert abs(l2_orbit.initial_state[0] - l2_position) < 0.1, f"L2 orbit x ({l2_orbit.initial_state[0]}) should be within 0.1 of L2 position ({l2_position})"
    
    assert abs(l1_orbit.initial_state[1]) < 1e-10, "Y coordinate should be approximately zero for planar Lyapunov orbit"
    assert abs(l2_orbit.initial_state[1]) < 1e-10, "Y coordinate should be approximately zero for planar Lyapunov orbit"

def test_lyapunov_correct(l1_orbit):
    initial_state_before = l1_orbit.initial_state.copy()
    
    l1_orbit.correct()
    
    assert not np.array_equal(l1_orbit.initial_state, initial_state_before), "Initial state should change after correction"
    
    assert l1_orbit.period > 0, "Period should be positive after correction"
    
    assert abs(l1_orbit.initial_state[1]) < 1e-10, "Y coordinate should still be approximately zero after correction"

def test_lyapunov_orbit_propagation(l1_orbit):
    l1_orbit.correct()
    l1_orbit.propagate()
    
    assert l1_orbit.trajectory is not None, "Trajectory should be generated after propagation"
    assert len(l1_orbit.trajectory) > 0, "Trajectory should not be empty"
    
    assert np.allclose(l1_orbit.trajectory[0, :6], l1_orbit.initial_state), "Trajectory should start at initial state"
    
    final_state = l1_orbit.trajectory[-1, :6]
    initial_state = l1_orbit.initial_state
    position_close = np.allclose(final_state[:3], initial_state[:3], rtol=1e-2, atol=1e-2)
    assert position_close, "Trajectory should approximately return to initial position after one period"

def test_lyapunov_orbit_stability(l1_orbit):
    l1_orbit.correct()
    l1_orbit.propagate()
    l1_orbit.compute_stability()
    
    assert l1_orbit.stability_info is not None, "Stability info should be computed"
    _stability_indices, stability_eigvals = l1_orbit.stability_info
    
    assert len(_stability_indices) >= 1, "Should have at least one stability index"
    
    assert isinstance(_stability_indices[0], complex), "Stability indices should be complex numbers"
    
    assert isinstance(l1_orbit.is_stable, (bool, np.bool_)), "is_stable should be convertible to a boolean"

def test_lyapunov_base_class(l1_orbit):
    l1_orbit.correct()
    l1_orbit.propagate()
    l1_orbit.compute_stability()
    
    assert isinstance(l1_orbit.jacobi_constant, float), "Jacobi constant should be a float"
    
    assert isinstance(l1_orbit.energy, float), "Energy should be a float"
    
    assert l1_orbit.energy < 0, "Energy should be negative for a bound orbit"
