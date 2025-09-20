"""Tests for nima script."""

from pathlib import Path

import numpy as np
import pandas as pd
import pypdf
import pytest
import skimage.io
import skimage.measure
import tifffile as tff
from click.testing import CliRunner, Result
from matplotlib.testing.compare import compare_images
from matplotlib.testing.exceptions import ImageComparisonFailure

from nima.__main__ import bima, main

# tests path
TESTS_PATH = Path(__file__).parent
# test data: (rootname, times)
rootnames = [("1b_c16_15", 4)]
ResultFolder = tuple[Path, tuple[str, int], Result]


def _assert_image_comparison(
    fp_expected: Path, fp_result: Path, tol: float, suffix: str = ""
) -> None:
    msg = compare_images(str(fp_expected), str(fp_result), tol)
    if msg:
        if suffix:
            rename = f"{fp_expected.stem}_{suffix}.png"
            fp_expected.with_name(rename).unlink()
        raise ImageComparisonFailure(msg)


class TestNimaOptions:
    """It checks some command line option."""

    @pytest.fixture(scope="module", params=rootnames)
    def result_folder(
        self, tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
    ) -> ResultFolder:
        """Fixture for creating results folder and opening a sub-process."""
        tmpdir = tmp_path_factory.getbasetemp()
        filename = (TESTS_PATH / "data" / request.param[0]).with_suffix(".tif")
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                str(filename),
                "G",
                "R",
                "C",
                "-o",
                str(tmpdir),
                "--bg-adaptive-radius",
                "101",
            ],
        )
        return tmpdir, request.param, result

    def test_stdout(self, result_folder: ResultFolder) -> None:
        """It outputs the correct value for 'Times'."""
        out = result_folder[2].output
        assert result_folder[2].return_value is None
        assert result_folder[2].exit_code == 0
        assert (
            int(
                next(
                    line for line in out.splitlines() if "Times:" in str(line)
                ).split()[1]
            )
            == result_folder[1][1]
        )


class TestNima:
    """It checks all output files."""

    @pytest.fixture(scope="module", params=rootnames)
    def result_folder(
        self, tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
    ) -> ResultFolder:
        """Fixture for creating results folder and opening a sub-process."""
        tmpdir = tmp_path_factory.getbasetemp()
        filename = (TESTS_PATH / "data" / request.param[0]).with_suffix(".tif")
        runner = CliRunner()
        result = runner.invoke(main, [str(filename), "G", "R", "C", "-o", str(tmpdir)])
        return tmpdir, request.param, result

    def test_stdout(self, result_folder: ResultFolder) -> None:
        """It outputs the correct value for 'Times'."""
        out = result_folder[2].output
        assert result_folder[2].return_value is None
        assert result_folder[2].exit_code == 0
        assert (
            int(
                next(
                    line for line in out.splitlines() if "Times:" in str(line)
                ).split()[1]
            )
            == result_folder[1][1]
        )

    @pytest.mark.parametrize("f", ["bg.csv", "label1.csv", "label2.csv", "label3.csv"])
    def test_csv(self, result_folder: ResultFolder, f: str) -> None:
        """It checks csv tables."""
        fp_expected = TESTS_PATH / "data" / "output" / result_folder[1][0] / f
        fp_result = result_folder[0] / result_folder[1][0] / f
        expected = pd.read_csv(fp_expected)
        result = pd.read_csv(fp_result)
        pd.testing.assert_frame_equal(expected, result, atol=1e-15)

    @pytest.mark.parametrize(
        "f",
        [
            "label1_rpH.tif",
            "label1_rcl.tif",
            "label2_rpH.tif",
            "label2_rcl.tif",
            "label3_rpH.tif",
            "label3_rcl.tif",
        ],
    )
    def test_tif(self, result_folder: ResultFolder, f: str) -> None:
        """It checks tif files: r_Cl, r_pH of segmented cells."""
        fp_expected = TESTS_PATH / "data" / "output" / result_folder[1][0] / f
        fp_result = result_folder[0] / result_folder[1][0] / f
        expected = skimage.io.imread(fp_expected)
        result = skimage.io.imread(fp_result)
        assert np.sum(result - expected) == pytest.approx(0, 2.3e-06)

    @pytest.mark.parametrize(("f", "tol"), [("_dim.png", 8.001), ("_meas.png", 20)])
    def test_png(self, result_folder: ResultFolder, f: str, tol: float) -> None:
        """It checks png files: saved segmentation and analysis."""
        fp_expected = TESTS_PATH / "data" / "output" / "".join([result_folder[1][0], f])
        fp_result = result_folder[0] / "".join((result_folder[1][0], f))
        _assert_image_comparison(fp_expected, fp_result, tol)

    @pytest.mark.parametrize(
        ("text", "filename"),
        [
            ("262.0, 273.0, 284.0", "bg-C-li_adaptive.pdf"),
            ("423.0, 460.0, 528.0", "bg-G-li_adaptive.pdf"),
            ("237.0, 248.0, 264.0", "bg-R-li_adaptive.pdf"),
        ],
    )
    def test_pdf(self, result_folder: ResultFolder, text: str, filename: str) -> None:
        """It checks pdf files: saved bg estimation."""
        fp_result = result_folder[0] / result_folder[1][0] / filename
        page4 = pypdf.PdfReader(fp_result).pages[3]
        assert text in page4.extract_text()


@pytest.fixture
def run_bima(tmp_path: Path) -> Path:
    """Run `bima mflat` saving output in the temporary path."""
    filename = Path("tests") / "data" / "test_flat*.tif"
    runner = CliRunner()
    result = runner.invoke(
        bima, ["-o", str(tmp_path / "ff.tif"), "mflat", str(filename)]
    )
    assert str(3) in result.output
    assert (tmp_path / "ff-raw.tif").exists(), "ff-raw.tif was not created"
    return tmp_path


def test_bias_mflat(run_bima: Path) -> None:
    """Check `bias dflat` cli."""
    d = run_bima
    tmpflt = d / "ff.tif"
    tmpraw = d / "ff-raw.tif"
    # Verify that the raw output file exists
    assert tmpraw.exists(), f"Test file not found: {tmpraw}"
    # Load the test data
    test_raw = tff.imread(tmpraw)
    expect_raw = np.array(tff.imread(TESTS_PATH / "data" / "output" / "test_flat.tif"))
    np.testing.assert_allclose(np.array(test_raw), expect_raw)
    # Verify the processed output file
    test_flt = np.array(tff.imread(tmpflt))
    expect_flt = np.array(
        tff.imread(TESTS_PATH / "data" / "output" / "test_flat_gaussnorm.tif")
    )
    np.testing.assert_allclose(test_flt, expect_flt)
    # Ensure the PNG file is created
    assert tmpflt.with_suffix(".png").exists()
