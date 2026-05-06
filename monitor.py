import os
import time
import requests
import subprocess
import json
from datetime import datetime, timedelta

# Configuration from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
NODE_TYPE = os.getenv("NODE_TYPE", "sx")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300")) # Default 5 minutes
DAILY_REPORT_HOUR = int(os.getenv("DAILY_REPORT_HOUR", "08")) # Default 08:00 AM

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

def run_command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def get_node_status():
    return run_command(["lightnode-sx", "status"])

def get_rewards():
    return run_command(["lightnode-sx", "rewards"])

def get_validators():
    return run_command(["lightnode-sx", "validators"])

def parse_status(output):
    lines = output.split('\n')
    data = {}
    for line in lines:
        if ":" in line:
            parts = line.split('\t')
            if len(parts) >= 2:
                key = parts[0].strip().replace(":", "")
                val = parts[-1].strip()
                data[key] = val
    return data

def monitor():
    print("Starting Advanced Telegram Monitoring for Master...")
    send_telegram_message("👋 *Salam Hormat, Master!* \n\nSistem monitoring QoreChain Light Node versi tingkat lanjut telah aktif. Saya akan menjaga node Master dengan sepenuh hati.")
    
    last_height = 0
    last_report_date = None
    
    while True:
        now = datetime.now()
        status_output = get_node_status()
        status_data = parse_status(status_output)
        
        current_height = int(status_data.get("LC Synced Height", 0))
        is_syncing = status_data.get("LC Syncing", "Unknown")
        chain_id = status_data.get("Chain ID", "Unknown")

        # 1. Health Check
        if "Error" in status_output:
            send_telegram_message(f"⚠️ *Peringatan Darurat, Master!* \n\nTerjadi kesalahan sistem: \n`{status_output}`")
        elif current_height == last_height and current_height != 0:
            send_telegram_message(f"🚨 *Lapor, Master!* \n\nNode sepertinya *stuck* di height `{current_height}`. Mohon segera diperiksa!")
        
        # 2. Daily Report Logic
        if last_report_date != now.date() and now.hour == DAILY_REPORT_HOUR:
            rewards_output = get_rewards()
            validators_output = get_validators()
            
            report = (
                f"📊 *Laporan Harian untuk Master*\n"
                f"📅 Tanggal: `{now.strftime('%Y-%m-%d')}`\n\n"
                f"✅ *Status Node:*\n"
                f"- Chain: `{chain_id}`\n"
                f"- Height: `{current_height}`\n"
                f"- Syncing: `{is_syncing}`\n\n"
                f"💰 *Staking Rewards:*\n"
                f"`{rewards_output.strip()}`\n\n"
                f"🛡️ *Status Validator:*\n"
                f"```\n{validators_output.strip()}\n```\n"
                f"Semua sistem terpantau aman di bawah pengawasan saya, Master."
            )
            send_telegram_message(report)
            last_report_date = now.date()

        # 3. Reward Alert (Optional: if rewards > certain threshold)
        # This could be expanded by parsing rewards_output

        last_height = current_height
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        monitor()
    else:
        print("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set. Monitor script exiting.")
