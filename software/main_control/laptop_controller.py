"""Laptop side: read the Xbox controller and send commands to the Pi over SSH.

Run on the laptop:
    python3 laptop_controller.py --host pi@192.168.50.1
    python3 laptop_controller.py --show            # print raw axes/buttons, no SSH
    python3 laptop_controller.py --dry-run         # print the packets, no SSH

Controls (xpad driver numbering, check with --show if yours differs):
    hold RB 1 s     ARM (only if thrust stick is centred and triggers released)
    tap RB, Back    DISARM
    left stick Y    thruster (up = forward, down = reverse)
    right stick X   rudder fins (left/right)
    right stick Y   elevator fins (up = nose up)
    hold LT         valve open (let water in, descend)
    hold RT         pump on (push water out, ascend)
    LB              EMERGENCY ASCENT: thruster stops, valve closed, pump on.
                    Works even when disarmed. Disarms you afterwards.
Until armed, thruster, fins, pump and valve all stay neutral.

One ssh session stays open. Each line is:  C thr rud elv pump valve arm emerg
thr, rud, elv are -100..100; the rest are 0 or 1.
"""
import argparse
import subprocess
import sys
import threading
import time

import pygame

# ---- controller mapping (Linux xpad numbering) ---------------------------------
AX_LY, AX_RX, AX_RY, AX_LT, AX_RT = 1, 3, 4, 2, 5
BTN_LB, BTN_RB, BTN_BACK = 4, 5, 6
DEADZONE = 0.12
TRIGGER_ON = 0.5          # triggers rest at -1 (or 0 before first touch) and go to +1
ARM_HOLD_S = 1.0
SEND_HZ = 20
STOP = "C 0 0 0 0 0 0 0"


def shape(v):
    """Deadzone, then rescale so the output still reaches +-1."""
    if abs(v) < DEADZONE:
        return 0.0
    sign = 1 if v > 0 else -1
    return sign * (abs(v) - DEADZONE) / (1 - DEADZONE)


def to_pct(v):
    return int(round(max(-1.0, min(1.0, v)) * 100))


class Arming:
    """Tracks the armed state and the RB hold timer."""

    def __init__(self):
        self.armed = False
        self.rb_prev = False
        self.rb_since = None
        self.consumed = False    # this RB press already did its job

    def update(self, now, rb, back, emergency, safe):
        if back or emergency:
            self.armed = False
        if rb and not self.rb_prev:            # new press
            self.rb_since = now
            self.consumed = False
            if self.armed:                     # tap while armed = disarm
                self.armed = False
                self.consumed = True
        if (rb and not self.armed and not self.consumed and safe
                and self.rb_since is not None and now - self.rb_since >= ARM_HOLD_S):
            self.armed = True
            self.consumed = True
        if not rb:
            self.rb_since = None
        self.rb_prev = rb
        return self.armed


def build_packet(js, arming, now=None):
    pygame.event.pump()
    now = time.time() if now is None else now
    lb = bool(js.get_button(BTN_LB))
    rb = bool(js.get_button(BTN_RB))
    back = bool(js.get_button(BTN_BACK))
    lt = js.get_axis(AX_LT) > TRIGGER_ON
    rt = js.get_axis(AX_RT) > TRIGGER_ON
    thr_f = -shape(js.get_axis(AX_LY))
    safe = thr_f == 0.0 and not lt and not rt and not lb

    armed = arming.update(now, rb, back, lb, safe)

    if lb:                                   # emergency ascent, any time
        return "C 0 0 0 0 0 0 1"
    if not armed:
        return STOP

    thr = to_pct(thr_f)
    rud = to_pct(shape(js.get_axis(AX_RX)))
    elv = to_pct(-shape(js.get_axis(AX_RY)))
    pump = 1 if rt else 0
    valve = 1 if lt else 0
    if pump and valve:                       # never both; the Pico enforces this too
        pump = valve = 0
    return f"C {thr} {rud} {elv} {pump} {valve} 1 0"


def show(js):
    print("Move sticks and press buttons. Ctrl-C to quit.")
    while True:
        pygame.event.pump()
        axes = [f"{js.get_axis(i):+.2f}" for i in range(js.get_numaxes())]
        btns = [i for i in range(js.get_numbuttons()) if js.get_button(i)]
        print("\raxes", axes, "buttons down", btns, "   ", end="", flush=True)
        time.sleep(0.05)


def read_pico(proc):
    for line in proc.stdout:
        print("\r" + line.strip() + "          ", end="", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="aatv@192.168.50.1")
    ap.add_argument("--remote-script", default="/home/aatv/pi_forwarder.py")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        sys.exit("No controller found. Plug it in or pair it to the laptop first.")
    js = pygame.joystick.Joystick(0)
    js.init()
    print("Controller:", js.get_name())

    if args.show:
        show(js)
        return

    proc = None
    if not args.dry_run:
        # ServerAlive* makes ssh give up within ~6 s if the Bluetooth link dies.
        cmd = ["ssh", "-o", "ServerAliveInterval=2", "-o", "ServerAliveCountMax=3",
               args.host, "python3", "-u", args.remote_script]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                text=True, bufsize=1)
        threading.Thread(target=read_pico, args=(proc,), daemon=True).start()

    arming = Arming()
    period = 1.0 / SEND_HZ
    try:
        while True:
            t0 = time.time()
            pkt = build_packet(js, arming)
            if proc is None:
                print("\r" + pkt + ("  ARMED " if arming.armed else "  safe  "), end="", flush=True)
            else:
                if proc.poll() is not None:
                    sys.exit(f"\nssh ended (code {proc.returncode}). Motors stopped on the Pi.")
                proc.stdin.write(pkt + "\n")
                proc.stdin.flush()
            time.sleep(max(0.0, period - (time.time() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.stdin.write(STOP + "\n")
                proc.stdin.flush()
                proc.stdin.close()
            except OSError:
                pass


if __name__ == "__main__":
    main()
