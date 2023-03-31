"""Tests for gfs_latest.py."""
from datetime import datetime, timezone

from spinwx.gfs import build_s3_prefix, build_url


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
