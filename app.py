from spin_http import Response, Request, http_send
import xml.etree.ElementTree as ET
import datetime as dt

def handle_request(request):

    response_str = try_https()

    return Response(200,
                    [("content-type", "text/plain")],
                    bytes(response_str, "utf-8"))


def try_https() -> str:
    response = http_send(Request("GET", "https://noaa-gfs-bdp-pds.s3.amazonaws.com/?list-type=2&prefix=gfs.20230331/00/atmos/gfs.t00z.pgrb2.0p25.f&delimiter=/",[],None))
     
    tree = ET.fromstring(response.body)
    response = [thing for thing in tree.iter("Key")]
    return f"{response}"

    