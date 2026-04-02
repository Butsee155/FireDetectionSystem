from db_config import get_connection

try:
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM DetectionLogs")
    print(f"DetectionLogs rows : {cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM AlertSettings")
    print(f"AlertSettings rows : {cursor.fetchone()[0]}")

    cursor.execute("SELECT * FROM AlertSettings")
    row = cursor.fetchone()
    print(f"Default settings   : {row}")

    conn.close()
    print("\n[SUCCESS] Database connection working perfectly!")

except Exception as e:
    print(f"[ERROR] {e}")