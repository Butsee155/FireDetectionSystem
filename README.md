# 🔥 Fire Detection System

> An AI-powered real-time fire and smoke detection system built with Python, OpenCV, and SQL Server — with instant email alerts and a professional desktop dashboard.

## 📌 Overview

The **Fire Detection System** is a real-time desktop application that uses computer vision and color-based AI analysis to detect fire and smoke through a webcam. When a threat is detected, the system instantly triggers sound alerts, sends email notifications with a snapshot attached, and logs every event to a SQL Server database.

---

## ✨ Features

- 🔥 **Real-Time Fire Detection** — HSV color analysis detects fire regions instantly
- 💨 **Smoke Detection** — Frame blur analysis identifies smoke presence
- 📸 **Auto Snapshot** — Saves a photo of every detection automatically
- 📧 **Email Alerts** — Sends alert email with snapshot attached via Gmail
- 🔔 **Sound Alerts** — Audible beep on fire/smoke detection
- 📊 **Admin Dashboard** — Overview stats, detection logs, settings, export
- 📋 **Detection Logs** — Full history of every detection with timestamp
- 📤 **Export Reports** — Export logs to Excel (.xlsx) or CSV
- ⚙️ **Configurable Settings** — Adjust sensitivity, email, sound via dashboard

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Fire Detection | OpenCV HSV Color Analysis + Blur Detection |
| GUI Framework | Tkinter (Corporate Blue theme) |
| Database | Microsoft SQL Server 2019 + SSMS 20 |
| DB Connector | pyodbc |
| Image Processing | OpenCV, Pillow, NumPy |
| Email Alerts | smtplib (Gmail SMTP SSL) |
| Sound Alerts | winsound (Windows built-in) |
| Export | openpyxl, csv |

---

## 📁 Project Structure

```
FireDetectionSystem/
│
├── main_app.py           # Login screen & launcher
├── dashboard.py          # Admin dashboard (logs, settings, export)
├── live_monitor.py       # Real-time camera feed & detection
├── detection_engine.py   # Fire & smoke detection logic
├── alert_system.py       # Email & sound alert system
├── db_config.py          # SQL Server database connection
├── snapshots/            # Auto-saved detection snapshots
└── README.md
```

---

## 🗄️ Database Schema

```sql
CREATE DATABASE FireDetectionSystem;

-- Detection logs
CREATE TABLE DetectionLogs (
    LogID          INT IDENTITY(1,1) PRIMARY KEY,
    DetectionType  VARCHAR(50)  NOT NULL,   -- 'FIRE' or 'SMOKE'
    Confidence     FLOAT        NOT NULL,
    DetectedAt     DATETIME     DEFAULT GETDATE(),
    SnapshotPath   VARCHAR(500) DEFAULT '',
    AlertSent      BIT          DEFAULT 0
);

-- Alert & system settings
CREATE TABLE AlertSettings (
    SettingID     INT IDENTITY(1,1) PRIMARY KEY,
    EmailEnabled  BIT          DEFAULT 0,
    EmailFrom     VARCHAR(200) DEFAULT '',
    EmailPassword VARCHAR(200) DEFAULT '',
    EmailTo       VARCHAR(200) DEFAULT '',
    SoundEnabled  BIT          DEFAULT 1,
    Confidence    FLOAT        DEFAULT 0.45,
    UpdatedAt     DATETIME     DEFAULT GETDATE()
);

INSERT INTO AlertSettings (EmailEnabled, SoundEnabled, Confidence)
VALUES (0, 1, 0.45);
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10 — [python.org](https://python.org)
- SQL Server 2019 Express — [Microsoft](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)
- SSMS 20 — [Microsoft](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms)
- ODBC Driver 17 for SQL Server — [Microsoft](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### 2. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/FireDetectionSystem.git
cd FireDetectionSystem
```

### 3. Install Dependencies
```bash
py -3.10 -m pip install opencv-python numpy pyodbc pillow openpyxl
```

### 4. Set Up Database
Run the SQL script in SSMS to create the database and tables (see Database Schema above).

### 5. Configure DB Connection
Edit `db_config.py`:
```python
def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=FireDetectionSystem;'
        'Trusted_Connection=yes;'
    )
    return conn
```

### 6. Run the Application
```bash
py -3.10 main_app.py
```

> Default admin password: `admin123`
> Change it in `main_app.py` → `ADMIN_PASSWORD = "your_password"`

---

## 🚀 How It Works

1. **Live Monitor opens** — webcam starts automatically (no manual setup)
2. **Every frame is analyzed** using HSV color analysis for fire and blur analysis for smoke
3. **If fire/smoke detected** — system triggers sound alert + email + saves snapshot
4. **All detections logged** to SQL Server with timestamp and confidence score
5. **Admin dashboard** shows full history, stats, and export options

---

## 🔍 Detection Methods

### Fire Detection (HSV Color Analysis)
- Converts frame to HSV color space
- Detects orange, red, and yellow pixel clusters associated with fire
- Filters by contour area to eliminate false positives
- Confidence score based on detected region size

### Smoke Detection (Blur Analysis)
- Applies Gaussian blur and measures pixel difference
- High difference ratio indicates smoke/haze presence
- Threshold-based confidence scoring

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|---|---|
| `dlib` and `face_recognition` failed on Windows | Used OpenCV color analysis — no compilation needed |
| Camera backend errors with `CAP_DSHOW` | Used `cv2.VideoCapture(0)` directly — auto-detects |
| False positives from bright lights | Added minimum contour area filter + confidence threshold |
| SQL foreign key constraint errors on reset | Rebuilt database from scratch with clean schema |
| Email alerts blocking the UI | Used Python `threading` for non-blocking email sending |

---

## 📧 Gmail Email Alert Setup

1. Go to **myaccount.google.com**
2. Security → **2-Step Verification** → Turn ON
3. Search **"App Passwords"** → Generate one for "Mail"
4. Copy the 16-character password
5. Paste into **Settings** page in the dashboard

---

## 🔮 Future Improvements

- [ ] YOLOv8 AI model integration for higher accuracy
- [ ] SMS alerts via Twilio
- [ ] Multiple camera support
- [ ] Web-based dashboard using Flask
- [ ] Mobile push notifications
- [ ] Automatic fire department notification

---

## 👤 Author

**R.M. Nisitha Nethsilu**
🔗 [LinkedIn] - www.linkedin.com/in/nisithanethsilu/
🐙 [GitHub] - www.github.com/Butsee155

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> ⭐ If you found this project useful, please give it a star on GitHub!
