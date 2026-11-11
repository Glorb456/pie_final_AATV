import uuid, math, sys
from sexp import parse, dump, Sym, find
from libs import from_src, from_v7, pins
import custom

ROOT_UUID = '3d068461-6f07-4ae9-b8ca-6794a0e6ec0a'
PROJECT = 'AATV'
TITLE = {'title': 'AA-TV electrical', 'rev': 'v7', 'date': '2026-11-04', 'c1': '', 'c2': '', 'c3': ''}
_ns = uuid.UUID('6f1c2d1e-1111-4a5b-9c9d-aa7700000000')
_ctr = [0]
def U():
    _ctr[0] += 1
    return str(uuid.uuid5(_ns, str(_ctr[0])))

def f(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

# ---------------------------------------------------------------- symbol library
LIBSYMS = {}      # lib_id -> sexp text
PINS = {}         # lib_id -> list of pins
def need(lib_id):
    if lib_id in LIBSYMS: return
    lib, name = lib_id.split(':', 1)
    if lib == 'AATV':
        txt = custom.embedded(name)
        node = parse(txt)
    elif lib_id in ('MCU_Module:RaspberryPi_Pico', 'Connector:Raspberry_Pi_4'):
        node = from_src(lib_id)
        txt = dump(node)
    else:
        node = from_v7(lib, name)
        txt = dump(node)
    LIBSYMS[lib_id] = txt
    PINS[lib_id] = pins(node)

# ---------------------------------------------------------------- items
ITEMS = []
REFS = {}

def xf(px, py, X, Y, rot, mirror):
    sx, sy = px, -py
    if mirror: sx = -sx
    r = rot % 360
    if r == 90: sx, sy = sy, -sx
    elif r == 180: sx, sy = -sx, -sy
    elif r == 270: sx, sy = -sy, sx
    return (round(X + sx, 4), round(Y + sy, 4))

def dirvec(a, rot, mirror):
    # pin direction (from connection point toward body) in screen coords
    a = a % 360
    dx, dy = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[int(a)]
    if mirror: dx = -dx
    r = rot % 360
    if r == 90: dx, dy = dy, -dx
    elif r == 180: dx, dy = -dx, -dy
    elif r == 270: dx, dy = -dy, dx
    return dx, dy

class Part:
    def __init__(s, lib_id, ref, value, X, Y, rot=0, mirror=False, refpos=None, valpos=None,
                 hide_ref=False, hide_val=False, fields=None, in_bom=True, valsize=1.27, refsize=1.27, just=None):
        need(lib_id)
        s.lib_id, s.ref, s.value, s.X, s.Y, s.rot, s.mirror = lib_id, ref, value, X, Y, rot, mirror
        s.refpos = refpos if refpos else (X, Y - 7.62)
        s.valpos = valpos if valpos else (X, Y + 7.62)
        s.hide_ref, s.hide_val = hide_ref, hide_val
        s.fields = fields or {}
        s.in_bom = in_bom
        s.valsize, s.refsize = valsize, refsize
        s.just = just
        s.uuid = U()
        REFS[ref] = s
        ITEMS.append(s)
    def pin(s, key):
        for p in PINS[s.lib_id]:
            if p['num'] == str(key) or p['name'] == str(key):
                return p
        raise KeyError(f'{s.ref}: pin {key}')
    def P(s, key):
        p = s.pin(key)
        return xf(p['x'], p['y'], s.X, s.Y, s.rot, s.mirror)
    def out(s, key):
        p = s.pin(key)
        dx, dy = dirvec(p['rot'], s.rot, s.mirror)
        return (-dx, -dy)
    def text(s):
        L = [f'(symbol (lib_id "{s.lib_id}") (at {f(s.X)} {f(s.Y)} {s.rot})' + (' (mirror y)' if s.mirror else '') + ' (unit 1)',
             f'  (in_bom {"yes" if s.in_bom else "no"}) (on_board yes) (dnp no)',
             f'  (uuid {s.uuid})']
        def prop(n, v, pos, hide, size=1.27, just=None):
            h = ' hide' if hide else ''
            j = f' (justify {just})' if just else ''
            ang = s.rot if s.rot in (90, 270) else 0
            return f'  (property "{n}" {q(v)} (at {f(pos[0])} {f(pos[1])} {ang}) (effects (font (size {size} {size})){j}{h}))'
        L.append(prop('Reference', s.ref, s.refpos, s.hide_ref, s.refsize, s.just))
        L.append(prop('Value', s.value, s.valpos, s.hide_val, s.valsize, s.just))
        L.append(prop('Footprint', '', (s.X, s.Y), True))
        L.append(prop('Datasheet', '~', (s.X, s.Y), True))
        for k, v in s.fields.items():
            L.append(prop(k, v, (s.X, s.Y), True))
        seen = set()
        for p in PINS[s.lib_id]:
            if p['num'] in seen: continue
            seen.add(p['num'])
            L.append(f'  (pin "{p["num"]}" (uuid {U()}))')
        L.append(f'  (instances (project "{_proj()}" (path "/{ROOT_UUID}" (reference "{s.ref}") (unit 1))))')
        L.append(')')
        return '\n'.join(L)

def _proj():
    return PROJECT

def q(v):
    return '"' + v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

class Raw:
    def __init__(s, t): s.t = t; ITEMS.append(s)
    def text(s): return s.t

def wire(a, b):
    if a == b: return
    Raw(f'(wire (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) (stroke (width 0) (type default)) (uuid {U()}))')

def path(*pts):
    for a, b in zip(pts, pts[1:]): wire(a, b)

def label(name, at, angle=0, size=1.27):
    just = {0: 'left bottom', 90: 'left bottom', 180: 'right bottom', 270: 'right bottom'}[angle]
    Raw(f'(label {q(name)} (at {f(at[0])} {f(at[1])} {angle}) (fields_autoplaced) '
        f'(effects (font (size {size} {size})) (justify {just})) (uuid {U()}))')

def junction(at):
    Raw(f'(junction (at {f(at[0])} {f(at[1])}) (diameter 0) (color 0 0 0 0) (uuid {U()}))')

def nc(part, key):
    x, y = part.P(key)
    Raw(f'(no_connect (at {f(x)} {f(y)}) (uuid {U()}))')

def text(t, at, size=1.27, bold=False, just='left top', angle=0):
    b = ' bold' if bold else ''
    Raw(f'(text {q(t)} (at {f(at[0])} {f(at[1])} {angle}) (effects (font (size {size} {size}){b}) (justify {just})) (uuid {U()}))')

def rect(a, b, width=0.5, style='solid', color=None):
    c = f' (color {color})' if color else ''
    Raw(f'(rectangle (start {f(a[0])} {f(a[1])}) (end {f(b[0])} {f(b[1])}) '
        f'(stroke (width {width}) (type {style}){c}) (fill (type none)) (uuid {U()}))')

def line(a, b, width=0.3, style='dash'):
    Raw(f'(polyline (pts (xy {f(a[0])} {f(a[1])}) (xy {f(b[0])} {f(b[1])})) (stroke (width {width}) (type {style})) (uuid {U()}))')

def stub(part, key, net, length=2.54, size=1.27):
    """Short wire out of a pin, ending in a net label."""
    x, y = part.P(key)
    dx, dy = part.out(key)
    e = (round(x + dx * length, 4), round(y + dy * length, 4))
    wire((x, y), e)
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[(dx, dy)]
    label(net, e, ang, size)
    return e

def write(path_):
    need('power:PWR_FLAG')
    head = (f'(kicad_sch (version 20230121) (generator eeschema)\n\n  (uuid {ROOT_UUID})\n\n'
            f'  (paper "A2")\n\n'
            f'  (title_block\n    (title {q(TITLE["title"])})\n'
            f'    (date {q(TITLE["date"])})\n    (rev {q(TITLE["rev"])})\n    (company "PIE AA-TV")\n'
            f'    (comment 1 {q(TITLE["c1"])})\n'
            f'    (comment 2 {q(TITLE["c2"])})\n'
            f'    (comment 3 {q(TITLE["c3"])})\n'
            '  )\n\n')
    libs = '  (lib_symbols\n' + '\n'.join(LIBSYMS[k] for k in sorted(LIBSYMS)) + '\n  )\n\n'
    body = '\n'.join(i.text() for i in ITEMS)
    tail = '\n\n  (sheet_instances\n    (path "/" (page "1"))\n  )\n)\n'
    open(path_, 'w').write(head + libs + body + tail)
