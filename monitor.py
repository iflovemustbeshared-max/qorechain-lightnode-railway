import os
import time
import requests
import subprocess
import json

# Configuration from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NODE_TYPE = os.getenv("NODE_TYPE", "sx")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300")) # Default 5 minutes

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram configuration missing. Skipping notification.")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def get_node_status():
    try:
        # Run lightnode-sx status and capture output
        result = subprocess.run(["lightnode-sx", "status"], capture_mode=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def monitor():
    print("Starting Telegram Monitoring for Master...")
    send_telegram_message("👋 *Salam, Master!* \n\nSistem monitoring QoreChain Light Node telah aktif dan siap melayani Anda.")
    
    last_height = 0
    
    while True:
        status_output = get_node_status()
        
        # Simple parsing of the status output
        # Expected format from main.go:
        # Chain ID: ...
        # Latest Height: ...
        # LC Synced Height: ...
        
        lines = status_output.split('\n')
        current_height = 0
        is_syncing = "Unknown"
        
        for line in lines:
            if "LC Synced Height:" in line:
                try:
                    current_height = int(line.split('\t')[-1].strip())
                except:
                    pass
            if "LC Syncing:" in line:
                is_syncing = line.split('\t')[-1].strip()

        if "Error" in status_output:
            send_telegram_message(f"⚠️ *Peringatan, Master!* \n\nTerjadi kesalahan saat mengambil status node: \n`{status_output}`")
        elif current_height == last_height and current_height != 0:
            send_telegram_message(f"🚨 *Lapor, Master!* \n\nNode sepertinya berhenti sinkronisasi pada ketinggian (height) `{current_height}`. Mohon periksa koneksi atau log sistem.")
        else:
            print(f"Node healthy at height {current_height}")
            # Optional: send periodic heartbeat to Master
            # send_telegram_message(f"✅ *Update untuk Master* \n\nNode berjalan normal.\nHeight: `{current_height}`\nSyncing: `{is_syncing}`")

        last_height = current_height
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        monitor()
    else:
        print("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set. Monitor script exiting.")
