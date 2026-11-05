#!/usr/bin/env python3
"""Render an explicit physical-hole model; validate ideal copper/wire endpoints."""
import argparse
import csv
import html
import json
import math
from pathlib import Path


def validate(m):
    errors = []
    b = m['board']
    for key in ('width_mm', 'height_mm', 'pitch_mm'):
        if not isinstance(b[key], (int, float)) or not math.isfinite(b[key]) or b[key] <= 0:
            raise ValueError('board dimensions/pitch must be finite and positive')
    if b['baseline_view'] not in ('front', 'back') or b['copper_side'] not in ('front', 'back'):
        raise ValueError('declare front/back baseline_view and copper_side')
    if not isinstance(b['copper_verified'], bool):
        raise ValueError('copper_verified must be boolean')
    hs = m['holes']; holes = {h['id']: h for h in hs}
    if len(holes) != len(hs) or not holes:
        raise ValueError('hole IDs must be nonempty and unique')
    positions = set()
    for h in hs:
        x, y = h['x'], h['y']
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x, y)):
            raise ValueError('hole coordinates must be finite')
        if not (0 <= x <= b['width_mm'] and 0 <= y <= b['height_mm']):
            errors.append(f"hole outside board: {h['id']}")
        if (x, y) in positions: errors.append('duplicate hole position')
        positions.add((x, y))
    parent = {h: h for h in holes}
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def join(a, c): parent[root(a)] = root(c)
    claimed = set()
    for island in m.get('copper_islands', []):
        if not island: raise ValueError('empty copper island')
        for h in island:
            if h not in holes: raise ValueError('unknown copper hole: ' + h)
            if h in claimed: errors.append('overlapping copper islands: ' + h)
            claimed.add(h); join(island[0], h)
    for component in m.get('components', []):
        if not component['holes'] or any(h not in holes for h in component['holes']):
            raise ValueError('component has missing or unknown holes')
    leads = m.get('leads', [])
    wires = m.get('connections', [])
    for category, items in [('lead', leads), ('connection', wires)]:
        ids = [a['id'] for a in items]
        if len(ids) != len(set(ids)): errors.append('duplicate ' + category + ' ID')
    # Labels are design intent, not a simulated conductive path through components.
    labels = []
    for lead in leads:
        if lead['hole'] not in holes: raise ValueError('unknown lead hole')
        if not lead['net']: raise ValueError('empty lead net')
        labels.append((lead['hole'], lead['net'], lead['id']))
    for w in wires:
        a, c = w['start'], w['end']
        if a not in holes or c not in holes: raise ValueError('unknown connection endpoint')
        if a == c: errors.append('zero-length connection: ' + w['id'])
        if w['side'] not in ('front', 'back'): raise ValueError('invalid installation side')
        if w['method'] not in ('bridge', 'bare', 'insulated'): raise ValueError('invalid method')
        if not w['net'] or w['net'] == 'NC': errors.append('invalid wire net: ' + w['id'])
        if w['method'] == 'bridge':
            d = math.hypot(holes[a]['x'] - holes[c]['x'], holes[a]['y'] - holes[c]['y'])
            if not math.isclose(d, b['pitch_mm'], rel_tol=1e-5, abs_tol=1e-5):
                errors.append('bridge must join adjacent holes: ' + w['id'])
            if w['side'] != b['copper_side']: errors.append('bridge on non-copper side: ' + w['id'])
            if w.get('points'): errors.append('bridge cannot have route waypoints: ' + w['id'])
        for xy in w.get('points', []):
            if len(xy) != 2 or not all(isinstance(v, (int,float)) and math.isfinite(v) for v in xy):
                raise ValueError('invalid route point')
            if not (0 <= xy[0] <= b['width_mm'] and 0 <= xy[1] <= b['height_mm']):
                errors.append('route point outside board: ' + w['id'])
        join(a, c); labels.extend([(a, w['net'], w['id']), (c, w['net'], w['id'])])
    groups = {}; nets = {}
    for h, net, ident in labels:
        r = root(h); groups.setdefault(r, []).append((net, ident))
        if net != 'NC': nets.setdefault(net, set()).add(r)
    for entries in groups.values():
        active = {net for net, _ in entries if net != 'NC'}
        if len(active) > 1: errors.append('short between nets: ' + ', '.join(sorted(active)))
        ncs = [ident for net, ident in entries if net == 'NC']
        if ncs and (active or len(ncs) > 1): errors.append('NC not isolated: ' + ', '.join(ncs))
    for net, rs in nets.items():
        if len(rs) > 1: errors.append('disconnected required net: ' + net)
    return {'model_checks_passed': not errors, 'copper_verified': b['copper_verified'],
            'physical_verification': 'pending', 'errors': errors,
            'scope': 'Ideal copper and jumper endpoints only; see model-and-validation.md',
            'status': ('MODEL CHECKS PASSED - DRAWING/PHYSICAL REVIEW PENDING' if b['copper_verified'] else
                       'PROVISIONAL - COPPER VERIFICATION PENDING') if not errors else 'MODEL CHECKS FAILED'}


def render(m, side):
    b = m['board']; width, height = b['width_mm'], b['height_mm']
    mirror = side != b['baseline_view']
    def xy(p): return ((width-p[0]) if mirror else p[0], p[1])
    holes = {h['id']: h for h in m['holes']}
    def pos(h): return xy((holes[h]['x'], holes[h]['y']))
    esc = lambda s: html.escape(str(s), quote=True)
    page_width = max(width + 16, 125)
    legend_height = 19 + 2.7 * (len(m.get('connections', [])) + len(m.get('leads', [])))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-8 -18 {page_width} {height+18+legend_height}">',
           '<rect x="-8" y="-18" width="100%" height="100%" fill="white"/>',
           f'<text x="0" y="-13" font-family="sans-serif" font-size="2.1">{side.upper()} VIEW; physical IDs unchanged</text>',
           f'<text x="0" y="-9" font-family="sans-serif" font-size="1.6">Baseline: {b["baseline_view"]}; flip: horizontal; copper: {b["copper_side"]}</text>',
           '<text x="0" y="-5" font-family="sans-serif" font-size="1.6">Squares=endpoints; halo=crossing not joined; dash=opposite side</text>',
           f'<rect width="{width}" height="{height}" fill="#fafbfc" stroke="#667580" stroke-width="0.3"/>']
    for island in m.get('copper_islands', []):
        # A reference connectivity tree, not inferred physical trace geometry.
        for h in island[1:]:
            a,c=pos(island[0]),pos(h)
            out.append(f'<path d="M {a[0]} {a[1]} L {c[0]} {c[1]}" stroke="#c5cbd0" stroke-width="0.7" fill="none"/>')
    out.append('<text x="0" y="'+str(height+4)+'" font-size="1.5">Gray links: copper connectivity reference, not trace artwork.</text>')
    for ident,h in holes.items():
        x,y=pos(ident)
        out.append(f'<circle cx="{x}" cy="{y}" r="0.45" fill="white" stroke="#9ba7af" stroke-width="0.15"/>')
        out.append(f'<text x="{x+0.6}" y="{y-0.6}" font-family="sans-serif" font-size="1.1" fill="#687783">{esc(ident)}</text>')
    for c in m.get('components', []):
        ps=[pos(h) for h in c['holes']]; xs,ys=zip(*ps)
        x,y=min(xs)-1,min(ys)-1
        out.append(f'<rect x="{x}" y="{y}" width="{max(xs)-min(xs)+2}" height="{max(ys)-min(ys)+2}" fill="none" stroke="#52606b" stroke-width="0.25"/>')
        out.append(f'<text x="{x}" y="{y-0.5}" font-size="1.6">{esc(c["id"].split()[0][:8])}</text>')
    palette=['#0068B5','#007F78','#A66A00','#6845A5','#C43C28','#263238']
    colors={n:palette[i%len(palette)] for i,n in enumerate(sorted({w['net'] for w in m.get('connections',[])}))}
    colors.update(m.get('net_colors',{}))
    for w in m.get('connections', []):
        points=[pos(w['start'])]+[xy(p) for p in w.get('points',[])]+[pos(w['end'])]
        pts=' '.join(f'{x},{y}' for x,y in points); color=esc(colors[w['net']])
        dash=' stroke-dasharray="1.2 0.7"' if w['side']!=side else ''
        out.append(f'<polyline points="{pts}" fill="none" stroke="white" stroke-width="0.95"/>')
        stroke_width = {'bridge': 0.8, 'bare': 0.55, 'insulated': 0.35}[w['method']]
        out.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{stroke_width}"{dash}/>')
        # Endpoint squares redrawn after all wires, so later crossings never hide them.
    for w in m.get('connections', []):
        color=esc(colors[w['net']]); x,y=pos(w['start'])
        for x1,y1 in [pos(w['start']),pos(w['end'])]:
            out.append(f'<rect x="{x1-0.7}" y="{y1-0.7}" width="1.4" height="1.4" fill="none" stroke="{color}" stroke-width="0.3"/>')

    out.append(f'<text x="0" y="{height+7}" font-size="1.5" fill="#8c3c12">' + ('MODEL ONLY: drawing / physical review pending' if b['copper_verified'] else 'PROVISIONAL: copper / physical verification pending') + '</text>')
    y = height + 11
    out.append(f'<text x="0" y="{y}" font-size="1.6">Construction legend: thick=bridge; medium=bare; thin=insulated</text>')
    for w in m.get('connections', []):
        y += 2.7
        label = f"{w['id']} | {w['net']} | {w['start']} to {w['end']} | {w['method']} | {w['side']}"
        out.append(f'<text x="0" y="{y}" font-size="1.7" fill="{esc(colors[w["net"]])}">{esc(label)}</text>')
    for lead in m.get('leads', []):
        y += 2.7
        label = f"{lead['id']} | hole {lead['hole']} | net {lead['net']}"
        out.append(f'<text x="0" y="{y}" font-size="1.6">{esc(label)}</text>')
    out.append('</svg>'); return '\n'.join(out)


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('model',type=Path); ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); m=json.loads(args.model.read_text()); args.out.mkdir(parents=True,exist_ok=True)
    for old_name in ('front.svg', 'back.svg', 'connections.csv'):
        (args.out/old_name).unlink(missing_ok=True)
    try: result=validate(m)
    except (KeyError,ValueError,TypeError) as e: result={'model_checks_passed':False,'errors':[str(e)]}
    (args.out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['model_checks_passed']: print(json.dumps(result)); return 1
    for side in ('front','back'): (args.out/f'{side}.svg').write_text(render(m,side))
    purposes={}
    for lead in m.get('leads',[]): purposes.setdefault(lead['hole'],[]).append(lead['id'])
    with (args.out/'connections.csv').open('w',newline='') as f:
        fields=['id','net','start','end','start_pins','end_pins','method','side','group']
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader()
        for wire in m.get('connections',[]):
            row={k:wire.get(k,'') for k in fields};row['start_pins']=';'.join(purposes.get(wire['start'],[]));row['end_pins']=';'.join(purposes.get(wire['end'],[]));wr.writerow(row)
    print(json.dumps(result));return 0

if __name__=='__main__': raise SystemExit(main())
