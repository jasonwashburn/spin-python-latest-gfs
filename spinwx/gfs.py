"""Spin service to find the latest complete GFS model run."""

import logging
from datetime import datetime, timedelta, timezone

MODEL_HOUR_INTERVAL = 6
NUM_EXPECTED_FORECASTS = 209
S3_BUCKET = "noaa-gfs-bdp-pds"

logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def build_s3_prefix(model_run: datetime) -> str:
    """Build the S3 prefix for the given model run.

    Args:
        model_run (datetime): The model run time.

    Returns:
        str: The S3 prefix.
    """
    year = model_run.year
    month = model_run.month
    day = model_run.day
    hour = model_run.hour
    return f"gfs.{year}{month:02}{day:02}/{hour:02}/atmos/gfs.t{hour:02}z.pgrb2.0p25"


def build_url(model_run: datetime) -> str:
    """Build the URL to list the S3 objects for the given model run.

    Args:
        model_run (datetime): The model run time.

    Returns:
        str: The URL.
    """
    prefix = build_s3_prefix(model_run=model_run)
    return f"https://{S3_BUCKET}.s3.amazonaws.com/?list-type=2&prefix={prefix}"


def calc_latest_possible_run(now: datetime) -> datetime:
    """Calculate the latest possible model run time.

    Args:
        now (datetime): The current time.

    Returns:
        datetime: The latest possible model run time.
    """
    estimated_model_delay = timedelta(hours=2)
    adjusted_base_time = now - estimated_model_delay
    hour = adjusted_base_time.hour
    run_hour = MODEL_HOUR_INTERVAL * (hour // MODEL_HOUR_INTERVAL)
    return datetime(
        year=adjusted_base_time.year,
        month=adjusted_base_time.month,
        day=adjusted_base_time.day,
        hour=run_hour,
        tzinfo=timezone.utc,
    )
