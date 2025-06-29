# backported from current master
def _filter_request_fields(req):
    """Return only the parts that belong to the request.."""
    return {k: v for k, v in req.items() if k in ["did", "siid", "piid"]}
