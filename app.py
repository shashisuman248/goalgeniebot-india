from flask import Flask, request
import json
import os
from twilio.rest import Client

app = Flask(__name__)

@app.route('/')
def index():
    return "✅ GoalGenieBot is live and secure!"

# Webhook for Twilio Sandbox (both routes supported)
@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 Received data:", json.dumps(data, indent=2))

    try:
        # Extract phone and message
        phone = data["contacts"][0]["wa_id"]
        user_message = data["messages"][0]["text"]["body"].strip().lower()

        # Basic pattern recognition
        if "goal" in user_message and "tenure" in user_message and "sip" in user_message:
            reply = "📊 Got it! Your SIP goal has been received. Fund recommendations coming soon!"
        else:
            reply = (
                "👋 This is GoalGenieBot powered by Sip Wealth.\n"
                "Send your goal like this:\n\n"
                "`goal: 10000000`\n"
                "`tenure: 7`\n"
                "`sip: 60000`\n"
                "`risk: aggressive`"
            )

        send_whatsapp_reply(phone, reply)

    except Exception as e:
        print("❌ Error processing message:", str(e))

    return "OK", 200

def send_whatsapp_reply(to, message):
    # Load credentials from Render env variables
    ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=message,
            from_=FROM_WHATSAPP_NUMBER,
            to=f"whatsapp:+{to}"
        )
        print("✅ WhatsApp reply sent.")
    except Exception as e:
        print("❌ Failed to send message:", str(e))
