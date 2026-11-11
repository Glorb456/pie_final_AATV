# AA-TV electrical edits log

Newest first. Each entry says what changed, why, and which files carry it.

---

## v9 — 2026-11-06 · Single IP67 main box (proposal; v8.3 kept)

**Decisions (from the team)**
- All dryboxes combined into one IP67 box (191 × 111 × 58 mm inside). Everything outside it is flooded ballast space.
- Battery and its connectors move inside the box. Pump goes in its own drybox (or is sealed) outside.
- The box ships with 4× M16 cable glands. Out of the box: 4 servo leads, Pico USB, thruster, pump ESC output.

**Design changes vs v8.3**
- One solder-board (old Boards A + B merged). H1 harness, TA1 / TB1, D1, D3, D4, D5, D6, rear leak sensor TB6 and potted holes A2 / R2 / R3 removed.
- Glands: G1 USB, G2 thruster phase cable (TD1.2 ESC U2 now inside the box), G3 pump motor pair as a round 2-core cable to D2, G4 four servo leads (insert removed, gland body epoxy-potted).
- Battery: 3S pack drawn as three cells. EC5 (J2) is the in-box disconnect, then F1 (standard holder) and SW1.
- **Kill switch SW1 moved to the high side** (battery + → F1 → SW1 → VBAT). Required because the balance lead (J3) ties battery − to board GND, which would bypass a low-side switch.
- Battery monitor: J3 balance lead → dividers 47k/100k, 200k/100k, 330k/100k (+100 nF each) → ADS1115 U4 on I2C0 (GP20 SDA, GP21 SCL, 0x48), R15 / R16 4.7k pull-ups.
- Servo rail set to 7.4 V (net SERVO_7V4; Hitec DB777WP max 7.4 V).
- 10k pull-downs R13 / R14 on THR_PWM and PUMP_PWM.
- Free Pico pins: GP4, GP5, GP17, GP18, GP27 (optional 2nd leak sensor), GP28.

**Checks run**
- Netlist exported and every net checked against the plan. ERC not run (kicad-cli 7 has no ERC); run it in KiCad 10.

**Files**
- `kicad_files/AATV_v9/AATV_v9.kicad_sch` + `AATV_v9.pdf`; generator `tools/schematic_gen/layout7.py` (`python3 layout7.py out.kicad_sch`).
- Wiring guide: `../AATV_wiring_guide_v9.html` + `../AATV_wiring_v9.png` (`tools/wiring_guide/`: `python3 page7.py out.html`; `diagram7.build()` returns the SVG).

**Open items**
- Battery length fit: 169 mm pack in a 173 mm floor; consider a 5000 mAh pack.
- Kill switch is inside the sealed box (lid off to reach). Reed switch + ≥30 A relay to make it external.
- Check M16 gland clamp range against the USB, thruster and pump cables.

---

## v8.3 — 2026-11-05 · Battery back to one contact per pole (no wet splice)

**Decision (from the team):** no underwater splice. D1 returns to the v8.1 layout. All other v8.2 changes stay (30 A fuse, Molence terminals, 4-pos TB7, OONO bus bar, corrected servo and pump data).

**Changes vs v8.2**
- D1: 1 +12 V (after F1), 2 GND (after kill switch SW1), 3–4 dummy loop (net D1_LOOP restored). No battery-side splits.
- Trunk back to 2 × 14 AWG; bus bar uses one position per row for it (2 spare per row).

**Trade-off to remember:** D1 now carries each pole on a single 25 A contact behind a 30 A fuse. Realistic peaks (~25 A) sit at the contact rating, which is acceptable for short peaks. A 14 A pump would push it over; prefer a ~10 A pump, or drop the fuse to 25 A.

**Checks run:** v8.3 netlist vs guide, 76 pin checks, 0 mismatches.

**Superseded files (safe to delete):** `../AATV_wiring_guide_v8_2.html`, `../AATV_wiring_v8_2.png`, `kicad_files/AATV/AATV_v8_2.pdf` (v8.2 schematic kept as `AATV_backup_v8_2.kicad_sch`).

---

## v8.2 — 2026-11-05 · Battery back on two contacts per pole, 30 A fuse, BOM fixes

**Decisions (from the team)**
- D1 (battery) goes back to two DTP contacts per pole into the +12 V / GND bus bar inside the rear drybox. The D1 dummy loop is removed. D2 (pump) keeps its dummy loop.
- Main fuse raised to **30 A** (BOM).
- Screw terminals: **Molence 5.08 mm** 2/3/4-pos blocks, 10 A, 22–12 AWG (BOM; replaces the 2.54 mm 6 A / 26–18 AWG listing that couldn't take 14 AWG).
- Battery trunk: use the 14 AWG already bought, or 12 AWG if found.
- BOM wire roles corrected (14 AWG = outer, 20 AWG = inner). "Additional waterproof box" renamed to rear drybox.
- Servo rail stays 7.5 V. Hitec's DB777WP page lists 6.0–7.4 V but the package says 8.4 V; check the package before final assembly (fallback: set the buck to 7.2 V).

**Design changes vs v8.1**
- D1: 1–2 +12 V (after F1), 3–4 GND (after kill switch SW1). Net D1_LOOP removed.
- Battery side: + splits after F1, − splits after SW1, each into two 14 AWG wires (sealed Y-splice in adhesive heat shrink, or two ring terminals on a switch stud).
- Trunk: 4 × 14 AWG through R3; two positions per row on the bus bar.
- Bus bar: OONO 2×6 screw-clamp module (30 A), one row per pole: trunk ×2, buck, pump ESC, thruster feed, 1 spare. Check the two rows aren't bridged.
- TB7 (7.5 V into Board B) is now 4-pos: 1–2 +7.5 V, 3–4 GND, two 14 AWG per pole from the buck, so no 10 A terminal carries a full four-servo stall (≈13.8 A).
- Servo data corrected to the owned parts: 2× DB777WP (4.5 A stall at 7.4 V), 2× SW-1250MG (2.4 A stall). SW-1210SG removed from notes.
- Pump spec updated to the Seaflo reversible candidate (~10 A; 01 series 14 A). Current budget: typical ≈12 A, realistic peak ≈25 A; everything stalled at once ≈32 A would blow the 30 A fuse.

**Checks run**
- v8.2 KiCad netlist exported; the guide's D1–D6 pins (both halves), servo → TB2/TB3 pins and TB7 compared automatically: 76 pin checks, 0 mismatches.

**Superseded files (safe to delete)**
- `../AATV_wiring_guide_v8_1.html`, `../AATV_wiring_v8_1.png`, `kicad_files/AATV/AATV_v8_1.pdf` (v8.1 schematic kept as `AATV_backup_v8_1.kicad_sch`).

**Open items**
- Pump and pump ESC not chosen. ESC must exceed the pump's stall current.
- Confirm the kill switch and fuse holder are rated ≥30 A DC.
- BOM cells still to update: screw terminal current/gauge (10 A, 22–12), 30 A fuse current column. Missing BOM lines: 6× 220 Ω, 1000 µF/16 V cap, 2 leak sensors, long micro-USB cable, adhesive heat shrink, open-barrel crimper, XT60 for the charge adapter.
- Servos are IP67 (1 m, 30 min); deeper or longer dives need extra sealing.

---

## v8.1 — 2026-11-04 · Dummy loops on battery and pump, servos potted

**Decisions (from the team)**
- Keep the battery on a DTP 4-pin. Instead of splitting each pole over two contacts, run one 14 AWG per pole and fill cavities 3–4 with a short dummy wire loop so the connector stays sealed.
- Servos will most likely be potted straight into the rear drybox (they're expensive, so no cutting into connectors unless needed). **Backup** if a lead can't reach the box: MGYOO 20 AWG 3-pin waterproof connectors (3pin-10Pack, $13.99, IP68, Weather Pack style), one per servo, inline in the wet zone.

**Design changes vs v8**
- D1 battery: 1 +12 V, 2 GND, 3–4 dummy loop (net D1_LOOP). No wet splits after the fuse and switch; trunk is 2 × 14 AWG.
- D2 pump: 1 pump +, 2 pump −, 3–4 dummy loop (net D2_LOOP). Same pattern.
- Dummy loop: ≈3 cm 14 AWG, contact crimped on each end, in cavities 3–4 on **both** halves (pins in the receptacle, sockets in the plug). Isolated: never loop a powered pin.
- Servo connectors D4/D5 removed. Servo factory leads potted uncut into R2. TB2 and TB3 become 6-position (sig / + / GND per servo).
- H1 connectors renamed D6/D7/D8 → **D4/D5/D6** (pins unchanged).
- DTP count 8 → **6**. 4Pin-12 Set ($29.99) leaves 6 spare; 2 × 4Pin-4 ($43.98) would leave 2.
- Bus bars: one 14 AWG per pole for the trunk, so 4 studs used (trunk, buck, pump ESC, thruster feed).
- Splices left: thruster ESC leads → 14 AWG pigtails (wet); battery lead → fuse holder / kill switch joins (or ring terminals on switch studs); pump ESC motor leads → 14 AWG only if too short; servo ↔ MGYOO pigtail only if the backup is used.

**Checks run**
- v8.1 KiCad netlist exported. Every D1–D6 pin (both halves) and every servo → TB2/TB3 pin in the guide compared automatically: 0 mismatches. D1_LOOP and D2_LOOP confirmed isolated.

**Superseded files (safe to delete)**
- `../AATV_wiring_guide_v8.html`, `../AATV_wiring_v8.png`, `kicad_files/AATV/AATV_v8.pdf` (v8 schematic kept as `AATV_backup_v8.kicad_sch`)
- Still from v7 if not yet removed: `kicad_files/AATV_planB/`, `../AATV_wiring_guide_v7.html`, `../AATV_wiring_planA_v7.png`, `../AATV_wiring_planB_v7.png`, `kicad_files/AATV/AATV_planA_v7.pdf`

**Open items**
- Measure each servo lead against its route to R2 before potting; order the MGYOO pack only if one falls short.
- If the MGYOO backup is used, check its per-pin current rating against servo stall current (up to 7.4 A for the SW-1210SG). Stall is brief, but 20 AWG contacts are at the low end.
- Pump model not chosen (target 12 V brushed, reversible, ≤5 A).
- `software/PI_SETUP.md` and `flash_pico.sh` still describe the old UART/RUN link.
- Run ERC in KiCad 10.

---

## v8 — 2026-11-04 · Wheels dropped, Deutsch DTP 4-pin only, 14 AWG marine outside

**Decisions (from the team)**
- Front driven wheels are fully abandoned (no wheel ESCs, motors or connector). Plan A/B split removed; there is one design.
- DT connectors don't fit the gauge and jacket of waterproof marine wire. Switched to **Deutsch DTP** (size-12 contacts, 12–14 AWG, 25 A each) from the Deutusacc Amazon listing (ASIN B0C49B4G3M), which only comes in 2- and 4-pin.

**Design changes vs v7**
- Every connector is a **DTP 4-pin**. 8 used: D1 battery, D2 pump, D3 thruster ESC, D4 rudder servos (M4, M5), D5 elevator servos (M6, M7), D6/D7/D8 = H1 pins 1–4 / 5–8 / 9–12.
- **Buy the 4Pin-12 Set ($29.99)**: 12 sets, 8 used, 4 spare, $2.50 each. Cheaper than 2 × 4Pin-4 ($43.98, no spares). No 2-pin sets needed.
- Every cavity is filled, so no seal plugs are needed: D1 and D2 use 2 contacts per pole; H1 spare pins 6–7 still carry wires.
- **Wire:** 14 AWG tinned marine for everything leaving a drybox or going through a DTP contact (H1 is now 12 × 14 AWG), plus power inside the boxes. 20 AWG hookup only for on-board signal jumpers and leak-sensor leads.
- Servos grouped two per connector: pin 1–2 signals, pin 3 shared +7.5 V, pin 4 shared GND (≤15 A if both stall, under 25 A).
- Board B terminals renumbered: TB1 H1 (12), TB2 rudder (4), TB3 elevator (4), TB4 thruster signal (2), TB5 pump ESC signal (2), TB6 rear leak (3), TB7 7.5 V in (2). TB7 (wheels) from v7 is gone.
- Board A: R7/R8 (wheel PWM) removed. GP17/GP18 free. H1 pins 6–7 renamed H1_SPARE6/7 (wired, unused).
- Bus bars now 5 studs (trunk ×2, buck, pump ESC, thruster feed). Fuse 20 A.
- Potted holes: A2 (H1), R2 (signal cables: H1, 2 servo cables, thruster signal pair), R3 (power: trunk, thruster feed, pump).
- Splices: wet (adhesive heat-shrink) at battery fuse/switch outputs, servo leads → 14 AWG, thruster ESC leads → 14 AWG, pump leads; dry inside rear box at pump ESC outputs.

**Checks run**
- KiCad v8 netlist exported; every D1–D8 pin in the guide's schedule compared against it: 0 mismatches.

**Superseded files (safe to delete)**
- `kicad_files/AATV_planB/` (v7 Plan B project)
- `../AATV_wiring_guide_v7.html`, `../AATV_wiring_planA_v7.png`, `../AATV_wiring_planB_v7.png`
- `kicad_files/AATV/AATV_planA_v7.pdf` (v7 schematic kept as `AATV_backup_v7.kicad_sch`)

**Open items**
- Pump model not chosen (target 12 V brushed, reversible, ≤5 A).
- Confirm the 4Pin-12 listing ships 12 complete sets (plug, receptacle, wedgelocks, 4 pins, 4 sockets each). Contacts are stamped: use an open-barrel crimper for 12–14 AWG.
- `software/PI_SETUP.md` and `flash_pico.sh` still describe the old UART/RUN link.
- Run ERC in KiCad 10.

---

## v7 — 2026-11-04 · Deutsch-only connectors, two wire gauges, Plan A / Plan B

**Decisions (from the team)**
- Cables are epoxy-potted into holes in the dryboxes. No panel-mount connectors on the boxes.
- Every disconnect outside the boxes is a waterproof **Deutsch DT** connector (aiming for one 6-pack). Inside the boxes, only 5.08 mm screw terminals and screw bus bars.
- Wire is limited to **two gauges**: HIGH = 14 AWG, LOW = 20 AWG.
- Two plans: **Plan A** keeps the front driven wheels. **Plan B** has no front driven motors.
- The TD1.2 thruster ESC is waterproof, so it moves to the wet zone next to the thruster. Its factory thruster cable stays intact.
- The ballast pump gets a reserved interface even though the model isn't chosen yet.

**What changed vs v6**
| Area | v6 | v7 |
|---|---|---|
| Box penetrations | M12/IP68 panel connectors + cable gland | Epoxy-potted holes: A2 (main, H1); R2 (rear, all 20 AWG); R3 (rear, all 14 AWG). A1 air-tube fitting unchanged |
| Battery connector | XT60W pair | D1 = DT 4-pin, two contacts per pole (26 A) |
| Main ↔ rear harness | IP68 12-pin panel connectors both ends | D4 = DT 12-pin in the wet zone; cable potted into both boxes |
| Servos | JR plugs on 2.54 mm headers | Cut the JR plugs; D3 = DT 12-pin (3 pins per servo); land on TB2 screw terminal |
| Thruster ESC | Inside rear drybox, power off XT60 Y-pigtail | Wet zone. Fed through D2 pins 1–4 (12 V pair + PWM + signal ground) |
| Pump | Spare PWM pin only | GP19 → TB4 → pump ESC U3 (dry, rear box) → R3 → D2 pins 5–6 → pump motor |
| Wheels (Plan A) | ESCs fed from wet Y-splice, signal via splice S2 | D5 = DT 8-pin: per-ESC 12 V pair + PWM/signal-GND pair, all from the rear box |
| 12 V distribution | Wet Y-splice + dry XT60 Y-pigtail | +12 V and GND screw bus bars (≥30 A) in the rear drybox, off the breadboard |
| Fuse | 30 A | Plan A 25 A, Plan B 20 A (sized to D1's 26 A paired contacts) |
| Wire gauges | 12/14/16/18/22–24 AWG | 14 AWG and 20 AWG only |
| Screw terminals | Mixed 3.5/5.08 mm | 5.08 mm everywhere (3.5 mm doesn't fit the 2.54 mm breadboard grid) |
| Board B headers | J5–J13 pin headers | All screw terminals TB1–TB7 |

**H1 pin order changed** (pins 6–8): 1–4 servos M4–M7 (GP12–15), 5 thruster (GP16), 6 wheel L (GP17), 7 wheel R (GP18), 8 pump (GP19), 9 rear leak (GP27), 10 3V3, 11–12 GND. In Plan B, pins 6–7 are spare and get cavity plugs.

**Deutsch count**: Plan A uses 5 (1× 4-pin, 2× 8-pin, 2× 12-pin). Plan B uses 4 (1× 4-pin, 1× 8-pin, 2× 12-pin). A generic 6-pack assortment (one each of 2/3/4/6/8/12) won't cover this; two 12-pins are needed.

**Checks run**
- Both KiCad schematics exported to netlists. Every DT pin, TA1/TB1/D4 (H1), and the guide's pin tables were compared automatically: 0 mismatches in either plan.
- Current per DT contact stays ≤13 A by design: trunk is split over 2 contacts per pole, the thruster is at most 13 A (8 A nominal), each wheel ESC has its own contact pair.

**Open items**
- Pump model not chosen. Target: 12 V brushed, reversible, ≤5 A, rated for submersion.
- Wheel motor current is an estimate (5–10 A running). Measure one.
- Check the wire insulation diameter fits the DT seals: thick silicone 14 AWG may be too fat, thin ESC/servo signal leads too thin.
- `software/PI_SETUP.md` and `flash_pico.sh` still describe the old UART/RUN wiring (Pico now talks over USB).
- Run ERC in KiCad 10 (files were generated in KiCad 7 format and checked by netlist only).

**Files**
- `kicad_files/AATV/AATV.kicad_sch`: Plan A (previous v6 kept as `AATV_backup_v6.kicad_sch`)
- `kicad_files/AATV/AATV_planA_v7.pdf`: rendered Plan A
- `kicad_files/AATV_planB/`: Plan B project (`AATV_planB.kicad_pro/.kicad_sch`, symbol lib, PDF)
- `../AATV_wiring_guide_v7.html`, `../AATV_wiring_planA_v7.png`, `../AATV_wiring_planB_v7.png`: wiring guide and diagrams
- `tools/`: generator scripts for the schematics and the guide

---

## v6 — 2026-11-03 · No PCB, two solder-boards

- Replaced the PCB with two solderable breadboards: Board A (Pico, main drybox) and Board B (servo/thruster logic + 7.5 V rail, rear drybox).
- Pico now powered and controlled over USB from the buoy Pi 4 through the air tube. Removed the BEC → VSYS feed, the UART link and the RUN reset wire.
- Servos on a 7.5 V buck in the rear drybox; thruster on 12 V.
- Schematic rebuilt as boxed sections (buoy, main drybox, harness, rear drybox, wet zone) with connector symbols. Added custom symbol library `AATV.kicad_sym` + project `sym-lib-table`.
- Previous v5 schematic saved as `AATV_backup_v5.kicad_sch`.
- Superseded by v7 (IP68 panel connectors, XT60W, JR headers all removed).
