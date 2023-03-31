"""Tests for gfs_latest.py."""
from datetime import datetime, timezone

import pytest

from spinwx.gfs import build_s3_prefix, build_url, calc_latest_possible_run


def test_build_s3_prefix() -> None:
    """Test build_s3_prefix."""
    model_run = datetime(2020, 3, 1, 12, tzinfo=timezone.utc)
    expected = "gfs.20200301/12/atmos/gfs.t12z.pgrb2.0p25"
    assert build_s3_prefix(model_run) == expected


def test_build_url() -> None:
    """Test build_url."""
    model_run = datetime(2020, 3, 1, 12, tzinfo=timezone.utc)
    expected = (
        "https://noaa-gfs-bdp-pds.s3.amazonaws.com/"
        "?list-type=2&prefix=gfs.20200301/12/atmos/gfs.t12z.pgrb2.0p25"
    )
    assert build_url(model_run) == expected


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (
            datetime(2020, 3, 1, 12, tzinfo=timezone.utc),
            datetime(2020, 3, 1, 6, tzinfo=timezone.utc),
        ),
        (
            datetime(2020, 3, 1, 13, tzinfo=timezone.utc),
            datetime(2020, 3, 1, 6, tzinfo=timezone.utc),
        ),
        (
            datetime(2020, 3, 1, 14, tzinfo=timezone.utc),
            datetime(2020, 3, 1, 12, tzinfo=timezone.utc),
        ),
    ],
)
def test_calc_latest_possible_run(now: datetime, expected: datetime) -> None:
    """Test calc_latest_possible_run."""
    assert calc_latest_possible_run(now=now) == expected
