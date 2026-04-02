import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import openpyxl, csv, os
from db_config import get_connection

BG_DARK    = "#0A1628"
BG_PANEL   = "#0F2044"
BG_CARD    = "#162950"
FIRE_COLOR = "#FF4C00"
BLUE_ACCENT= "#1E6FD9"
BLUE_LIGHT = "#4A9FFF"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#8BA3C7"
SUCCESS    = "#00C896"
DANGER     = "#FF4C4C"
WARNING    = "#FFB84C"


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Fire Detection System — Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_DARK)
        self.center_window(1100, 700)
        self.build_ui()
        self.load_stats()

    def center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg=BG_PANEL, width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🔥", font=("Segoe UI", 30),
                 bg=BG_PANEL, fg=FIRE_COLOR).pack(pady=(25, 4))
        tk.Label(sidebar, text="FIRE DETECTION",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack()
        tk.Label(sidebar, text="Admin Dashboard",
                 font=("Segoe UI", 9),
                 bg=BG_PANEL, fg=TEXT_GRAY).pack(pady=(0, 20))
        tk.Frame(sidebar, bg=FIRE_COLOR, height=1).pack(fill="x", padx=20)

        self.nav_btns = {}
        nav = [
            ("📊  Overview",       "overview"),
            ("📋  Detection Logs", "logs"),
            ("⚙️   Settings",      "settings"),
            ("📤  Export",         "export"),
        ]
        for label, key in nav:
            btn = tk.Button(sidebar, text=label,
                            font=("Segoe UI", 10),
                            bg=BG_PANEL, fg=TEXT_GRAY,
                            relief="flat", cursor="hand2",
                            anchor="w", padx=20,
                            activebackground=BG_CARD,
                            activeforeground=TEXT_WHITE,
                            command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", ipady=10, pady=1)
            self.nav_btns[key] = btn

        tk.Frame(sidebar, bg=BG_CARD, height=1).pack(fill="x", padx=20, pady=15)
        tk.Button(sidebar, text="📷  Live Monitor",
                  font=("Segoe UI", 10, "bold"),
                  bg=FIRE_COLOR, fg=TEXT_WHITE, relief="flat",
                  cursor="hand2", padx=20,
                  activebackground="#CC3A00",
                  command=self.open_monitor).pack(fill="x", ipady=10)
        tk.Button(sidebar, text="🚪  Logout",
                  font=("Segoe UI", 10),
                  bg=BG_PANEL, fg=DANGER, relief="flat",
                  cursor="hand2", padx=20,
                  activebackground=BG_CARD,
                  command=self.logout).pack(fill="x", ipady=8, pady=5)

        self.content = tk.Frame(self.root, bg=BG_DARK)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        self.build_overview()
        self.build_logs()
        self.build_settings()
        self.build_export()
        self.show_page("overview")

    def show_page(self, key):
        for f in self.pages.values():
            f.pack_forget()
        for k, b in self.nav_btns.items():
            b.config(bg=BG_PANEL, fg=TEXT_GRAY)
        self.pages[key].pack(fill="both", expand=True)
        self.nav_btns[key].config(bg=BG_CARD, fg=TEXT_WHITE)
        if key == "logs":     self.load_logs()
        if key == "overview": self.load_stats()

    # ── Overview ──────────────────────────────────────────────────────────────
    def build_overview(self):
        page = tk.Frame(self.content, bg=BG_DARK)
        self.pages["overview"] = page

        hdr = tk.Frame(page, bg=BG_PANEL, height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📊  System Overview",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(side="left", padx=25, pady=20)
        tk.Button(hdr, text="🔄 Refresh",
                  font=("Segoe UI", 9),
                  bg=FIRE_COLOR, fg=TEXT_WHITE, relief="flat",
                  cursor="hand2",
                  command=self.load_stats).pack(side="right", padx=20, pady=18)

        cards = tk.Frame(page, bg=BG_DARK)
        cards.pack(fill="x", padx=25, pady=18)

        self.stat_vars = {}
        for i, (icon, label, key, color) in enumerate([
            ("🔥", "Total Fire",   "fire",  FIRE_COLOR),
            ("💨", "Total Smoke",  "smoke", WARNING),
            ("📅", "Today",        "today", DANGER),
            ("📋", "All Logs",     "all",   BLUE_ACCENT),
        ]):
            card = tk.Frame(cards, bg=BG_CARD, height=112)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            card.pack_propagate(False)
            cards.columnconfigure(i, weight=1)
            tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
            inner = tk.Frame(card, bg=BG_CARD)
            inner.pack(side="left", fill="both", expand=True, padx=14, pady=14)
            tk.Label(inner, text=icon, font=("Segoe UI", 22),
                     bg=BG_CARD, fg=color).pack(anchor="w")
            var = tk.StringVar(value="0")
            self.stat_vars[key] = var
            tk.Label(inner, textvariable=var,
                     font=("Segoe UI", 22, "bold"),
                     bg=BG_CARD, fg=TEXT_WHITE).pack(anchor="w")
            tk.Label(inner, text=label,
                     font=("Segoe UI", 8),
                     bg=BG_CARD, fg=TEXT_GRAY).pack(anchor="w")

        tk.Label(page, text="Recent Detections",
                 font=("Segoe UI", 11, "bold"),
                 bg=BG_DARK, fg=TEXT_WHITE).pack(anchor="w", padx=25, pady=(8, 5))

        tbl = tk.Frame(page, bg=BG_DARK)
        tbl.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Fire.Treeview",
                         background=BG_CARD, foreground=TEXT_WHITE,
                         fieldbackground=BG_CARD, rowheight=30,
                         font=("Segoe UI", 9))
        style.configure("Fire.Treeview.Heading",
                         background=BG_PANEL, foreground=FIRE_COLOR,
                         font=("Segoe UI", 9, "bold"))
        style.map("Fire.Treeview",
                  background=[("selected", BLUE_ACCENT)])

        cols = ("Type", "Confidence", "Time", "Snapshot", "Alert Sent")
        self.ov_tree = ttk.Treeview(tbl, columns=cols,
                                     show="headings",
                                     style="Fire.Treeview", height=10)
        for col, w in zip(cols, [90, 110, 160, 280, 90]):
            self.ov_tree.heading(col, text=col)
            self.ov_tree.column(col, width=w)

        sb = ttk.Scrollbar(tbl, orient="vertical", command=self.ov_tree.yview)
        self.ov_tree.configure(yscrollcommand=sb.set)
        self.ov_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def load_stats(self):
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            today  = datetime.now().strftime("%Y-%m-%d")

            cursor.execute("SELECT COUNT(*) FROM DetectionLogs WHERE DetectionType='FIRE'")
            self.stat_vars["fire"].set(str(cursor.fetchone()[0]))
            cursor.execute("SELECT COUNT(*) FROM DetectionLogs WHERE DetectionType='SMOKE'")
            self.stat_vars["smoke"].set(str(cursor.fetchone()[0]))
            cursor.execute("SELECT COUNT(*) FROM DetectionLogs WHERE CAST(DetectedAt AS DATE)=?", today)
            self.stat_vars["today"].set(str(cursor.fetchone()[0]))
            cursor.execute("SELECT COUNT(*) FROM DetectionLogs")
            self.stat_vars["all"].set(str(cursor.fetchone()[0]))

            cursor.execute("""
                SELECT TOP 10 DetectionType, Confidence, DetectedAt,
                       ISNULL(SnapshotPath,'—'),
                       CASE WHEN AlertSent=1 THEN 'YES' ELSE 'NO' END
                FROM DetectionLogs ORDER BY DetectedAt DESC
            """)
            for item in self.ov_tree.get_children():
                self.ov_tree.delete(item)
            for row in cursor.fetchall():
                vals    = list(row)
                vals[1] = f"{vals[1]:.1%}"
                tag = "fire" if row[0] == "FIRE" else "smoke"
                self.ov_tree.insert("", "end", values=vals, tags=(tag,))
            self.ov_tree.tag_configure("fire",  foreground=FIRE_COLOR)
            self.ov_tree.tag_configure("smoke", foreground=WARNING)
            conn.close()
        except Exception as e:
            print(f"Stats error: {e}")

    # ── Logs ──────────────────────────────────────────────────────────────────
    def build_logs(self):
        page = tk.Frame(self.content, bg=BG_DARK)
        self.pages["logs"] = page

        hdr = tk.Frame(page, bg=BG_PANEL, height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📋  Detection Logs",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(side="left", padx=25, pady=20)
        tk.Button(hdr, text="🔄 Refresh",
                  font=("Segoe UI", 9),
                  bg=FIRE_COLOR, fg=TEXT_WHITE,
                  relief="flat", cursor="hand2",
                  command=self.load_logs).pack(side="right", padx=25, pady=18)

        tbl = tk.Frame(page, bg=BG_DARK)
        tbl.pack(fill="both", expand=True, padx=25, pady=15)

        cols = ("ID", "Type", "Confidence", "Detected At", "Snapshot", "Alert")
        self.log_tree = ttk.Treeview(tbl, columns=cols,
                                      show="headings",
                                      style="Fire.Treeview")
        for col, w in zip(cols, [50, 90, 100, 160, 300, 80]):
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=w)

        sb = ttk.Scrollbar(tbl, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=sb.set)
        self.log_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def load_logs(self):
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 300 LogID, DetectionType, Confidence,
                       DetectedAt, ISNULL(SnapshotPath,'—'),
                       CASE WHEN AlertSent=1 THEN 'YES' ELSE 'NO' END
                FROM DetectionLogs ORDER BY DetectedAt DESC
            """)
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            for row in cursor.fetchall():
                vals    = list(row)
                vals[2] = f"{vals[2]:.1%}"
                tag = "fire" if row[1] == "FIRE" else "smoke"
                self.log_tree.insert("", "end", values=vals, tags=(tag,))
            self.log_tree.tag_configure("fire",  foreground=FIRE_COLOR)
            self.log_tree.tag_configure("smoke", foreground=WARNING)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Settings ──────────────────────────────────────────────────────────────
    def build_settings(self):
        page = tk.Frame(self.content, bg=BG_DARK)
        self.pages["settings"] = page

        hdr = tk.Frame(page, bg=BG_PANEL, height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚙️  Alert Settings",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(side="left", padx=25, pady=20)

        form = tk.Frame(page, bg=BG_DARK, padx=55)
        form.pack(fill="both", expand=True, pady=20)

        self.svar = {}

        tk.Label(form, text="EMAIL ALERT SETTINGS",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG_DARK, fg=FIRE_COLOR).pack(anchor="w", pady=(0, 10))

        for label, key in [("Sender Gmail Address", "email_from"),
                            ("Gmail App Password",   "email_password"),
                            ("Recipient Email",      "email_to")]:
            tk.Label(form, text=label.upper(),
                     font=("Segoe UI", 8, "bold"),
                     bg=BG_DARK, fg=TEXT_GRAY).pack(anchor="w", pady=(8, 3))
            var  = tk.StringVar()
            self.svar[key] = var
            show = "●" if "password" in key else ""
            f    = tk.Frame(form, bg=BG_CARD)
            f.pack(fill="x")
            tk.Entry(f, textvariable=var, show=show,
                     bg=BG_CARD, fg=TEXT_WHITE,
                     insertbackground=TEXT_WHITE,
                     relief="flat", font=("Segoe UI", 11),
                     bd=0).pack(fill="x", ipady=10, padx=14)

        tk.Label(form, text="SYSTEM SETTINGS",
                 font=("Segoe UI", 10, "bold"),
                 bg=BG_DARK, fg=FIRE_COLOR).pack(anchor="w", pady=(22, 10))

        self.email_on = tk.BooleanVar(value=False)
        self.sound_on = tk.BooleanVar(value=True)

        for text, var in [("✅  Enable Email Alerts", self.email_on),
                           ("🔔  Enable Sound Alerts", self.sound_on)]:
            tk.Checkbutton(form, text=text, variable=var,
                           font=("Segoe UI", 10),
                           bg=BG_DARK, fg=TEXT_WHITE,
                           selectcolor=BG_CARD,
                           activebackground=BG_DARK).pack(anchor="w", pady=3)

        tk.Label(form, text="DETECTION SENSITIVITY",
                 font=("Segoe UI", 8, "bold"),
                 bg=BG_DARK, fg=TEXT_GRAY).pack(anchor="w", pady=(14, 3))

        self.conf_var = tk.DoubleVar(value=0.45)
        row = tk.Frame(form, bg=BG_DARK)
        row.pack(fill="x")
        tk.Scale(row, from_=0.1, to=0.9, resolution=0.05,
                 orient="horizontal", variable=self.conf_var,
                 bg=BG_DARK, fg=TEXT_WHITE, troughcolor=BG_CARD,
                 highlightthickness=0, length=300).pack(side="left")
        tk.Label(row, textvariable=self.conf_var,
                 font=("Segoe UI", 10, "bold"),
                 bg=BG_DARK, fg=FIRE_COLOR).pack(side="left", padx=10)

        tk.Button(form, text="💾  Save Settings",
                  font=("Segoe UI", 11, "bold"),
                  bg=FIRE_COLOR, fg=TEXT_WHITE,
                  relief="flat", cursor="hand2",
                  activebackground="#CC3A00",
                  command=self.save_settings).pack(anchor="w",
                  pady=20, ipady=10, padx=0)

        self.load_setting_vals()

    def load_setting_vals(self):
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 1 * FROM AlertSettings")
            row = cursor.fetchone()
            conn.close()
            if row:
                self.email_on.set(bool(row[1]))
                self.svar["email_from"].set(row[2] or "")
                self.svar["email_password"].set(row[3] or "")
                self.svar["email_to"].set(row[4] or "")
                self.sound_on.set(bool(row[5]))
                self.conf_var.set(float(row[6]) if row[6] else 0.45)
        except Exception as e:
            print(f"Load settings: {e}")

    def save_settings(self):
        try:
            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE AlertSettings SET
                    EmailEnabled=?, EmailFrom=?, EmailPassword=?,
                    EmailTo=?, SoundEnabled=?, Confidence=?,
                    UpdatedAt=GETDATE()
                WHERE SettingID=1
            """, (
                1 if self.email_on.get() else 0,
                self.svar["email_from"].get(),
                self.svar["email_password"].get(),
                self.svar["email_to"].get(),
                1 if self.sound_on.get() else 0,
                self.conf_var.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── Export ────────────────────────────────────────────────────────────────
    def build_export(self):
        page = tk.Frame(self.content, bg=BG_DARK)
        self.pages["export"] = page

        hdr = tk.Frame(page, bg=BG_PANEL, height=68)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📤  Export Reports",
                 font=("Segoe UI", 14, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack(side="left", padx=25, pady=20)

        cards = tk.Frame(page, bg=BG_DARK)
        cards.pack(fill="both", expand=True, padx=40, pady=35)

        for i, (icon, title, cmd) in enumerate([
            ("🔥", "All Detections",  self.exp_all),
            ("📅", "Today's Report",  self.exp_today),
            ("🔥", "Fire Only",       self.exp_fire),
            ("💨", "Smoke Only",      self.exp_smoke),
        ]):
            card = tk.Frame(cards, bg=BG_CARD, height=165)
            card.grid(row=i//2, column=i%2, padx=14, pady=14, sticky="nsew")
            card.pack_propagate(False)
            cards.columnconfigure(i%2, weight=1)
            tk.Label(card, text=icon, font=("Segoe UI", 34),
                     bg=BG_CARD, fg=FIRE_COLOR).pack(pady=(18, 4))
            tk.Label(card, text=title,
                     font=("Segoe UI", 11, "bold"),
                     bg=BG_CARD, fg=TEXT_WHITE).pack()
            br = tk.Frame(card, bg=BG_CARD)
            br.pack(pady=10)
            tk.Button(br, text="Excel", font=("Segoe UI", 9),
                      bg=SUCCESS, fg="#000", relief="flat",
                      cursor="hand2", padx=10,
                      command=lambda c=cmd: c("xlsx")).pack(side="left", padx=3)
            tk.Button(br, text="CSV", font=("Segoe UI", 9),
                      bg=BLUE_ACCENT, fg=TEXT_WHITE,
                      relief="flat", cursor="hand2", padx=10,
                      command=lambda c=cmd: c("csv")).pack(side="left", padx=3)

    def _save(self, fmt, name):
        ext = ".xlsx" if fmt == "xlsx" else ".csv"
        return filedialog.asksaveasfilename(
            defaultextension=ext,
            filetypes=[("Excel","*.xlsx"),("CSV","*.csv")],
            initialfile=name)

    def _write(self, path, headers, rows, fmt):
        if not path: return
        if fmt == "xlsx":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            for r in rows: ws.append(list(r))
            wb.save(path)
        else:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(rows)
        messagebox.showinfo("Exported", f"Saved:\n{path}")
        os.startfile(path)

    def _fetch(self, where=""):
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT LogID, DetectionType, Confidence, DetectedAt,
                   ISNULL(SnapshotPath,''), AlertSent
            FROM DetectionLogs {where} ORDER BY DetectedAt DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def exp_all(self, fmt):
        path = self._save(fmt, "AllDetections")
        self._write(path, ["ID","Type","Confidence","Time","Snapshot","Alert"], self._fetch(), fmt)

    def exp_today(self, fmt):
        today = datetime.now().strftime("%Y-%m-%d")
        path  = self._save(fmt, f"Today_{today}")
        self._write(path, ["ID","Type","Confidence","Time","Snapshot","Alert"],
                    self._fetch(f"WHERE CAST(DetectedAt AS DATE)='{today}'"), fmt)

    def exp_fire(self, fmt):
        path = self._save(fmt, "FireDetections")
        self._write(path, ["ID","Type","Confidence","Time","Snapshot","Alert"],
                    self._fetch("WHERE DetectionType='FIRE'"), fmt)

    def exp_smoke(self, fmt):
        path = self._save(fmt, "SmokeDetections")
        self._write(path, ["ID","Type","Confidence","Time","Snapshot","Alert"],
                    self._fetch("WHERE DetectionType='SMOKE'"), fmt)

    def open_monitor(self):
        self.root.destroy()
        import live_monitor
        live_monitor.launch()

    def logout(self):
        if messagebox.askyesno("Logout", "Return to login?"):
            self.root.destroy()
            import main_app
            main_app.launch()


def launch():
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()

if __name__ == "__main__":
    launch()