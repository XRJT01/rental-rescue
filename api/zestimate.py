import os
import json
import zillow

ZWS_ID = os.getenv("ZWS_ID")

def split_address(full_address: str):
    parts = [p.strip() for p in full_address.split(",")]
    if len(parts) < 2:
        return None, None
    address = parts[0]
    citystatezip = ", ".join(parts[1:])
    return address, citystatezip

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }

    if not ZWS_ID:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "ZWS_ID missing on server"})
        }

    try:
        payload = json.loads(request.body or "{}")
        full_address = (payload.get("address") or "").strip()
        address, citystatezip = split_address(full_address)

        if not address or not citystatezip:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid address format"})
            }

        api = zillow.ValuationApi()
        search = api.GetSearchResults(ZWS_ID, address, citystatezip)
        zpid = search.zpid
        zestimate = search.zestimate.amount if search.zestimate else None

        if not zestimate and zpid:
            detail = api.GetZEstimate(ZWS_ID, zpid)
            zestimate = detail.zestimate.amount if detail.zestimate else None

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "zpid": zpid,
                "zestimate": zestimate
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }