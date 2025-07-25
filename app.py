from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ GoalGenieBot is live and secure!'

@app.route('/webhook', methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'goal' in incoming_msg and 'tenure' in incoming_msg and 'sip' in incoming_msg and 'risk' in incoming_msg:
        msg.body("This is GoalGenieBot powered by Sip Wealth 🤖\nAnalyzing your input...\n(Recommendation logic will go here)")
    else:
        msg.body("This is GoalGenieBot powered by Sip Wealth 🤖\nPlease send your goal like this:\ngoal: 10000000\ntenure: 7\nsip: 60000\nrisk: aggressive")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
