from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "GoalGenieBot is live!"

# Support both /webhook and /whatsapp/webhook
@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", json.dumps(data, indent=2))

    try:
        # Get user phone & message
        phone = data["contacts"][0]["wa_id"]
        user_message = data["messages"][0]["text"]["body"].strip().lower()

        # Check if message contains goal info
        if "goal" in user_message and "tenure" in user_message and "sip" in user_message:
            reply = "📊 Thanks! Your SIP goal has been received. Recommendation logic coming soon."
        else:
            reply = "👋 This is GoalGenieBot powered by Sip Wealth.\nPlease send your goal like this:\n\n" \
                    "`goal: 10000000`\n`tenure: 7`\n`sip: 60000`\n`risk: aggressive`"

        send_whatsapp_reply(phone, reply)

    except Exception as e:
        print("Error:", str(e))

    return "OK", 200

def send_whatsapp_reply(to, message):
    from twilio.rest import Client

    # Replace with your Twilio credentials
    ACCOUNT_SID = "your_account_sid"
    AUTH_TOKEN = "your_auth_token"
    FROM_WHATSAPP_NUMBER = "whatsapp:+14155238886"

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=message,
            from_=FROM_WHATSAPP_NUMBER,
            to=f"whatsapp:+{to}"
        )
        print("Reply sent successfully.")

    except Exception as e:
        print("Failed to send WhatsApp message:", str(e))
