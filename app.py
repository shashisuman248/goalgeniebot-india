from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ GoalGenieBot is running with recommendations!'

def parse_input(message):
    try:
        lines = message.strip().lower().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return int(data['goal']), int(data['tenure']), int(data['sip']), data['risk']
    except:
        return None

def get_fund_recommendations(risk):
    if risk == 'aggressive':
        return [
            ('Quant Flexi Cap Fund', 'Large & Mid Cap'),
            ('Parag Parikh Flexi Cap Fund', 'Flexi Cap'),
            ('Mirae Asset Emerging Bluechip', 'Mid Cap')
        ]
    elif risk == 'moderate':
        return [
            ('HDFC Balanced Advantage', 'Balanced'),
            ('ICICI Prudential Equity & Debt', 'Aggressive Hybrid'),
            ('Axis Bluechip Fund', 'Large Cap')
        ]
    else:
        return [
            ('ICICI Prudential Liquid Fund', 'Liquid'),
            ('HDFC Short Term Debt Fund', 'Debt'),
            ('SBI Equity Savings Fund', 'Equity Savings')
        ]

@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').lower()
    print("📩 Incoming message:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    parsed = parse_input(incoming_msg)
    print("🔍 Parsed result:", parsed)

    if parsed:
        goal, tenure, sip, risk = parsed
        print(f"✅ Parsed values: goal={goal}, tenure={tenure}, sip={sip}, risk={risk}")
        recommendations = get_fund_recommendations(risk)

        funds_text = "\n".join([f"• {name} ({category})" for name, category in recommendations])
        msg.body(
            f"✅ Your Goal: ₹{goal}\n"
            f"📅 Tenure: {tenure} years\n"
            f"💸 SIP: ₹{sip}/month\n"
            f"📈 Risk: {risk.capitalize()}\n\n"
            f"📊 Recommended Funds:\n{funds_text}"
        )
    else:
        msg.body(
            "👋 This is GoalGenieBot powered by Sip Wealth 🤖\n\n"
            "Please enter your goal like this:\n\n"
            "*goal: 10000000*\n*tenure: 7*\n*sip: 60000*\n*risk: aggressive*"
        )

    return str(resp)
