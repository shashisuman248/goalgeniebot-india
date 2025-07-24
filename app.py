from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import math

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ GoalGenieBot v2 is live with smart recommendations!'

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

def future_value(sip, r, n):
    return sip * (((1 + r) ** n - 1) / r) * (1 + r)

def categorize_tenure(years):
    if years < 3:
        return 'short'
    elif years <= 5:
        return 'medium'
    else:
        return 'long'

def get_fund_mix(risk, tenure_category):
    mix = []

    if tenure_category == 'short':
        mix = [
            ('ICICI Liquid Fund', '40%'),
            ('HDFC Ultra Short Term Fund', '40%'),
            ('SBI Arbitrage Fund', '20%')
        ]
    elif tenure_category == 'medium':
        if risk == 'aggressive':
            mix = [
                ('Axis Balanced Advantage Fund', '40%'),
                ('Kotak MultiCap Fund', '30%'),
                ('Mirae Asset Large Cap Fund', '30%')
            ]
        else:
            mix = [
                ('HDFC Hybrid Equity Fund', '40%'),
                ('Kotak MultiCap Fund', '30%'),
                ('ICICI Bluechip Fund', '30%')
            ]
    elif tenure_category == 'long':
        if risk == 'aggressive':
            mix = [
                ('Parag Parikh Flexi Cap Fund', '40%'),
                ('Quant Mid Cap Fund', '30%'),
                ('Nippon Small Cap Fund', '30%')
            ]
        elif risk == 'moderate':
            mix = [
                ('SBI Large & Mid Cap Fund', '40%'),
                ('ICICI Balanced Advantage Fund', '30%'),
                ('Axis Midcap Fund', '30%')
            ]
        else:
            mix = [
                ('HDFC Balanced Advantage Fund', '40%'),
                ('ICICI Equity Savings Fund', '30%'),
                ('SBI Hybrid Debt Fund', '30%')
            ]
    
    return mix

@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').lower()
    print("📩 Incoming message:", incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    parsed = parse_input(incoming_msg)
    print("🔍 Parsed input:", parsed)

    if parsed:
        goal, tenure, sip, risk = parsed
        tenure_cat = categorize_tenure(tenure)
        print(f"🎯 Goal: ₹{goal}, Tenure: {tenure_cat}, SIP: ₹{sip}, Risk: {risk}")

        # Monthly rate based on risk
        rate_map = {'aggressive': 0.012, 'moderate': 0.009, 'conservative': 0.006}
        r = rate_map.get(risk, 0.009)
        months = tenure * 12
        fv = round(future_value(sip, r, months))
        feasible = "Achievable ✅" if fv >= goal else f"Not Achievable ❌ (est. ₹{fv})"

        # Fund suggestions
        funds = get_fund_mix(risk, tenure_cat)
        fund_lines = '\n'.join([f"• {name} ({alloc})" for name, alloc in funds])

        msg.body(
            f"🎯 Goal: ₹{goal:,} in {tenure} years\n"
            f"💸 SIP: ₹{sip:,}/month\n"
            f"📈 Risk: {risk.capitalize()}\n"
            f"🧮 Feasibility: {feasible}\n\n"
            f"📊 Recommended Fund Allocation:\n{fund_lines}\n\n"
            f"🔁 Tip: Review this yearly and consider SIP top-up."
        )
    else:
        msg.body(
            "👋 This is GoalGenieBot powered by Sip Wealth 🤖\n\n"
            "Send your goal like this:\n\n"
            "*goal: 10000000*\n*tenure: 7*\n*sip: 60000*\n*risk: aggressive*"
        )

    return str(resp)
