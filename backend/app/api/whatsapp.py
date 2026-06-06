from fastapi import APIRouter, Request, Form
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import pandas as pd
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# In-memory store shared with routes.py
community_reports = []

@router.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
):
    """Receive WhatsApp messages and save as community reports."""
    
    response = MessagingResponse()
    message_body = Body.strip()
    phone = From.replace("whatsapp:", "")
    
    # Try to parse bin ID from message
    # Expected format: BIN001 message text
    # or just: overflow at molyko market
    words = message_body.upper().split()
    bin_id = "BIN001"  # default
    
    for word in words:
        if word.startswith("BIN") and len(word) == 6:
            bin_id = word
            break
    
    # Estimate fill level from keywords
    fill_level = 80.0  # default
    lower_body = message_body.lower()
    if any(w in lower_body for w in ["overflow", "overflowing", "full", "completely"]):
        fill_level = 95.0
    elif any(w in lower_body for w in ["almost", "nearly", "almost full"]):
        fill_level = 75.0
    elif any(w in lower_body for w in ["half", "halfway"]):
        fill_level = 50.0

    # Save report
    report_entry = {
        "report_id"  : f"WA{len(community_reports)+1:04d}",
        "bin_id"     : bin_id,
        "reporter"   : "WhatsApp User",
        "phone"      : phone,
        "message"    : message_body,
        "fill_level" : fill_level,
        "timestamp"  : datetime.now().isoformat(),
        "status"     : "received",
        "channel"    : "whatsapp"
    }
    community_reports.append(report_entry)

    # Save to CSV
    try:
        reports_df = pd.DataFrame(community_reports)
        reports_df.to_csv(
            os.path.join(BASE_DIR, "data/processed/community_reports.csv"),
            index=False
        )
    except Exception as e:
        print(f"CSV save error: {e}")

    # Reply to the user
    reply = (
        f"✅ Thank you for your report!\n\n"
        f"📍 Bin: {bin_id}\n"
        f"📊 Fill level recorded: {fill_level}%\n"
        f"🕐 Received: {datetime.now().strftime('%H:%M')}\n\n"
        f"Our team has been notified. Thank you for keeping Buea clean! 🌿"
    )
    response.message(reply)
    return response.to_xml()