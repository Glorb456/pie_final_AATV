# Custom AATV symbols in KiCad 7 library syntax (readable by KiCad 7-10)

def _prop(name, val, x=0, y=0, hide=False, size=1.27):
    h = ' hide' if hide else ''
    return f'(property "{name}" "{val}" (at {x} {y} 0) (effects (font (size {size} {size})){h}))'

def _pin(typ, x, y, rot, name, num, length=2.54, hide=False):
    h = ' hide' if hide else ''
    return (f'(pin {typ} line (at {x} {y} {rot}) (length {length}){h} '
            f'(name "{name}" (effects (font (size 1.016 1.016)))) '
            f'(number "{num}" (effects (font (size 1.016 1.016)))))')

def _rect(x1, y1, x2, y2, w=0.254, fill='background'):
    return f'(rectangle (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def _poly(pts, w=0.254, fill='none'):
    p = ' '.join(f'(xy {x} {y})' for x, y in pts)
    return f'(polyline (pts {p}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def _circle(x, y, r, w=0.254, fill='none'):
    return f'(circle (center {x} {y}) (radius {r}) (stroke (width {w}) (type default)) (fill (type {fill})))'

def _text(t, x, y, size=1.27, rot=0):
    return f'(text "{t}" (at {x} {y} {rot}) (effects (font (size {size} {size}))))'

def sym(name, ref, value, graphics, pinlist, desc='', pin_names_offset=1.016, hide_pin_names=False,
        hide_pin_numbers=False, refpos=(0, 0), valpos=(0, 0), in_bom='yes', on_board='yes', fp=''):
    pn = f'(pin_names (offset {pin_names_offset}){" hide" if hide_pin_names else ""})'
    pnum = '(pin_numbers hide)' if hide_pin_numbers else ''
    out = [f'(symbol "{name}" {pnum} {pn} (in_bom {in_bom}) (on_board {on_board})',
           _prop('Reference', ref, *refpos),
           _prop('Value', value, *valpos),
           _prop('Footprint', fp, hide=True),
           _prop('Datasheet', '~', hide=True),
           _prop('ki_description', desc, hide=True),
           f'(symbol "{name}_0_1" ' + ' '.join(graphics) + ')',
           f'(symbol "{name}_1_1" ' + ' '.join(pinlist) + ')',
           ')']
    return '\n'.join(out)

CUSTOM = {}

CUSTOM['ESC_Brushed'] = sym(
    'ESC_Brushed', 'U', 'Brushed ESC', [
        _rect(-7.62, 5.08, 7.62, -10.16),
        _text('ESC', 4.445, -7.62, 1.27)],
    [_pin('power_in', -10.16, 2.54, 0, 'BAT+', 1),
     _pin('power_in', -10.16, 0, 0, 'BAT-', 2),
     _pin('power_out', -10.16, -2.54, 0, 'BEC+', 3),
     _pin('input', -10.16, -5.08, 0, 'SIG', 4),
     _pin('passive', -10.16, -7.62, 0, 'SIG_GND', 5),
     _pin('passive', 10.16, 2.54, 180, 'M+', 6),
     _pin('passive', 10.16, -2.54, 180, 'M-', 7)],
    desc='Brushed motor ESC (waterproof crawler type). BEC+ (red signal wire) is left unconnected.',
    refpos=(0, 6.35), valpos=(0, -11.43))

CUSTOM['ESC_TD1.2'] = sym(
    'ESC_TD1.2', 'U', 'TD1.2 ESC', [
        _rect(-7.62, 5.08, 7.62, -10.16),
        _text('BLDC ESC', 3.175, -5.588, 1.016)],
    [_pin('power_in', -10.16, 2.54, 0, 'BAT+', 1),
     _pin('power_in', -10.16, 0, 0, 'BAT-', 2),
     _pin('input', -10.16, -5.08, 0, 'SIG', 3),
     _pin('passive', -10.16, -7.62, 0, 'SIG_GND', 4),
     _pin('passive', 10.16, 2.54, 180, 'U', 5),
     _pin('passive', 10.16, 0, 180, 'V', 6),
     _pin('passive', 10.16, -2.54, 180, 'W', 7)],
    desc='Diamond Dynamics TD1.2 bidirectional ESC (no BEC). Yellow=SIG, White=SIG_GND, Red/Black=12 V.',
    refpos=(0, 6.35), valpos=(0, -11.43))

CUSTOM['Thruster_TD1.2'] = sym(
    'Thruster_TD1.2', 'MT', 'TD1.2 thruster', [
        _circle(0, 0, 5.08),
        _poly([(-2.54, 2.54), (2.54, -2.54)]), _poly([(-2.54, -2.54), (2.54, 2.54)]),
        _text('BLDC', 0, -3.556, 1.016)],
    [_pin('passive', -10.16, 2.54, 0, 'U', 1, length=5.08),
     _pin('passive', -10.16, 0, 0, 'V', 2, length=5.08),
     _pin('passive', -10.16, -2.54, 0, 'W', 3, length=5.08)],
    desc='Diamond Dynamics TD1.2 underwater thruster, 12 V, up to ~15 A',
    hide_pin_names=True, refpos=(0, 6.35), valpos=(0, -6.35))

CUSTOM['Buck_12V_7V5'] = sym(
    'Buck_12V_7V5', 'U', '12V->7.5V buck', [
        _rect(-7.62, 5.08, 7.62, -5.08),
        _text('BUCK', 0, 0, 1.27)],
    [_pin('power_in', -10.16, 2.54, 0, 'VIN+', 1),
     _pin('power_in', -10.16, -2.54, 0, 'VIN-', 2),
     _pin('power_out', 10.16, 2.54, 180, 'VOUT+', 3),
     _pin('passive', 10.16, -2.54, 180, 'VOUT-', 4)],
    desc='12 V to 7.5 V buck module for the servo rail',
    refpos=(0, 6.35), valpos=(0, -6.35))

CUSTOM['USB_Cable'] = sym(
    'USB_Cable', 'W', 'USB cable', [
        _rect(-7.62, 3.81, -5.08, -3.81, fill='outline'),
        _rect(5.08, 2.54, 7.62, -2.54, fill='outline'),
        _poly([(-5.08, 0), (5.08, 0)], w=0.762),
        _text('USB-A', -6.35, 5.08, 1.016), _text('micro-B', 6.35, 5.08, 1.016),
        _text('+ USB data', 0, -2.286, 1.016)],
    [_pin('passive', -10.16, 2.54, 0, 'VBUS', 1, hide=False),
     _pin('passive', -10.16, -2.54, 0, 'GND', 4),
     _pin('passive', 10.16, 1.27, 180, 'VBUS', 5),
     _pin('passive', 10.16, -1.27, 180, 'GND', 8)],
    desc='USB-A to micro-B cable. Carries 5 V + USB data from the Pi 4 to the Pico.',
    hide_pin_names=True, refpos=(0, 7.62), valpos=(0, -5.08))

# Penetration marker: no pins. Drawn as a hatched plug in a wall.
CUSTOM['Penetration'] = sym(
    'Penetration', 'PEN', 'Penetration', [
        _rect(-2.54, 3.81, 2.54, -3.81, w=0.508, fill='none'),
        _poly([(-2.54, 1.27), (0, 3.81)]), _poly([(-2.54, -1.27), (2.54, 3.81)]),
        _poly([(-2.54, -3.81), (2.54, 1.27)]), _poly([(0, -3.81), (2.54, -1.27)]),
        _poly([(-3.81, 3.81), (-3.81, -3.81)], w=0.508), _poly([(3.81, 3.81), (3.81, -3.81)], w=0.508)],
    [], desc='Drybox wall penetration (cable gland / bulkhead fitting). Mechanical part, no pins.',
    refpos=(0, 5.08), valpos=(0, -5.08), on_board='no')

LIB_HEADER = '(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n'

def library_file():
    return LIB_HEADER + '\n'.join(CUSTOM.values()) + '\n)\n'

def embedded(name):
    """Return the symbol text renamed for embedding as AATV:<name> in a schematic."""
    s = CUSTOM[name]
    return s.replace(f'(symbol "{name}" ', f'(symbol "AATV:{name}" ', 1)
