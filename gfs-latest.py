import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional

from spin_http import Request, Response, http_send

MODEL_HOUR_INTERVAL = 6
NUM_EXPECTED_FORECASTS = 209
S3_BUCKET = "noaa-gfs-bdp-pds"


def handle_request(request):
    latest_run = get_latest_complete_run()
    prefix = build_s3_prefix(model_run=latest_run).rsplit("/", maxsplit=1)[0]
    url = f"https://{S3_BUCKET}.s3.amazonaws.com/index.html#{prefix}/"
    response = json.dumps(
        {
            "bucket": S3_BUCKET,
            "prefix": prefix,
            "url": url.rsplit(),
            "latest_run": latest_run.isoformat(),
        }
    )
    return Response(200, [("content-type", "text/plain")], bytes(response, "utf-8"))


def build_s3_prefix(model_run: datetime) -> str:
    year = model_run.year
    month = model_run.month
    day = model_run.day
    hour = model_run.hour
    prefix = f"gfs.{year}{month:02}{day:02}/{hour:02}/atmos/gfs.t{hour:02}z.pgrb2.0p25"
    return prefix


def build_url(model_run: datetime) -> str:
    prefix = build_s3_prefix(model_run=model_run)

    url = f"https://{S3_BUCKET}.s3.amazonaws.com/?list-type=2&prefix={prefix}"
    return url


def get_available_forecasts(model_run: datetime) -> set[int]:
    url = build_url(model_run=model_run)

    resp = http_send(Request("GET", url, [], None))
    root = ET.fromstring(resp.body)
    # with requests.get(url) as resp:
    #     root = ET.fromstring(resp.text)

    xmlns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    available_keys = set()

    for key in root.iter(f"{xmlns}Key"):
        key_text = key.text
        if not key_text.endswith(".anl") and not key_text.endswith(".idx"):
            hour = key_text.rsplit(".")[-1].lstrip("f")
            available_keys.add(int(hour))

    return available_keys


def calc_latest_possible_run() -> datetime:
    estimated_model_delay = timedelta(hours=2)
    now = datetime.utcnow()
    adjusted_base_time = now - estimated_model_delay
    hour = adjusted_base_time.hour
    run_hour = MODEL_HOUR_INTERVAL * (hour // MODEL_HOUR_INTERVAL)
    model_run = datetime(
        year=adjusted_base_time.year,
        month=adjusted_base_time.month,
        day=adjusted_base_time.day,
        hour=run_hour,
    )
    return model_run


def get_latest_complete_run() -> Optional[datetime]:
    max_runs_to_try = 3
    latest_possible_run = calc_latest_possible_run()
    runs_to_try = [
        latest_possible_run - timedelta(hours=i * MODEL_HOUR_INTERVAL)
        for i in range(max_runs_to_try)
    ]

    for run in runs_to_try:
        forecasts = get_available_forecasts(model_run=run)
        if len(forecasts) == 209:
            return run
