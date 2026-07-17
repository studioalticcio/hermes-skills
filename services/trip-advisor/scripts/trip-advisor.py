#!/usr/bin/env python3
"""Bike-or-bus advisor for Luxembourg: compare a vel'OH! ride vs the next bus.

Reads the live vel'OH! feed (feeds/veloh.json) for bike availability and shells
out to the `mobiliteit` HAFAS CLI for the bus option, then recommends whichever
gets you there sooner door-to-door.

Estimates (walk speed, cycling speed, detour factor) are rough and tunable via
env — this is a nudge, not a routing engine. ponytail: geodesic + fixed speeds;
swap in OSRM if you ever want turn-by-turn cycling time.

Usage: trip-advisor.py "Luxembourg, Gare Centrale"
       trip-advisor.py --json "Belair, Nico Klopp"
"""
import json
import math
import os
import re
import subprocess
import sys

FEED = os.environ.get('VELOH_FEED', '/var/lib/server-dashboard/feeds/veloh.json')
MOBILITEIT = os.environ.get('MOBILITEIT_BIN', os.path.expanduser('~/.local/bin/mobiliteit'))
HOME = (49.6116, 6.1319)  # <your home address>
HOME_STOP = os.environ.get('HOME_STOP', 'Kirchberg, <home station>')
WALK_KMH = float(os.environ.get('WALK_KMH', '4.8'))
BIKE_KMH = float(os.environ.get('BIKE_KMH', '15'))
DETOUR = float(os.environ.get('DETOUR', '1.35'))  # street distance / straight line
UNLOCK_MIN = float(os.environ.get('VELOH_UNLOCK_MIN', '2'))  # dock faff each end


def geo_m(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    x = (lon2 - lon1) * math.cos((lat1 + lat2) / 2)
    return 6371000 * math.hypot(x, lat2 - lat1)


def mobiliteit(*args):
    return subprocess.run([MOBILITEIT, *args], capture_output=True, text=True, timeout=30).stdout


def dest_coords(name):
    out = mobiliteit('search', '--json', name)
    arr = json.loads(out)
    if not arr:
        raise RuntimeError(f'no stop found for {name!r}')
    crd = arr[0]['crd']
    return (crd['y'] / 1e6, crd['x'] / 1e6), arr[0].get('name') or name


def parse_dur(tok):
    """HAFAS duration token like '002900' -> minutes (HHMMSS)."""
    t = tok.zfill(6)
    h, m, s = int(t[-6:-4]), int(t[-4:-2]), int(t[-2:])
    return h * 60 + m + round(s / 60)


def bus_option(origin, dest):
    out = mobiliteit('route', '--max', '3', origin, dest)
    # First result line: '#1 17:04 → 17:33  002900'
    m = re.search(r'#1\s+(\d\d:\d\d)\s*→\s*(\d\d:\d\d)\s+(\d+)', out)
    if not m:
        return None
    block = out.split('#2')[0]
    legs = len(re.findall(r'-\s+(?:Bus|RB|IC|TER|Tram|Train)\b', block))
    return {'depart': m.group(1), 'arrive': m.group(2), 'minutes': parse_dur(m.group(3)),
            'transfers': max(0, legs - 1), 'vehicles': legs}


def bike_option(dest):
    d = json.load(open(FEED))
    if not d.get('ok'):
        return None
    st = d['stations']
    pickup = min((s for s in st if s['open'] and s['bikes'] >= 1),
                 key=lambda s: geo_m(HOME, (s['lat'], s['lon'])), default=None)
    if not pickup:
        return None
    drop = min((s for s in st if s['open'] and (s['stands'] or 0) >= 1),
               key=lambda s: geo_m(dest, (s['lat'], s['lon'])), default=None)
    walk1 = geo_m(HOME, (pickup['lat'], pickup['lon']))
    ride = geo_m((pickup['lat'], pickup['lon']),
                 (drop['lat'], drop['lon']) if drop else dest) * DETOUR
    walk2 = geo_m((drop['lat'], drop['lon']) if drop else dest, dest)
    mins = (walk1 + walk2) / (WALK_KMH * 1000 / 60) + ride / (BIKE_KMH * 1000 / 60) + UNLOCK_MIN * 2
    return {'minutes': round(mins), 'pickup': pickup['name'], 'pickup_bikes': pickup['bikes'],
            'dropoff': drop['name'] if drop else None,
            'ride_km': round(ride / 1000, 1), 'walk_m': round(walk1 + walk2)}


def advise(dest_name):
    dest, label = dest_coords(dest_name)
    bus = bus_option(HOME_STOP, dest_name)
    bike = bike_option(dest)
    pick = None
    if bus and bike:
        pick = 'bike' if bike['minutes'] + 3 < bus['minutes'] else 'bus'  # 3-min bias to transit reliability
    elif bike:
        pick = 'bike'
    elif bus:
        pick = 'bus'
    return {'destination': label, 'recommend': pick, 'bus': bus, 'bike': bike}


def human(r):
    lines = [f"To {r['destination']}:"]
    if r['bike']:
        b = r['bike']
        lines.append(f"  🚲 vel'OH ~{b['minutes']} min · {b['pickup']} ({b['pickup_bikes']} bikes) → "
                     f"{b['dropoff'] or 'destination'} · {b['ride_km']} km ride, {b['walk_m']} m walk")
    else:
        lines.append("  🚲 vel'OH: no bike/dock available")
    if r['bus']:
        s = r['bus']
        lines.append(f"  🚌 bus ~{s['minutes']} min · {s['depart']}→{s['arrive']} · "
                     f"{s['transfers']} transfer(s)")
    else:
        lines.append("  🚌 bus: no route found")
    if r['recommend']:
        lines.append(f"  → take the {r['recommend'].upper()}")
    return '\n'.join(lines)


def main(argv):
    as_json = '--json' in argv
    args = [a for a in argv if a != '--json']
    if not args:
        print('usage: trip-advisor.py [--json] "Destination stop"', file=sys.stderr)
        return 2
    r = advise(' '.join(args))
    print(json.dumps(r) if as_json else human(r))
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        assert parse_dur('002900') == 29
        assert parse_dur('010500') == 65
        assert parse_dur('000045') == 1
        assert round(geo_m((49.62, 6.14), (49.62, 6.14))) == 0
        print('selftest ok')
    else:
        sys.exit(main(sys.argv[1:]))
