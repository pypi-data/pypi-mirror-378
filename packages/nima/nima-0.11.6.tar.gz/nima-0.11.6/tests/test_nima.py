"""Tests for nima module."""

from pathlib import Path

import numpy as np
import pytest
import tifffile as tff
from numpy.testing import assert_array_equal
from numpy.typing import NDArray

from nima import nima, segmentation
from nima.nima_types import DIm, ImFrame

data_fp = "./tests/data/1b_c16_15.tif"


@pytest.fixture(name="d_im")
def d_im_setup() -> dict[str, NDArray[np.float64]]:
    """Create a dict of images."""
    return {
        "C": (np.ones((5, 5, 5)) * 2).astype(np.float64),
        "C2": (np.ones((5, 5, 5)) * 4).astype(np.float64),
    }


@pytest.fixture(name="d_flat")
def d_flat_setup() -> dict[str, NDArray[np.float64]]:
    """Create a dict of flat images."""
    return {
        "C": (np.ones((5, 5)) * 2).astype(np.float64),
        "C2": (np.ones((5, 5)) * 3).astype(np.float64),
    }


@pytest.fixture(name="d_dark")
def d_dark_setup() -> dict[str, NDArray[np.float64]]:
    """Create a dict of bias images."""
    return {"C": np.ones((5, 5)), "C2": (np.ones((5, 5)) * 2).astype(np.float64)}


@pytest.fixture(name="dark")
def dark_setup() -> NDArray[np.float64]:
    """Create a dark image."""
    return np.ones((5, 5))


@pytest.fixture(name="flat")
def flat_setup() -> NDArray[np.float64]:
    """Create a flat image."""
    return (np.ones((5, 5)) * 2).astype(np.float64)


class TestDShading:
    """Test d_shading."""

    def test_single_dark_and_single_flat(
        self,
        d_im: DIm,
        dark: ImFrame,
        flat: ImFrame,
    ) -> None:
        """Test d_shading using single dark and single flat images."""
        d_cor = nima.d_shading(d_im, dark, flat, clip=True)
        assert_array_equal(d_cor["C"], np.ones((5, 5, 5)) / 2)
        assert_array_equal(d_cor["C2"], np.ones((5, 5, 5)) * 1.5)

    def test_single_dark_and_d_flat(
        self,
        d_im: DIm,
        dark: ImFrame,
        d_flat: DIm,
    ) -> None:
        """Test d_shading using single dark and a stack of flat images."""
        d_cor = nima.d_shading(d_im, dark, d_flat, clip=True)
        assert_array_equal(d_cor["C"], np.ones((5, 5, 5)) / 2)
        assert_array_equal(d_cor["C2"], np.ones((5, 5, 5)))

    def test_d_dark_and_d_flat(
        self,
        d_im: DIm,
        d_dark: DIm,
        d_flat: DIm,
    ) -> None:
        """Test d_shading using stacks of dark and flat images."""
        d_cor = nima.d_shading(d_im, d_dark, d_flat, clip=True)
        assert_array_equal(d_cor["C"], np.ones((5, 5, 5)) / 2)
        assert_array_equal(d_cor["C2"], np.ones((5, 5, 5)) * 2 / 3)


@pytest.fixture(name="im")
def im_setup() -> NDArray[np.int_] | NDArray[np.float64]:
    """Create a dict of images."""
    return np.array(tff.imread(data_fp))


class TestCalculateBg:
    """Test bg methods."""

    def test_default(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test default (arcsinh) method."""
        assert segmentation.calculate_bg(im[3, 2]).iqr[1] == 286

    def test_arcsinh(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test arcsinh method and arcsinh_perc, radius and perc arguments."""
        bg_params = segmentation.BgParams(kind="arcsinh")
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 286
        bg_params = segmentation.BgParams(kind="arcsinh", arcsinh_perc=50, radius=15)
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 287
        bg_params = segmentation.BgParams(
            kind="arcsinh", arcsinh_perc=50, radius=15, perc=20
        )
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 288

    def test_entropy(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test entropy method and radius argument."""
        bg_params = segmentation.BgParams(kind="entropy")
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 297
        bg_params = segmentation.BgParams(kind="entropy", radius=20)
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 293

    def test_adaptive(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test adaptive method and adaptive_radius argument."""
        bg_params = segmentation.BgParams(kind="adaptive")
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 287
        bg_params = segmentation.BgParams(kind="adaptive", adaptive_radius=101)
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 280

    def test_li_adaptive(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test li_arcsinh method."""
        bg_params = segmentation.BgParams(kind="li_adaptive")
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 273

    def test_li_li(self, im: NDArray[np.int_] | NDArray[np.float64]) -> None:
        """Test li_li method."""
        bg_params = segmentation.BgParams(kind="li_li")
        assert segmentation.calculate_bg(im[3, 2], bg_params).iqr[1] == 288


def test_plot_img_profile() -> None:
    """Plot summary graphics for Bias-Flat images.

    Test both lines (whole frame and central region) along x (axis=0).

    """
    sample_flat_image = Path("tests") / "data" / "output" / "test_flat_gaussnorm.tif"
    img = np.array(tff.imread(sample_flat_image))
    f = nima.plt_img_profile(img)
    _, y_plot = f.get_axes()[1].lines[0].get_xydata().T  # type: ignore[union-attr]
    ydata = np.array([1.00000001, 0.99999999, 1.00000002, 1.0, 0.99999999])
    np.testing.assert_allclose(y_plot, ydata)
    _, y_plot = f.get_axes()[1].lines[1].get_xydata().T  # type: ignore[union-attr]
    ydata = np.array([1.0, 0.99999997, 1.0, 0.99999998, 0.99999997])
    np.testing.assert_allclose(y_plot, ydata)
