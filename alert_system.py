import smtplib
import threading
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime


def play_alert_sound():
    def _play():
        try:
            import winsound
            for _ in range(5):
                winsound.Beep(1200, 400)
        except Exception as e:
            print(f"[SOUND] {e}")
    threading.Thread(target=_play, daemon=True).start()


def send_email_alert(settings, detection_type, confidence, snapshot_path=None):
    def _send():
        try:
            msg            = MIMEMultipart()
            msg["From"]    = settings["email_from"]
            msg["To"]      = settings["email_to"]
            msg["Subject"] = f"🔥 FIRE ALERT — {detection_type} Detected!"

            body = f"""
⚠️  FIRE DETECTION SYSTEM ALERT  ⚠️

Detection  : {detection_type}
Confidence : {confidence:.1%}
Time       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please take immediate action!

— Fire Detection System
            """
            msg.attach(MIMEText(body, "plain"))

            if snapshot_path and os.path.exists(snapshot_path):
                with open(snapshot_path, "rb") as f:
                    img = MIMEImage(f.read())
                    img.add_header("Content-Disposition", "attachment",
                                   filename="snapshot.jpg")
                    msg.attach(img)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings["email_from"], settings["email_password"])
                server.send_message(msg)
            print(f"[EMAIL] Alert sent to {settings['email_to']}")

        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    threading.Thread(target=_send, daemon=True).start()


def trigger_alert(settings, detection_type, confidence, snapshot_path=None):
    if settings.get("sound_enabled"):
        play_alert_sound()
    if settings.get("email_enabled") and settings.get("email_from"):
        send_email_alert(settings, detection_type, confidence, snapshot_path)