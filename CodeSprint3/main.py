"""
rover_control.py  —  Interface de contrôle du Rover IPSA
─────────────────────────────────────────────────────────
Lancement : python rover_control.py

Raccourcis clavier :
  Z / ↑      → Avancer
  S / ↓      → Reculer
  D          → 360° Droite
  X          → Strap Droit
  W          → Strap Gauche
  N / Espace → STOP

La carte à droite montre la position estimée du rover en temps réel.
"""

import tkinter as tk
from tkinter import messagebox
import socket
import time
import math

HOST = "192.168.4.1"
PORT = 8080

# ─── Calibration odométrie ─────────────────────────────────────────────────────
CM_PER_SEC  = 4.7    # cm/s en avance/recul
DEG_PER_SEC = 45.0   # °/s en rotation
CM_PER_SEC_STRAP = 3.5  # cm/s en latéral

# ─── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0f0f0f"
PANEL   = "#1a1a1a"
BORDER  = "#2a2a2a"
FG      = "#e0e0e0"
FG_DIM  = "#555555"
ACCENT  = "#00d4ff"
RED     = "#ff3b3b"
GREEN   = "#00c853"
YELLOW  = "#ffd600"
BTN_BG  = "#222222"
FONT    = ("Courier New", 10, "bold")
FONT_SM = ("Courier New", 8)
FONT_XL = ("Courier New", 18, "bold")

MAP_BG      = "#0a0a0a"
MAP_GRID    = "#1a1a1a"
MAP_AXIS    = "#2a2a2a"
TRAIL_COLOR = "#00d4ff"
ROVER_COLOR = "#ff3b3b"


# ══════════════════════════════════════════════════════════════════════════════
#  CARTE TEMPS RÉEL
# ══════════════════════════════════════════════════════════════════════════════

class MapCanvas(tk.Canvas):
    SCALE    = 3.0    # pixels par cm
    GRID_CM  = 25     # espacement grille en cm

    def __init__(self, master, **kwargs):
        super().__init__(master, bg=MAP_BG, **kwargs)
        self.trail   = [(0.0, 0.0)]
        self.rover_x = 0.0
        self.rover_y = 0.0
        self.rover_heading = 0.0
        self.bind("<Configure>", lambda e: self._redraw())

    def _to_px(self, x_cm, y_cm):
        w = self.winfo_width()
        h = self.winfo_height()
        cx = w // 2
        cy = h // 2
        px = cx + y_cm * self.SCALE
        py = cy - x_cm * self.SCALE
        return px, py

    def _redraw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2: return

        cx, cy = w // 2, h // 2
        step = self.GRID_CM * self.SCALE

        # Grille
        x = cx % step
        while x < w:
            self.create_line(x, 0, x, h, fill=MAP_GRID, width=1)
            x += step
        y = cy % step
        while y < h:
            self.create_line(0, y, w, y, fill=MAP_GRID, width=1)
            y += step

        # Axes
        self.create_line(cx, 0, cx, h, fill=MAP_AXIS, width=1)
        self.create_line(0, cy, w, cy, fill=MAP_AXIS, width=1)

        # Labels
        for i in range(-10, 11):
            if i == 0: continue
            val = i * self.GRID_CM
            px, py = self._to_px(val, 0)
            if 0 < py < h:
                self.create_text(cx + 4, py, anchor="w", text=f"{val}", fill=FG_DIM, font=("Courier New", 6))
            px2, py2 = self._to_px(0, val)
            if 0 < px2 < w:
                self.create_text(px2, cy - 4, anchor="s", text=f"{val}", fill=FG_DIM, font=("Courier New", 6))

        # Origine
        ox, oy = self._to_px(0, 0)
        self.create_oval(ox - 3, oy - 3, ox + 3, oy + 3, fill=FG_DIM, outline="")

        # Trajectoire
        if len(self.trail) >= 2:
            pts = []
            for (x, y) in self.trail:
                px, py = self._to_px(x, y)
                pts.extend([px, py])
            self.create_line(*pts, fill=TRAIL_COLOR, width=2, joinstyle="round", smooth=True)

        for (x, y) in self.trail:
            px, py = self._to_px(x, y)
            self.create_oval(px - 2, py - 2, px + 2, py + 2, fill=TRAIL_COLOR, outline="")

        # Rover
        self._draw_rover()

        # Coordonnées
        self.create_text(6, h - 6, anchor="sw",
                         text=f"x={self.rover_x:.1f}cm  y={self.rover_y:.1f}cm  cap={self.rover_heading:.0f}°",
                         fill=FG_DIM, font=("Courier New", 7))

    def _draw_rover(self):
        px, py = self._to_px(self.rover_x, self.rover_y)
        s  = 10
        hr = math.radians(self.rover_heading)
        tip = (px + s * math.sin(hr),   py - s * math.cos(hr))
        bl  = (px + s * math.sin(hr + 2.4), py - s * math.cos(hr + 2.4))
        br  = (px + s * math.sin(hr - 2.4), py - s * math.cos(hr - 2.4))
        self.create_polygon(tip[0], tip[1], bl[0], bl[1], br[0], br[1], fill=ROVER_COLOR, outline="#ff7070", width=1)

    def update_pos(self, x, y, heading):
        self.rover_x = x
        self.rover_y = y
        self.rover_heading = heading
        if math.hypot(x - self.trail[-1][0], y - self.trail[-1][1]) > 0.5:
            self.trail.append((x, y))
        self._redraw()

    def reset(self):
        self.trail = [(0.0, 0.0)]
        self.rover_x = 0.0
        self.rover_y = 0.0
        self.rover_heading = 0.0
        self._redraw()


# ══════════════════════════════════════════════════════════════════════════════
#  ODOMÉTRIE
# ══════════════════════════════════════════════════════════════════════════════

class Odometry:
    def __init__(self):
        self.x       = 0.0
        self.y       = 0.0
        self.heading = 0.0
        self.cmd     = None 
        self.WHEEL_DIAMETER = 6
        self.MAX_RPM = 300

    def speed_to_cm_s(self, speed):
        rpm = (speed * self.MAX_RPM) / 1000
        return (rpm * math.pi * self.WHEEL_DIAMETER) / 60
    
    def tick(self, dt: float):
        speed = 50
        v = self.speed_to_cm_s(speed)

        if self.cmd == "z":  # avancer
            self.x += v * dt * math.cos(math.radians(self.heading))
            self.y += v * dt * math.sin(math.radians(self.heading))

        elif self.cmd == "s":  # reculer
            self.x -= v * dt * math.cos(math.radians(self.heading))
            self.y -= v * dt * math.sin(math.radians(self.heading))

        elif self.cmd == "d":  # 360 Droite
            WHEEL_BASE = 12
            angular_speed = (v / WHEEL_BASE) * (180 / math.pi)
            self.heading += angular_speed * dt

        elif self.cmd == "x":  # strap droit
            self.x += v * dt * math.cos(math.radians(self.heading + 90))
            self.y += v * dt * math.sin(math.radians(self.heading + 90))

        elif self.cmd == "w":  # strap gauche
            self.x += v * dt * math.cos(math.radians(self.heading - 90))
            self.y += v * dt * math.sin(math.radians(self.heading - 90))

        self.heading %= 360
        return self.x, self.y, self.heading

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.cmd = None


# ══════════════════════════════════════════════════════════════════════════════
#  FENÊTRE PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════

class RoverControl:
    TICK_MS = 50

    def __init__(self, root: tk.Tk):
        self.root      = root
        self.sock      = None
        self.connected = False
        self.odo       = Odometry()
        self._last_tick = time.time()

        root.title("ROVER CONTROL")
        root.configure(bg=BG)
        root.resizable(True, True)

        self._build()
        self._bind_keys()
        self._tick()

    def _build(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        left  = tk.Frame(main, bg=BG)
        left.pack(side="left", fill="y", padx=(0, 0))

        sep = tk.Frame(main, bg=BORDER, width=1)
        sep.pack(side="left", fill="y")

        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        self._build_controls(left)
        self._build_map(right)

    def _build_controls(self, parent):
        tk.Label(parent, text="◈ ROVER CONTROL", font=FONT_XL, fg=ACCENT, bg=BG, pady=14).pack()
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20)

        # Connexion
        cf = tk.Frame(parent, bg=BG)
        cf.pack(pady=12, padx=24, fill="x")
        self._ip_var = tk.StringVar(value=HOST)
        tk.Label(cf, text="IP", font=FONT_SM, fg=FG_DIM, bg=BG, width=3).pack(side="left")
        tk.Entry(cf, textvariable=self._ip_var, font=FONT_SM, bg=PANEL, fg=FG, insertbackground=FG, relief="flat", bd=4, width=16).pack(side="left", padx=(4, 10))
        self._status_dot = tk.Label(cf, text="●", font=("Courier New", 14), fg=RED, bg=BG)
        self._status_dot.pack(side="right", padx=(0, 4))
        self._conn_btn = tk.Button(cf, text="CONNECT", font=FONT, bg=GREEN, fg="black", activebackground=GREEN, relief="flat", padx=12, pady=4, cursor="hand2", command=self._toggle_connect)
        self._conn_btn.pack(side="right", padx=(0, 8))

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 8))

        # Pavé directionnel
        pad = tk.Frame(parent, bg=BG)
        pad.pack(pady=4, padx=30)

        r1 = tk.Frame(pad, bg=BG); r1.pack()
        self._make_btn(r1, "▲\nAVANCER", "z", ACCENT, w=14, h=3).pack(pady=2)

        r2 = tk.Frame(pad, bg=BG); r2.pack()
        self._make_btn(r2, "◀\nSTRAP G", "w", YELLOW, w=10, h=3, fg_color="black").pack(side="left", padx=4, pady=2)
        self._make_btn(r2, "■\nSTOP",    "n", RED,    w=10, h=3).pack(side="left", padx=4, pady=2)
        self._make_btn(r2, "▶\nSTRAP D", "x", YELLOW, w=10, h=3, fg_color="black").pack(side="left", padx=4, pady=2)

        r3 = tk.Frame(pad, bg=BG); r3.pack()
        self._make_btn(r3, "▼\nRECULER", "s", BTN_BG, w=14, h=3).pack(pady=2)

        r4 = tk.Frame(pad, bg=BG); r4.pack(pady=(8, 0))
        self._make_btn(r4, "↻  360° DROITE", "d", BTN_BG, w=34, h=2).pack()

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)

        # Hints
        tk.Label(parent, text="Z/↑ Avancer   S/↓ Reculer\nW Strap G  X Strap D  D 360° Droite\nN/Espace Stop", font=FONT_SM, fg=FG_DIM, bg=BG, justify="center").pack(padx=20)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=8)

        # Log
        lf = tk.Frame(parent, bg=BG)
        lf.pack(padx=20, pady=(0, 14), fill="x")
        self._log_txt = tk.Text(lf, height=5, bg=PANEL, fg=FG_DIM, font=FONT_SM, relief="flat", state="disabled", bd=0)
        sb = tk.Scrollbar(lf, command=self._log_txt.yview, bg=PANEL)
        self._log_txt.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._log_txt.pack(fill="x")

    def _build_map(self, parent):
        header = tk.Frame(parent, bg=BG)
        header.pack(fill="x", padx=12, pady=(10, 4))
        tk.Label(header, text="CARTE", font=FONT, fg=ACCENT, bg=BG).pack(side="left")
        tk.Button(header, text="RESET", font=FONT_SM, bg=BTN_BG, fg=FG_DIM, activebackground=BTN_BG, relief="flat", cursor="hand2", padx=6, command=self._reset_map).pack(side="right")
        tk.Label(header, text="▲=Nord   grille=25cm", font=FONT_SM, fg=FG_DIM, bg=BG).pack(side="right", padx=10)

        self._map = MapCanvas(parent, width=400, height=400)
        self._map.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _make_btn(self, parent, label, cmd, color, w=10, h=2, fg_color="white"):
        b = tk.Button(parent, text=label, font=FONT, width=w, height=h, bg=color, fg=fg_color, activebackground=color, activeforeground=fg_color, relief="flat", cursor="hand2", command=lambda c=cmd: self._send(c))
        b.bind("<Enter>", lambda e, btn=b, c=color: btn.config(bg=self._lighten(c)))
        b.bind("<Leave>", lambda e, btn=b, c=color: btn.config(bg=c))
        return b

    @staticmethod
    def _lighten(hex_color):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"#{min(255,r+30):02x}{min(255,g+30):02x}{min(255,b+30):02x}"

    def _write_log(self, msg):
        self._log_txt.config(state="normal")
        self._log_txt.insert("end", f"{msg}\n")
        self._log_txt.see("end")
        self._log_txt.config(state="disabled")

    def _tick(self):
        now = time.time()
        dt  = now - self._last_tick
        self._last_tick = now
        x, y, hdg = self.odo.tick(dt)
        self._map.update_pos(x, y, hdg)
        self.root.after(self.TICK_MS, self._tick)

    def _reset_map(self):
        self.odo.reset()
        self._map.reset()
        self._write_log("Carte réinitialisée.")

    def _bind_keys(self):
        moves = {
            "z": "z", "Z": "z", "Up":   "z",
            "s": "s", "S": "s", "Down": "s",
            "d": "d", "D": "d",
            "x": "x", "X": "x",
            "w": "w", "W": "w",
            "n": "n", "N": "n", "space": "n",
        }
        for key, cmd in moves.items():
            self.root.bind(f"<{key}>", lambda e, c=cmd: self._send(c))
        self.root.bind("<Escape>", lambda e: self._send("exit"))

    def _toggle_connect(self):
        if self.connected: self._disconnect()
        else: self._connect()

    def _connect(self):
        ip = self._ip_var.get().strip()
        self._write_log(f"Connexion à {ip}:{PORT}...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((ip, PORT))
            s.settimeout(None)
            self.sock      = s
            self.connected = True
            self._conn_btn.config(text="DISCONNECT", bg=RED, fg="white", activebackground=RED)
            self._status_dot.config(fg=GREEN)
            self._write_log(f"✓ Connecté à {ip}:{PORT}")
        except Exception as e:
            self._write_log(f"✗ Échec : {e}")
            messagebox.showerror("Connexion impossible", f"Impossible de joindre {ip}:{PORT}\n\n{e}")

    def _disconnect(self):
        self.connected = False
        if self.sock:
            try: self.sock.close()
            except Exception: pass
            self.sock = None
        self.odo.cmd = None
        self._conn_btn.config(text="CONNECT", bg=GREEN, fg="black", activebackground=GREEN)
        self._status_dot.config(fg=RED)
        self._write_log("Déconnecté.")

    def _send(self, cmd: str):
        labels = {
            "z": "▲ AVANCER", "s": "▼ RECULER",
            "d": "↻ 360 DROITE",
            "x": "▶ STRAP DROIT", "w": "◀ STRAP GAUCHE",
            "n": "■ STOP", "exit": "EXIT",
        }
        if cmd in ("z", "s", "d", "x", "w"):
            self.odo.cmd = cmd
        elif cmd in ("n", "exit"):
            self.odo.cmd = None

        if not self.connected or not self.sock:
            self._write_log(f"[non connecté] {labels.get(cmd, cmd)}")
            return
        try:
            self.sock.send(cmd.encode())
            self._write_log(f"→ {labels.get(cmd, cmd)}")
        except Exception as e:
            self._write_log(f"Erreur : {e}")
            self._disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    app  = RoverControl(root)
    root.mainloop()