import tkinter as tk

BG_DARK    = "#0A1628"
BG_PANEL   = "#0F2044"
BG_CARD    = "#162950"
FIRE_COLOR = "#FF4C00"
BLUE_LIGHT = "#4A9FFF"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#8BA3C7"
DANGER     = "#FF4C4C"

ADMIN_PASSWORD = "admin123"


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Fire Detection System — Login")
        self.root.geometry("460x540")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)
        self.center_window(460, 540)
        self.build_ui()

    def center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def build_ui(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=165)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🔥", font=("Segoe UI", 44),
                 bg=BG_PANEL, fg=FIRE_COLOR).pack(pady=(18, 4))
        tk.Label(hdr, text="FIRE DETECTION SYSTEM",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG_PANEL, fg=TEXT_WHITE).pack()
        tk.Label(hdr, text="AI-Powered Real-Time Monitoring",
                 font=("Segoe UI", 9),
                 bg=BG_PANEL, fg=TEXT_GRAY).pack()

        tk.Frame(self.root, bg=FIRE_COLOR, height=2).pack(fill="x")

        form = tk.Frame(self.root, bg=BG_DARK, padx=50)
        form.pack(fill="both", expand=True, pady=25)

        tk.Label(form, text="SELECT LOGIN TYPE",
                 font=("Segoe UI", 9, "bold"),
                 bg=BG_DARK, fg=TEXT_GRAY).pack(anchor="w", pady=(0, 12))

        self.role_var = tk.StringVar(value="admin")
        for role, label, icon in [
            ("admin",   "Administrator",  "⚙️"),
            ("monitor", "Live Monitor",   "📷"),
        ]:
            rf = tk.Frame(form, bg=BG_CARD, cursor="hand2")
            rf.pack(fill="x", pady=4, ipady=10, ipadx=10)
            tk.Label(rf, text=icon, font=("Segoe UI", 18),
                     bg=BG_CARD, fg=FIRE_COLOR).pack(side="left", padx=(15, 10))
            tk.Label(rf, text=label, font=("Segoe UI", 11, "bold"),
                     bg=BG_CARD, fg=TEXT_WHITE).pack(side="left")
            tk.Radiobutton(rf, variable=self.role_var, value=role,
                           bg=BG_CARD, fg=BLUE_LIGHT, selectcolor=BG_DARK,
                           activebackground=BG_CARD,
                           cursor="hand2").pack(side="right", padx=15)

        tk.Label(form, text="PASSWORD",
                 font=("Segoe UI", 9, "bold"),
                 bg=BG_DARK, fg=TEXT_GRAY).pack(anchor="w", pady=(18, 5))

        pw_frame = tk.Frame(form, bg=BG_CARD)
        pw_frame.pack(fill="x")
        tk.Label(pw_frame, text="🔒", bg=BG_CARD, fg=TEXT_GRAY,
                 font=("Segoe UI", 12)).pack(side="left", padx=10)
        self.pw = tk.Entry(pw_frame, show="●", bg=BG_CARD, fg=TEXT_WHITE,
                            insertbackground=TEXT_WHITE, relief="flat",
                            font=("Segoe UI", 12), bd=0)
        self.pw.pack(side="left", fill="x", expand=True, ipady=10)
        self.pw.bind("<Return>", lambda e: self.login())

        tk.Button(form, text="ENTER SYSTEM",
                  font=("Segoe UI", 11, "bold"),
                  bg=FIRE_COLOR, fg=TEXT_WHITE, relief="flat",
                  cursor="hand2", activebackground="#CC3A00",
                  command=self.login).pack(fill="x", pady=(18, 0), ipady=12)

        self.status = tk.Label(form, text="",
                                font=("Segoe UI", 9),
                                bg=BG_DARK, fg=DANGER)
        self.status.pack(pady=5)

        tk.Label(self.root,
                 text="© 2025 Fire Detection System  |  All Rights Reserved",
                 font=("Segoe UI", 8), bg=BG_DARK,
                 fg=TEXT_GRAY).pack(pady=8)

    def login(self):
        if self.pw.get() != ADMIN_PASSWORD:
            self.status.config(text="❌ Incorrect password.")
            return
        self.root.destroy()
        if self.role_var.get() == "admin":
            import dashboard
            dashboard.launch()
        else:
            import live_monitor
            live_monitor.launch()


def launch():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    launch()