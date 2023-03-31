"""Spin service to find the latest complete GFS model run."""

import json
import logging
from datetime import datetime, timedelta
from xml.etree import ElementTree

from spin_http import Request, Response, http_send
from spinwx.gfs import build_s3_prefix, build_url, calc_latest_possible_run

MODEL_HOUR_INTERVAL = 6
NUM_EXPECTED_FORECASTS = 209
S3_BUCKET = "noaa-gfs-bdp-pds"

logging.basicConfig(
    format="%(levelname)s: %(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)


def handle_request(request: Request) -> Response:
    """Handle a request.

    Args:
        request (Request): The request.

    Returns:
        Response: The response.
    """
    logging.info(
        'Received Request: {"route": %s, "host": %s}',
        request.uri,
        request.headers[0][1],
    )
    latest_run = get_latest_complete_run()
    prefix = build_s3_prefix(model_run=latest_run).rsplit("/", maxsplit=1)[0]
    url = f"https://{S3_BUCKET}.s3.amazonaws.com/index.html#{prefix}/"
    response = json.dumps(
        {
            "bucket": S3_BUCKET,
            "prefix": prefix,
            "url": url.rsplit(),
            "latest_run": latest_run.isoformat(),
        },
    )
    return Response(200, [("content-type", "text/plain")], bytes(response, "utf-8"))


def get_available_forecasts(model_run: datetime) -> set[int]:
    """Get the available forecasts for the given model run.

    Args:
        model_run (datetime): The model run time.

    Returns:
        set[int]: The available forecasts.
    """
    url = build_url(model_run=model_run)

    resp = http_send(Request("GET", url, [], None))
    root = ElementTree.fromstring(resp.body)

    xmlns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
    available_keys = set()

    for key in root.iter(f"{xmlns}Key"):
        key_text = key.text
        if not key_text.endswith(".anl") and not key_text.endswith(".idx"):
            hour = key_text.rsplit(".")[-1].lstrip("f")
            available_keys.add(int(hour))

    return available_keys


def get_latest_complete_run() -> datetime | None:
    """Find the latest complete model run.

    Returns:
        datetime | None: The latest complete model run, or None if no complete
            model run was found.
    """
    max_runs_to_try = 3
    latest_possible_run = calc_latest_possible_run()
    runs_to_try = [
        latest_possible_run - timedelta(hours=i * MODEL_HOUR_INTERVAL)
        for i in range(max_runs_to_try)
    ]

    for run in runs_to_try:
        forecasts = get_available_forecasts(model_run=run)
        num_forecasts = len(forecasts)
        if num_forecasts == NUM_EXPECTED_FORECASTS:
            logging.info(
                "Found COMPLETE (%d forecasts) run: %s",
                num_forecasts,
                run.isoformat(),
            )
            return run
        logging.info(
            "Found incomplete (%d forecasts) run: %s",
            num_forecasts,
            run.isoformat(),
        )
    return None
