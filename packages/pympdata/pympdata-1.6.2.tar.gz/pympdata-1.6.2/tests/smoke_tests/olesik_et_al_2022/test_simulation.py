# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import warnings

import numpy as np
import pytest
from numba.core.errors import NumbaExperimentalFeatureWarning
from PyMPDATA_examples.Olesik_et_al_2022.analysis import compute_figure_data
from PyMPDATA_examples.Olesik_et_al_2022.coordinates import x_id, x_log_of_pn, x_p2
from PyMPDATA_examples.Olesik_et_al_2022.settings import (
    Settings,
    default_GC_max,
    default_nr,
)
from PyMPDATA_examples.Olesik_et_al_2022.simulation import Simulation

from PyMPDATA.options import Options

settings = Settings()
grid_layout_set = (x_id(), x_p2(), x_log_of_pn(r0=1, n=1))
opt_set = (
    {"n_iters": 1},
    {"n_iters": 2, "nonoscillatory": True},
    {
        "n_iters": 3,
        "third_order_terms": True,
        "infinite_gauge": True,
        "nonoscillatory": True,
    },
)


@pytest.fixture(scope="module")
def data():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=NumbaExperimentalFeatureWarning)
        result, _ = compute_figure_data(
            nr=default_nr,
            GC_max=default_GC_max,
            psi_coord=x_id(),
            grid_layouts=grid_layout_set,
            opt_set=opt_set,
        )
    return result


@pytest.mark.parametrize(
    "psi_coord", [x_id(), x_p2(), x_log_of_pn(r0=1 * settings.si.um, n=1)]
)
@pytest.mark.parametrize("grid_layout", [x_id(), x_p2(), x_log_of_pn(r0=1, n=3)])
@pytest.mark.parametrize("nonoscillatory", [False, True])
def test_init(grid_layout, psi_coord, nonoscillatory):
    # Arrange
    opts = Options(nonoscillatory=nonoscillatory)

    # Act
    simulation = Simulation(
        settings,
        grid_layout=grid_layout,
        GC_max=default_GC_max,
        psi_coord=psi_coord,
        opts=opts,
    )
    simulation.step(1)

    # Asserts for array shapes
    assert simulation.n_of_r.shape[0] == settings.nr

    # Asserts for Jacobian
    g_factor_with_halo = simulation.solver.g_factor.data
    assert np.isfinite(g_factor_with_halo).all()
    if isinstance(psi_coord, type(grid_layout)):
        np.testing.assert_array_almost_equal(np.diff(g_factor_with_halo), 0)
    else:
        assert (np.diff(g_factor_with_halo) >= 0).all() or (
            np.diff(g_factor_with_halo) <= 0
        ).all()


@pytest.mark.parametrize("grid_layout", grid_layout_set)
@pytest.mark.parametrize("opts", opt_set)
# pylint: disable-next=redefined-outer-name
def test_n_finite(grid_layout, opts, data):
    # Arrange
    grid_layout_str = grid_layout.__class__.__name__
    psi = data[grid_layout_str]["numerical"][str(opts)][-1].magnitude

    # Assert
    assert np.isfinite(psi).all()
    assert 69 < np.amax(psi) < 225


@pytest.mark.parametrize("grid_layout", grid_layout_set)
@pytest.mark.parametrize("opts", opt_set)
# pylint: disable-next=redefined-outer-name
def test_error_norm_finite(grid_layout, opts, data):
    # Arrange
    grid_layout_str = grid_layout.__class__.__name__
    sut = data[grid_layout_str]["error_L2"][str(opts)]

    # Assert
    assert np.isfinite(sut).all()
