from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/")
def home():
    return "GoalGenieBot is running ✅"

@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    print("User said:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()
    msg.body("This is GoalGenieBot powered by Sip Wealth 🤖\nHow can I help you with your mutual fund goals today?")

    return str(resp)
