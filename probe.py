#!/usr/bin/env python3

import requests
import time
import json
import sqlite3
from datetime import datetime

SERVICES = {
    "DBU_EMS": {
        "url": "https://ems.deshbhagatuniversity.in",
        "category": "Education",
        "timeout": 10,
        "check_interval": 60
    },
    "DBU_ERP": {
        "url": "https://erp.deshbhagatuniversity.in",
        "category": "Education",
        "timeout": 10,
        "check_interval": 60
    },
    "DBU_Main": {
        "url": "https://deshbhagatuniversity.in",
        "category": "Education",
        "timeout": 10,
        "check_interval": 60
    },
    "Bank_of_Baroda": {
        "url": "https://www.bankofbaroda.in",
        "category": "Banking",
        "timeout": 10,
        "check_interval": 60
    },
    "SBI_Online": {
        "url": "https://www.onlinesbi.sbi",
        "category": "Banking",
        "timeout": 10,
        "check_interval": 60
    },
    "NPCI_UPI": {
        "url": "https://www.npci.org.in",
        "category": "Finance",
        "timeout": 10,
        "check_interval": 60
    },
    "UIDAI_Aadhaar": {
        "url": "https://uidai.gov.in",
        "category": "Government",
        "timeout": 10,
        "check_interval": 60
    },
    "DigiLocker": {
        "url": "https://www.digilocker.gov.in",
        "category": "Government",
        "timeout": 10,
        "check_interval": 60
    },
    "Income_Tax": {
        "url": "https://www.incometax.gov.in",
        "category": "Tax",
        "timeout": 10,
        "check_interval": 60
    },
    "GST_Portal": {
        "url": "https://www.gst.gov.in",
        "category": "Tax",
        "timeout": 10,
        "check_interval": 60
    },
    "EPFO": {
        "url": "https://www.epfindia.gov.in",
        "category": "Labour",
        "timeout": 10,
        "check_interval": 60
    },
    "IRCTC": {
        "url": "https://www.irctc.co.in",
        "category": "Railway",
        "timeout": 10,
        "check_interval": 60
    },
    "Passport_Seva": {
        "url": "https://www.passportindia.gov.in",
        "category": "Public_Service",
        "timeout": 10,
        "check_interval": 60
    },
    "Parivahan": {
        "url": "https://parivahan.gov.in",
        "category": "Transport",
        "timeout": 10,
        "check_interval": 60
    },
    "CoWIN": {
        "url": "https://www.cowin.gov.in",
        "category": "Healthcare",
        "timeout": 10,
        "check_interval": 60
    },
    "NTA": {
        "url": "https://nta.ac.in",
        "category": "Education_Govt",
        "timeout": 10,
        "check_interval": 60
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def setup_database():
    conn = sqlite3.connect("bharat_pulse.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            url TEXT NOT NULL,
            status TEXT NOT NULL,
            status_code INTEGER,
            response_time_ms REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        )
    """)
    conn.commit()
    return conn

def check_service(name, config):
    result = {
        "service": name,
        "url": config["url"],
        "timestamp": datetime.now().isoformat(),
        "status": "DOWN",
        "status_code": None,
        "response_time_ms": None,
        "error": None
    }

    try:
        start_time = time.time()
        response = requests.get(
            config["url"],
            headers=HEADERS,
            timeout=config["timeout"],
            allow_redirects=True
        )
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        result["status_code"] = response.status_code
        result["response_time_ms"] = elapsed_ms

        if response.status_code == 200:
            if elapsed_ms > 5000:
                result["status"] = "SLOW"
            else:
                result["status"] = "UP"
        elif response.status_code in [301, 302]:
            result["status"] = "UP"
        else:
            result["status"] = "DOWN"

    except requests.exceptions.Timeout:
        result["error"] = "Connection timeout"
        result["status"] = "DOWN"

    except requests.exceptions.ConnectionError:
        result["error"] = "Connection failed"
        result["status"] = "DOWN"

    except Exception as e:
        result["error"] = str(e)
        result["status"] = "DOWN"

    return result

def save_to_db(conn, result):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checks 
        (service_name, url, status, status_code, response_time_ms, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        result["service"],
        result["url"],
        result["status"],
        result["status_code"],
        result["response_time_ms"],
        result["error"]
    ))
    conn.commit()

def print_result(result):
    status_emoji = {
        "UP": "✅",
        "DOWN": "❌",
        "SLOW": "🐌"
    }
    emoji = status_emoji.get(result["status"], "❓")

    if result["response_time_ms"]:
        print(f"{emoji} {result['service']}: {result['status']} "
              f"({result['response_time_ms']}ms) "
              f"[HTTP {result['status_code']}]")
    else:
        print(f"{emoji} {result['service']}: {result['status']} "
              f"- {result['error']}")

def run_all_checks():
    print(f"\n{'='*50}")
    print(f"🇮🇳 BHARAT PULSE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    conn = setup_database()
    results = []

    for name, config in SERVICES.items():
        result = check_service(name, config)
        save_to_db(conn, result)
        print_result(result)
        results.append(result)
        time.sleep(1)

    up = sum(1 for r in results if r["status"] == "UP")
    down = sum(1 for r in results if r["status"] == "DOWN")
    slow = sum(1 for r in results if r["status"] == "SLOW")

    print(f"\n📊 Summary: {up} UP | {down} DOWN | {slow} SLOW")
    print(f"{'='*50}\n")

    conn.close()
    return results

if __name__ == "__main__":
    print("🚀 Bharat Pulse Starting...")
    print("Press Ctrl+C to stop\n")

    while True:
        try:
            run_all_checks()
            print("⏳ Next check in 60 seconds...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Bharat Pulse stopped.")
            break