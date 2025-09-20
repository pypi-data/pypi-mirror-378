# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import numpy as np
import pint
import pytest
from PyMPDATA_examples.Olesik_et_al_2022.coordinates import x_id, x_log_of_pn, x_p2

si = pint.UnitRegistry()


@pytest.mark.parametrize("k", [0, 1, 2, 3])
@pytest.mark.parametrize("coord", [x_id(), x_log_of_pn(r0=1 * si.um, n=1), x_p2()])
def test_moment_of_r_integral(k, coord):
    # Arrange
    r_0 = 2 * si.um
    r_1 = 4 * si.um

    # Act
    with np.errstate(divide="ignore", invalid="ignore"):
        integral = coord.moment_of_r_integral(
            coord.x(r_1), k
        ) - coord.moment_of_r_integral(coord.x(r_0), k)

    # Assert
    if coord.__class__ == x_id:
        assert integral.check(f"[length]**{k+1}")
    elif coord.__class__ == x_p2:
        assert integral.check(f"[length]**{k+2}")
    elif coord.__class__ == x_log_of_pn:
        assert integral.check(f"[length]**{k}")
