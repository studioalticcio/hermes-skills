#!/usr/bin/env python3
"""Tiny CLI for mobiliteit.lu / cdt.hafas.de HAFAS API."""
import argparse
import datetime as dt
import json
import os
import urllib.request

GATE = "https://cdt.hafas.de/gate"
AID = os.environ.get("MOBILITEIT_AID", "SkC81GuwuzL4e0")
CLIENT = {"id": "MMILUX", "type": "WEB", "name": "webapp", "l": "vs_webapp"}
VER = "1.77"


def gate(svc_req_l, lang="eng"):
    payload = {"lang": lang, "ver": VER, "auth": {"type": "AID", "aid": AID}, "client": CLIENT, "svcReqL": svc_req_l}
    req = urllib.request.Request(
        GATE,
        data=json.dumps(payload, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "mobiliteit-cli/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def svc_res(obj, idx=0):
    if obj.get("err") and obj.get("err") != "OK":
        raise SystemExit(json.dumps(obj, indent=2, ensure_ascii=False))
    res_l = obj.get("svcResL") or []
    if not res_l:
        raise SystemExit("No service response")
    item = res_l[idx]
    if item.get("err") and item.get("err") != "OK":
        raise SystemExit(json.dumps(item, indent=2, ensure_ascii=False))
    return item.get("res") or {}


def locmatch(query, loc_type="S", max_results=10, lang="eng"):
    req = {"input": {"field": "S", "loc": {"name": query, "type": loc_type}}}
    obj = gate([{"meth": "LocMatch", "req": req}], lang=lang)
    res = svc_res(obj)
    return (((res.get("match") or {}).get("locL")) or [])[:max_results]


def fmt_crd(crd):
    if not crd:
        return ""
    return f"{crd.get('y', 0)/1e6:.6f},{crd.get('x', 0)/1e6:.6f}"


def cmd_search(args):
    locs = locmatch(args.query, args.type, args.max, args.lang)
    if args.json:
        print(json.dumps(locs, indent=2, ensure_ascii=False))
        return
    for i, loc in enumerate(locs, 1):
        print(f"{i:2}. {loc.get('name')}  [{loc.get('type')}] extId={loc.get('extId','')} {fmt_crd(loc.get('crd'))}")
        print(f"    lid={loc.get('lid')}")


def resolve_stop(value):
    if value.startswith("A="):
        return {"lid": value}
    if value.isdigit():
        return {"extId": value}
    locs = locmatch(value, "S", 1)
    if not locs:
        raise SystemExit(f"No stop found for {value!r}")
    return locs[0]


def parse_when(date_s=None, time_s=None):
    now = dt.datetime.now()
    day = dt.datetime.strptime(date_s, "%Y-%m-%d").date() if date_s else now.date()
    if time_s:
        if len(time_s.split(":")) == 2:
            time_s += ":00"
        t = dt.datetime.strptime(time_s, "%H:%M:%S").time()
    else:
        t = now.time().replace(microsecond=0)
    return day.strftime("%Y%m%d"), t.strftime("%H%M%S")


def product_name(common, prod_x):
    try:
        return common.get("prodL", [])[prod_x].get("name")
    except Exception:
        return ""


def loc_name(common, loc_x):
    try:
        return common.get("locL", [])[loc_x].get("name")
    except Exception:
        return ""


def cmd_departures(args):
    loc = resolve_stop(args.stop)
    date, time = parse_when(args.date, args.time)
    stb_loc = {"lid": loc["lid"]} if loc.get("lid") else {"extId": loc["extId"]}
    req = {"stbLoc": stb_loc, "type": "ARR" if args.arrivals else "DEP", "date": date, "time": time, "maxJny": args.max}
    res = svc_res(gate([{"meth": "StationBoard", "req": req}], lang=args.lang))
    common = res.get("common", {})
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    print(f"{('Arrivals' if args.arrivals else 'Departures')} for {loc.get('name', args.stop)}")
    for jny in res.get("jnyL", [])[:args.max]:
        prod = product_name(common, jny.get("prodX"))
        direction = jny.get("dirTxt") or loc_name(common, jny.get("dirLocX"))
        stop = jny.get("stbStop", {})
        time_s = jny.get("time") or stop.get("dTimeS") or stop.get("dTimeR") or ""
        rt = stop.get("dTimeR")
        delay = f" rt {rt}" if rt and rt != time_s else ""
        print(f"{time_s[:2]}:{time_s[2:4]} {prod:<12} → {direction}{delay}")


def loc_for_trip(value):
    loc = resolve_stop(value)
    return {"lid": loc["lid"]} if loc.get("lid") else {"extId": loc["extId"]}


def cmd_route(args):
    date, time = parse_when(args.date, args.time)
    req = {
        "depLocL": [loc_for_trip(args.origin)],
        "arrLocL": [loc_for_trip(args.destination)],
        "outDate": date,
        "outTime": time,
        "getPasslist": False,
        "getPolyline": False,
        "numF": args.max,
        "jnyFltrL": [{"type": "PROD", "mode": "INC", "value": 127}],
    }
    if args.arrive_by:
        req["outFrwd"] = False
    res = svc_res(gate([{"meth": "TripSearch", "req": req}], lang=args.lang))
    common = res.get("common", {})
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    for n, con in enumerate((res.get("outConL") or [])[:args.max], 1):
        dur = con.get("dur") or ""
        dep = con.get("dep", {}).get("dTimeR") or con.get("dep", {}).get("dTimeS") or ""
        arr = con.get("arr", {}).get("aTimeR") or con.get("arr", {}).get("aTimeS") or ""
        print(f"#{n} {dep[:2]}:{dep[2:4]} → {arr[:2]}:{arr[2:4]}  {dur}")
        for sec in con.get("secL", []):
            jny = sec.get("jny") or {}
            prod = product_name(common, jny.get("prodX")) if jny.get("prodX") is not None else sec.get("type", "")
            dep_stop = loc_name(common, sec.get("dep", {}).get("locX"))
            arr_stop = loc_name(common, sec.get("arr", {}).get("locX"))
            print(f"   - {prod}: {dep_stop} → {arr_stop}")


def main():
    parser = argparse.ArgumentParser(description="mobiliteit.lu HAFAS CLI")
    parser.add_argument("--lang", default="eng", choices=["eng", "fra", "deu"])
    sub = parser.add_subparsers(dest="cmd", required=True)

    search = sub.add_parser("search", help="search stops/locations")
    search.add_argument("query")
    search.add_argument("--type", default="S", help="HAFAS location type, default S=stop")
    search.add_argument("--max", type=int, default=10)
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    deps = sub.add_parser("departures", aliases=["deps"], help="show departures for a stop name, extId, or lid")
    deps.add_argument("stop")
    deps.add_argument("--date")
    deps.add_argument("--time")
    deps.add_argument("--max", type=int, default=10)
    deps.add_argument("--arrivals", action="store_true")
    deps.add_argument("--json", action="store_true")
    deps.set_defaults(func=cmd_departures)

    route = sub.add_parser("route", help="plan route between two stops/locations")
    route.add_argument("origin")
    route.add_argument("destination")
    route.add_argument("--date")
    route.add_argument("--time")
    route.add_argument("--max", type=int, default=3)
    route.add_argument("--arrive-by", action="store_true")
    route.add_argument("--json", action="store_true")
    route.set_defaults(func=cmd_route)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
