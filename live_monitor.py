import tkinter as tk
from tkinter import ttk
import cv2
import time
import os
from datetime import datetime
from PIL import Image, ImageTk
from detection_engine import (process_frame, get_alert_settings,
                               log_detection, save_snapshot)
from alert_system import trigger_alert

BG_DARK    = "#0A1628"
BG_PANEL   = "#0F2044"
BG_CARD    = "#162950"
FIRE_COLOR = "#FF4C00"
SMOKE_COLOR= "#AAAAAA"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#8BA3C7"
SUCCESS    = "#00C896"
DANGER     = "#FF4C4C"
WARNING    = "#FFB84C"
BLUE_ACCENT= "#1E6FD9"


class LiveMonitor:
    def __init__(self, root):
        self.root    = root
        self.root.title("Fire Detection — Live Monitor")
        self.root.geometry("1080x660")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)
        self.center_window(1080, 660)

        self.cap          = None
        self.running      = False
        self.last_alert   = 0
        self.alert_cooldown = 15       # seconds between alerts
        self.frame_count  = 0

        self.build_ui()
        self.start_camera()            # ← auto-start like face recognition
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def build_ui(self):
        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=62)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🔥  FIRE DETECTION — LIVE MONITOR",
                 font=("Segoe UI", 13, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(side="left", padx=22, pady=15)

        self.clock_var = tk.StringVar()
        tk.Label(hdr, textvariable=self.clock_var,
                 font=("Segoe UI", 10),
                 bg=BG_PANEL, fg=FIRE_COLOR).pack(side="right", padx=22)

        tk.Button(hdr, text="⬅  Dashboard",
                  font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_GRAY,
                  relief="flat", cursor="hand2",
                  command=self.go_dashboard).pack(side="right", padx=8, pady=14)

        self.update_clock()

        # ── Body ─────────────────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=14, pady=12)

        # Camera feed (left)
        cam_outer = tk.Frame(body, bg="#000000", width=640, height=490)
        cam_outer.pack(side="left", padx=(0, 12))
        cam_outer.pack_propagate(False)
        self.cam_label = tk.Label(cam_outer, bg="#000000",
                                   text="⏳  Starting camera...",
                                   font=("Segoe UI", 12), fg=TEXT_GRAY)
        self.cam_label.pack(fill="both", expand=True)

        # Right info panel
        right = tk.Frame(body, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        # ── Status card ───────────────────────────────────────────────────────
        self.status_frame = tk.Frame(right, bg=BG_CARD, height=95)
        self.status_frame.pack(fill="x", pady=(0, 10))
        self.status_frame.pack_propagate(False)

        self.status_icon = tk.Label(self.status_frame, text="👁",
                                     font=("Segoe UI", 30),
                                     bg=BG_CARD, fg=TEXT_GRAY)
        self.status_icon.pack(side="left", padx=14)

        stxt = tk.Frame(self.status_frame, bg=BG_CARD)
        stxt.pack(side="left", pady=12)
        self.status_text = tk.Label(stxt, text="Monitoring...",
                                     font=("Segoe UI", 13, "bold"),
                                     bg=BG_CARD, fg=TEXT_GRAY)
        self.status_text.pack(anchor="w")
        self.conf_label = tk.Label(stxt, text="",
                                    font=("Segoe UI", 9),
                                    bg=BG_CARD, fg=TEXT_GRAY)
        self.conf_label.pack(anchor="w")

        # ── Last detection card ───────────────────────────────────────────────
        det_card = tk.Frame(right, bg=BG_CARD)
        det_card.pack(fill="x", pady=(0, 10))

        tk.Label(det_card, text="LAST DETECTION",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG_CARD, fg=TEXT_GRAY).pack(anchor="w", padx=14, pady=(10, 5))
        tk.Frame(det_card, bg=FIRE_COLOR, height=1).pack(fill="x", padx=14)

        self.det_vars = {}
        for label, key in [("Type",       "type"),
                            ("Confidence", "conf"),
                            ("Time",       "time"),
                            ("Snapshot",   "snap")]:
            row = tk.Frame(det_card, bg=BG_CARD)
            row.pack(fill="x", padx=14, pady=4)
            tk.Label(row, text=label, font=("Segoe UI", 9),
                     bg=BG_CARD, fg=TEXT_GRAY,
                     width=12, anchor="w").pack(side="left")
            var = tk.StringVar(value="—")
            self.det_vars[key] = var
            tk.Label(row, textvariable=var,
                     font=("Segoe UI", 9, "bold"),
                     bg=BG_CARD, fg=TEXT_WHITE,
                     anchor="w").pack(side="left")

        tk.Frame(det_card, height=6, bg=BG_CARD).pack()

        # ── Stats row ─────────────────────────────────────────────────────────
        stats_row = tk.Frame(right, bg=BG_DARK)
        stats_row.pack(fill="x", pady=(0, 10))

        self.stat_vars = {}
        for i, (label, key, color) in enumerate([
            ("🔥  Fire",  "fire",  FIRE_COLOR),
            ("💨  Smoke", "smoke", SMOKE_COLOR),
            ("⚠️  Total", "total", WARNING),
        ]):
            card = tk.Frame(stats_row, bg=BG_CARD, height=65)
            card.grid(row=0, column=i, padx=4, sticky="nsew")
            card.pack_propagate(False)
            stats_row.columnconfigure(i, weight=1)
            var = tk.StringVar(value="0")
            self.stat_vars[key] = var
            tk.Label(card, textvariable=var,
                     font=("Segoe UI", 20, "bold"),
                     bg=BG_CARD, fg=color).pack(pady=(8, 0))
            tk.Label(card, text=label,
                     font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_GRAY).pack()

        self.session_fire  = 0
        self.session_smoke = 0

        # ── Recent log table ──────────────────────────────────────────────────
        tk.Label(right, text="SESSION DETECTIONS",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG_DARK, fg=TEXT_GRAY).pack(anchor="w", pady=(4, 4))

        style = ttk.Style()
        style.configure("Live.Treeview",
                         background=BG_CARD, foreground=TEXT_WHITE,
                         fieldbackground=BG_CARD, rowheight=25,
                         font=("Segoe UI", 8))
        style.configure("Live.Treeview.Heading",
                         background=BG_PANEL, foreground=FIRE_COLOR,
                         font=("Segoe UI", 8, "bold"))
        style.map("Live.Treeview",
                  background=[("selected", BLUE_ACCENT)])

        self.live_log = ttk.Treeview(right,
                                      columns=("Type", "Confidence", "Time"),
                                      show="headings",
                                      style="Live.Treeview", height=6)
        for col, w in zip(("Type", "Confidence", "Time"), [80, 100, 130]):
            self.live_log.heading(col, text=col)
            self.live_log.column(col, width=w)
        self.live_log.pack(fill="x")
        self.live_log.tag_configure("fire",  foreground=FIRE_COLOR)
        self.live_log.tag_configure("smoke", foreground=SMOKE_COLOR)

    # ── Camera ────────────────────────────────────────────────────────────────
    def start_camera(self):
        """Auto-start camera exactly like face recognition system"""
        print("[INFO] Opening camera...")
        self.cap     = cv2.VideoCapture(0)
        time.sleep(0.8)

        if not self.cap.isOpened():
            self.cam_label.config(text="❌  Camera not found.\nCheck your webcam connection.")
            return

        self.running = True
        print("[INFO] Camera started. Monitoring for fire/smoke...")
        self.update_frame()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.root.after(100, self.update_frame)
            return

        frame = cv2.resize(frame, (630, 480))
        self.frame_count += 1

        # Process every 2nd frame for performance
        if self.frame_count % 2 == 0:
            settings         = get_alert_settings()
            min_conf         = settings.get("confidence", 0.45)
            display, dets    = process_frame(frame, min_conf)
        else:
            display = frame.copy()
            dets    = []

        if dets:
            best     = max(dets, key=lambda x: x[1])
            det_type = best[0]
            conf     = best[1]
            now      = datetime.now()

            # Update status
            if det_type == "FIRE":
                bg = "#2E0800"
                self.status_frame.config(bg=bg)
                self.status_icon.config(text="🔥", bg=bg, fg=FIRE_COLOR)
                self.status_text.config(text="⚠  FIRE DETECTED!",
                                         bg=bg, fg=FIRE_COLOR)
                self.conf_label.config(text=f"Confidence: {conf:.1%}",
                                        bg=bg, fg="#FF9966")
                self.session_fire += 1

            else:
                bg = "#252525"
                self.status_frame.config(bg=bg)
                self.status_icon.config(text="💨", bg=bg, fg=SMOKE_COLOR)
                self.status_text.config(text="⚠  SMOKE DETECTED!",
                                         bg=bg, fg=WARNING)
                self.conf_label.config(text=f"Confidence: {conf:.1%}",
                                        bg=bg, fg=WARNING)
                self.session_smoke += 1

            # Update stats
            total = self.session_fire + self.session_smoke
            self.stat_vars["fire"].set(str(self.session_fire))
            self.stat_vars["smoke"].set(str(self.session_smoke))
            self.stat_vars["total"].set(str(total))

            # Update last detection card
            self.det_vars["type"].set(det_type)
            self.det_vars["conf"].set(f"{conf:.1%}")
            self.det_vars["time"].set(now.strftime("%H:%M:%S"))

            # Alert cooldown
            if time.time() - self.last_alert > self.alert_cooldown:
                snapshot = save_snapshot(frame, det_type)
                log_detection(det_type, conf, snapshot)
                trigger_alert(settings, det_type, conf, snapshot)
                self.det_vars["snap"].set(os.path.basename(snapshot))
                self.last_alert = time.time()

                # Add to session log
                self.live_log.insert("", 0,
                    values=(det_type, f"{conf:.1%}", now.strftime("%H:%M:%S")),
                    tags=(det_type.lower(),))
                children = self.live_log.get_children()
                if len(children) > 8:
                    self.live_log.delete(children[-1])

        else:
            # Normal — no detection
            self.status_frame.config(bg=BG_CARD)
            self.status_icon.config(text="👁", bg=BG_CARD, fg=TEXT_GRAY)
            self.status_text.config(text="Monitoring...",
                                     bg=BG_CARD, fg=TEXT_GRAY)
            self.conf_label.config(text="", bg=BG_CARD)

        # Overlay timestamp on frame
        cv2.putText(display,
                    datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
                    (10, 468), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (180, 180, 180), 1)

        # Show in Tkinter
        img   = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.cam_label.imgtk = imgtk
        self.cam_label.config(image=imgtk, text="")

        self.root.after(30, self.update_frame)

    def update_clock(self):
        self.clock_var.set(datetime.now().strftime("%d %b %Y  |  %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def go_dashboard(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()
        import dashboard
        dashboard.launch()

    def on_close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()


def launch():
    root = tk.Tk()
    LiveMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    launch()