# AA-TV (Amphibious All-Terrain Vehicle): project context

PIE (Olin) team project: a tethered, remote-controlled submarine. Front driven wheels were dropped in v8.

- Human-readable status and history: `DESIGN_AND_PROGRESS.md`
- Detailed change log through v9: `edits.md`
- Last updated: 2026-11-11

## Status in one paragraph

The design has moved past the newest schematic file. `kicad_files/AATV_v9/` (v9) is the latest KiCad schematic and `AATV_wiring_v10_draft.png` (v10) is the latest wiring diagram. Neither matches what is being built: the thruster changed, the ballast system changed twice, and the battery-monitor resistor values changed. The section "Current design" below is the source of truth until a v11 schematic and guide exist. Do not wire from the v9 schematic or the v10 draft without applying the "Known drawing errors" list.

## Current design (v11 target, not yet drawn)

### Layout
- **Buoy (surface, dry):** Raspberry Pi 4 and a USB-C power bank. A 3 m USB-A to micro-B cable runs down a vinyl tube to the Pico. The Pi powers the Pico (5 V on VBUS) and talks to it over USB serial.
- **Main box:** one IP67 ABS box with four M16 glands. It holds everything electrical: 3S LiPo, EC5 disconnect, main fuse, kill switch, bus bar, buck, boost, the Pico board and the MOSFET switch board.
- **Wet side:** four servos, the thruster (ESC built in), the bilge pump and the solenoid valve.
- **Glands:** G1 USB cable. G2 thruster cable (power pair plus signal pair; pot it, because a gland seals only one round cable). G3 pump and valve leads, potted. G4 four servo leads, potted.

### Power
```
3S LiPo (11.1 V nominal, 12.6 V full)
  + -> EC5 (J2) -> F1 25 A -> kill switch SW1 (high side, 30 A) -> +12 V bus bar row
  - -> GND bus bar row (never switched)
+12 V bus -> thruster power lead (ESC is inside the thruster)
          -> buck U1 (fixed 7.5 V, 20 A) -> TB7 (2 terminals per pole) -> servo rail, C1 1000 uF
          -> boost U5 (24 V, 3 A max; its own fuse is on the red INPUT lead) -> 24 V rail
24 V rail -> pump M3 -> Q1 drain; Q1 source -> GND      (D3 across the pump)
          -> valve SV1 -> Q2 drain; Q2 source -> GND     (D4 across the valve; 24 V valve only)
Balance lead -> J3 -> three dividers -> ADS1115 (bypasses fuse and kill switch by design)
```

### Pico pin map
| Pin | GPIO | Function | Notes |
|---|---|---|---|
| 16, 17, 19, 20 | GP12 to GP15 | Servo PWM M4 to M7 | 200 ohm series each (R1 to R4), 50 Hz |
| 21 | GP16 | Thruster ESC signal | 200 ohm series (R5), 10k pull-down (R13) |
| 24 | GP18 | Valve enable | 200 ohm to Q2 gate (R17), 10k gate pull-down (R18) |
| 25 | GP19 | Pump enable | 200 ohm to Q1 gate (R6), 10k gate pull-down (R14) |
| 26 | GP20 | I2C0 SDA | ADS1115 |
| 27 | GP21 | I2C0 SCL | ADS1115, address 0x48 |
| 31 | GP26 | Leak sensor (ADC0) | TA2: 3V3, GND, signal |
| 40 | VBUS | 5 V from the Pi over USB | |
| 36 | 3V3 OUT | ADS1115 and leak sensor supply | |

Free: GP4, GP5, GP17, GP27, GP28.

### Battery monitor (values chosen from the resistors the team has)
| ADS1115 input | Measures | Top | Bottom | ADC volts at full charge | Firmware scale |
|---|---|---|---|---|---|
| A0 | cell 1 (4.2 V) | 100k | 200k | 2.80 | x1.500 |
| A1 | cells 1+2 (8.4 V) | 200k | 100k | 2.80 | x3.000 |
| A2 | pack (12.6 V) | 100k | 30k | 2.91 | x4.333 |

- cell1 = A0 x 1.5; cell2 = A1 x 3 - cell1; cell3 = A2 x 4.333 - A1 x 3.
- ADS1115 gain must be +/-4.096 V. The default +/-2.048 V clips below the tap voltages.
- Inputs must stay under VDD + 0.3 V (3.6 V at a 3.3 V supply). All three taps do.
- Calibrate each channel once against a multimeter and store three correction factors. Cells 2 and 3 come from subtraction, so 1% resistors alone can put cell 3 off by 0.3 V.
- 100 nF from each ADC input to GND is planned but the parts are not in hand. Until then use the slowest data rate and average.
- I2C pull-ups: leave off (the breakout has its own). If needed, 4.99k.

### Ballast (sealed tank)
- The tank is sealed, with no vent to the surface. Valve open lets water in. Pump on pushes water out.
- Pump: Rule 28D, 24 V, 1.3 A at 24 V, centrifugal, one direction. Brown lead is +.
- Valve: not chosen yet. Must be normally closed and direct-acting (zero minimum pressure). Buy 24 V so it shares the boost rail.
- A check valve on the pump outlet is needed (low opening pressure, about 0.5 psi or less). Without it, water runs backward through the stopped pump.
- Valve inlet and pump intake both go at the bottom of the tank.

## Known drawing errors (v9 schematic and v10 draft)
1. v9 still shows a pump ESC (U3), a 12 V reversible pump, the D2 Deutsch connector and `PUMP_PWM`. All gone.
2. Both show a TD1.2 ESC (U2) inside the box with three phase wires through G2. The thruster is now an ApisQueen U92 Pro with the ESC built in: two power wires plus a signal pair through G2. Its XT60 plug is cut off to pass the gland.
3. v10 feeds the valve fuse F3 from the 24 V boost. That is only right for a 24 V valve. A 12 V valve must come off the 12 V bus through its own fuse.
4. v10 shows F2 (2.5 A) after the boost. Dropped: the boost limits its output to 3 A, so a fuse after it does nothing.
5. F1 is labelled 30 A. It is 25 A.
6. Buck is labelled "set to 7.4 V". The WSOLDMA buck is fixed at 7.5 V.
7. Divider tops are labelled 47k and 330k. Use the table above.
8. All "220 ohm" become 200 ohm.

## Measured and verified on the bench
| Check | Result | Date |
|---|---|---|
| Hitec and Savox servos driven by Pico 3.3 V PWM | Work | by 2026-11-11 |
| IRLZ44N switched from a Pico GPIO (3.3 V gate), pump load | Works | by 2026-11-11 |
| Buck low-voltage cutoff, no load | Output drops at 9 V input | 2026-11-11 |

## Component facts worth remembering
- **Thruster, ApisQueen U92 Pro 12 V (CCW, with ESC):** maximum supply 16.8 V. From the listing's table at 100% throttle, forward: 10 V 12 A 4 kg; 12 V 17 A 5 kg; 14 V 21 A 7.4 kg. Reverse at 12 V: 16 A, 1.9 kg. Forward thrust is about 2.6 times reverse, so mount it with the strong direction pushing the sub forward. Thick cable is DC power on an XT60. Thin black/white pair is signal and signal ground. No 5 V wire.
- **Servos:** 2x Hitec DB777WP (spec sheet 6.0 to 7.4 V, stall 4.5 A at 7.4 V; Hitec's feature list says 4.8 to 8.4 V) and 2x Savox SW-1250MG (about 2.4 A stall). All four stalled is about 13.8 A on the 7.5 V rail.
- **Buck, WSOLDMA 12/24 V to 7.5 V, 20 A:** fixed output, non-isolated, potted, low-voltage cutoff measured at 9 V. Seller says derate above 40 C.
- **Boost, 12 V to 24 V, 3 A, 72 W:** red/black = 12 V input (fuse on red), yellow/black = 24 V output. Its fuse holder takes mini blades; the team's fuse kit is standard blades. Input current is about 3.1 to 3.5 A with the pump running, so the input fuse must be 7.5 to 10 A.
- **Pump, Rule 28D:** 1.3 A at 24 V, 2.0 A at 27.2 V. Needs at least 21 V. Maker's fuse size 2.5 A.
- **MOSFET, IRLZ44N:** 55 V. On-resistance is only specified down to a 4.0 V gate (0.035 ohm); threshold 1 to 2 V. Fine at 3.3 V for this load, confirmed by test.
- **Diode, 1N5822:** 3 A, 40 V Schottky. Leads are about 1.3 mm and may not fit perfboard holes. Mount across the screw terminals. Stripe goes to the + side of the load.
- **ADS1115:** input impedance about 6 M-ohm at the +/-4.096 V range, so 23k to 67k dividers read up to about 1% low before calibration.
- **Ratings:** Molence screw terminals 10 A per position, 14 AWG maximum. OONO bus bar 30 A. Kill switch 30 A DC. Fuse holders 12 AWG, standard blades. Breadboard contacts about 1 A.

## Current budget at the battery (thruster at 100%, pump running)
| Battery | Thruster | Typical total | All four servos stalled |
|---|---|---|---|
| 12.6 V | 18 A | 22 A | 30 A |
| 11.1 V | 15 A | 19 A | 28 A |
| 10.0 V | 12 A | 16 A | 27 A |

F1 is 25 A, which relies on a firmware throttle cap. Measure the real current at the cap; current does not scale linearly with throttle. Go to 30 A only if the battery-to-bus-bar run is 12 AWG.

## Design rules learned
- A fuse protects the wire after it. Add one only where the wire gets thinner than the upstream fuse can protect, or where the source can deliver more than the wire can take. A current-limited source (the boost) needs no fuse after it.
- The kill switch must be on the high side. The balance lead ties battery minus to board ground, which would bypass a low-side switch.
- Low-side MOSFET switching needs one shared ground: Pico, battery minus and boost output minus. Check boost input minus to output minus with a continuity meter.
- 10k gate pull-downs keep the pump off and the valve closed while the Pico boots, resets or loses USB.
- Never switch the pump and the valve on together.
- 12 V and 24 V never go on the Pico board. Perfboard strips carry signals only; load current goes point to point in 20 AWG or thicker. Servo rails are 14 AWG soldered along the strips.
- An M16 gland seals one round cable (about 4 to 8 mm). Several leads through one gland means pulling the insert and potting with epoxy. Epoxy bonds poorly to silicone jackets; pass PVC-jacketed leads through potted glands.
- Marine wire is not needed inside the box. Silicone wire: 12 AWG battery to bus bar, 14 AWG bus bar to thruster, buck and boost, 20 AWG for pump, valve and signals.
- Do not substitute resistor values in the voltage dividers without changing the firmware scale. Do not confuse 200 ohm (red-black-brown) with 200k (red-black-yellow).
- Resistors on hand: 4.7 (unit unconfirmed; if it is ohms it has no use here), 200, 1k, 2.2k, 4.99k, 10k, 20k, 30k, 100k, 200k, 499k.

## Ballast physics (why the plumbing is the way it is)
- A sealed tank only takes in water by compressing its trapped air. Fraction of the air space that fills = h / (10.3 + h), with h the valve depth in metres: 2.4% at 0.25 m, 4.6% at 0.5 m, 8.8% at 1 m, 16% at 2 m. With 5 L of air that is 120, 230, 440 and 810 g.
- So the sub must be trimmed very close to neutral, and ballast cannot start a dive from the surface. Drive down with thrust and elevators first.
- A centrifugal pump at a fixed speed holds a pressure, not a volume. Running it continuously cannot hold a part-full tank, and the balance point is unstable with depth.
- A running pump blocks backflow; a stopped one does not. Hence the check valve.
- Open the valve in short bursts. Left open, the tank takes on more water the deeper the sub goes.
- There is no depth sensor in the design. Depth is held with elevators and forward thrust, trimmed slightly buoyant so the sub floats up on failure.

## Software
- Pico runs MicroPython. The Pi 4 reaches it over USB serial (`/dev/ttyACM0`, `mpremote`).
- There is no UART link and no RUN wire since v6. Reset the Pico by power-cycling the Pi's USB port (`uhubctl`). `software/PI_SETUP.md` and `software/flash_pico.sh` still describe the old UART and RUN wiring and need rewriting.
- Servos: `PWM(Pin(n))`, `freq(50)`, `duty_ns(us * 1000)`. 1000 to 2000 us is a safe range. `software/sysarch_demo.py` sweeps GP12 to GP15.
- Thruster ESC: servo-style signal, 1.0 to 2.0 ms with 1.5 ms as stop, both directions. Hold 1.5 ms for a few seconds at power-up to arm. Apply the throttle cap here.
- Pump and valve: plain GPIO outputs, created with `value=0`. Always drive them low in a `finally` block. Optional: ramp GP19 with PWM over about 0.5 s if the pump stalls the boost at start-up.
- `software/pumptest.py` is the bench on/off test. It uses GP16 for convenience; the real pump pin is GP19.
- Battery limits: warn at 10.8 V, stop and surface at 10.2 V, or when any cell is under 3.3 V. The buck drops out at 9 V.
- If USB drops, the Pico loses power: gates fall low (pump off, valve closed) and the ESC stops on signal loss.

## Open items
- Valve: choose a 24 V, normally closed, direct-acting part and record its coil wattage.
- Check valve for the pump outlet; hose and clamps once fittings are measured.
- Pump start through the boost with the battery near 10 V: not yet tested.
- Read the number on the boost's input fuse (needs 7.5 to 10 A, mini blade).
- Buck output voltage under no load: not recorded. Up to about 7.6 V is acceptable for the Hitec servos.
- Thruster current at the throttle cap: not measured.
- Confirm which drybox size was ordered (75 mm tall per the BOM link, or 114 mm tall per the cart) and that it fits the hull.
- Thruster cable diameter against the M16 gland range.
- Air volume of the sealed tank, to size the ballast change.
- 100 nF capacitors, potting epoxy, female headers for the Pico, glue-lined heat shrink, silicone wire.
- Draw v11: schematic, wiring guide, `edits.md` entry. Update the BOM thruster row, the resistor note and the shifted Current and Gauge columns.

## Files and tools
- `kicad_files/AATV_v9/`: v9 schematic and PDF (KiCad 7 format; opens in KiCad 10). Custom symbols in `AATV.kicad_sym` through the project `sym-lib-table`. Older versions are in `kicad_files/AATV/` as `AATV_backup_v*.kicad_sch`.
- `tools/schematic_gen/`: Python generator. Latest: `python3 layout7.py out.kicad_sch` (helpers `gen.py`, `libs.py`, `custom.py`). Needs KiCad 7 symbol libraries at `/usr/share/kicad/symbols`. `netdump.py` prints nets from `kicad-cli sch export netlist --format kicadxml`. kicad-cli 7 has no ERC; run ERC in KiCad 10.
- The ADS1115 library symbol extends another symbol and breaks the generator. Use `Analog_ADC:ADS1015IDGS` (same pinout) with the value "ADS1115".
- `tools/wiring_guide/`: run from that folder. v9 guide: `python3 page7.py out.html` (`diagram7.build()` returns the SVG). v10 draft diagram: `diagram8.py`. The SVG styling uses CSS variables defined on `.sheet`, so wrap the SVG in `<div class="sheet">` when rendering it alone.
- One folder up from the repo: `AATV_wiring_guide_v9.html`, `AATV_wiring_v9.png`, `AATV_wiring_v10_draft.png`, and `old-wiring/`.
- BOM: Google Sheet "BOM" (id `1EmhEsombVcgAmiwsgjCxAug_wP34TvZpDY4gXu9PxH4`). Tab "BOM": headers in row 4; columns Item, Use, Type, Link, Amount, Unit Price, Final Price, Notes, then data sheet, documentation, pressure, waterproofness, Current, Gauge. Three sections: to buy (with a Total row), Owned, Not buying. Green rows are ordered. Tab "Orders" lists each order's links. Final Price is `=IF(OR(E="",F=""),"",E*F)`; the Total sums the whole to-buy block.
- Amazon product pages cannot be fetched by Claude. Ask for a screenshot or pasted page text.

## Conventions
- Reference names in use: F1 main fuse, SW1 kill switch, J2 EC5, J3 balance lead, BB1/BB2 bus bar rows, U1 buck, U4 ADS1115, U5 boost, U6 switch board (Q1/D3 pump, Q2/D4 valve), M3 pump, SV1 valve, MT1 thruster, M4/M5 rudder servos, M6/M7 elevator servos, TB2/TB3 servo leads, TB4 thruster signal, TB5 pump enable, TB8 valve enable, TB7 7.5 V in, TA2 leak sensor, G1 to G4 glands.
- Net names in the v9 schematic: VBAT, BAT_RAW, BAT_FUSED, GND, SERVO_7V4, +3V3, M4_PWM to M7_PWM, THR_PWM, I2C_SDA, I2C_SCL, BAL_C1, BAL_C2, ADC_C1 to ADC_C3, LEAK_MAIN, VBUS_PICO, 5V_PI, GND_PI. Rename SERVO_7V4 to SERVO_7V5 in v11.
- Wire colors in the guide: red 12 V, maroon 24 V, black GND, orange servo rail, purple 3.3 V, blue servo PWM, yellow thruster PWM, pink pump enable, brown valve enable, green I2C and balance, cyan leak.
- When the design changes: add an entry to `edits.md`, update `DESIGN_AND_PROGRESS.md` and this file, regenerate the schematic and guide, and re-run the netlist comparison so they stay in sync.
