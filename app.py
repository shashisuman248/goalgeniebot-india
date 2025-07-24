from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import re
import os

app = Flask(__name__)

def parse_input(message):
    pattern = r'goal[:\s]+([\d,\.]+).*?tenure[:\s]+(\d+).*?sip[:\s]+([\d,\.]+).*?risk[:\s]+(\w+)'
    match = re.search(pattern, message, re.IGNORECASE | re.DOTALL)
    if match:
        goal = match.group(1).replace(",", "")
        tenure = match.group(2)
        sip = match.group(3).replace(",", "")
        risk = match.group(4)
        return float(goal), int(tenure), float(sip), risk.lower()
    return None

def get_fund_recommendations(risk_profile):
    funds = {
        "aggressive": [
            {"name": "Axis Midcap Fund", "category": "Mid Cap", "return": "18.2%", "risk": "High"},
            {"name": "Quant Small Cap Fund", "category": "Small Cap", "return": "21.6%", "risk": "High"},
            {"name": "Mirae Asset Emerging Bluechip", "category": "Large & Mid Cap", "return": "19.4%", "risk": "High"}
        ],
        "moderate": [
            {"name": "Parag Parikh Flexi Cap", "category": "Flexi Cap", "return": "14.8%", "risk": "Moderate"},
            {"name": "UTI Flexi Cap Fund", "category": "Flexi Cap", "return": "15.1%", "risk": "Moderate"}
        ]
    }
    return funds.get(risk_profile, funds["moderate"])

def generate_pdf(goal, tenure, sip, risk, fund_data):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)
    p.drawString(50, 750, "📄 GoalGenieBot Portfolio Report")
    p.drawString(50, 730, f"🎯 Goal Amount: ₹{goal:,.2f}")
    p.drawString(50, 715, f"⏳ Tenure: {tenure} years")
    p.drawString(50, 700, f"💰 Monthly SIP: ₹{sip:,.2f}")
    p.drawString(50, 685, f"📉 Risk Profile: {risk.capitalize()}")
    p.drawString(50, 660, "📊 Recommended Mutual Funds:")
    
    y = 640
    for fund in fund_data:
        p.drawString(60, y, f"{fund['name']} - {fund['category']} | {fund['return']} | Risk: {fund['risk']}")
        y -= 20

    p.drawString(50, y - 20, "🤖 Report by GoalGenieBot powered by Sip Wealth")
    p.save()
    buffer.seek(0)
    return buffer

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    parsed = parse_input(incoming_msg)
    if parsed:
        goal, tenure, sip, risk = parsed
        recommendations = get_fund_recommendations(risk)
        pdf_buffer = generate_pdf(goal, tenure, sip, risk, recommendations)

        os.makedirs("static", exist_ok=True)
        with open("static/goal_report.pdf", "wb") as f:
            f.write(pdf_buffer.read())

        msg.body("✅ Here’s your mutual fund recommendation PDF:")
        msg.media("https://goalgeniebot-india-1.onrender.com/static/goal_report.pdf")
    else:
        msg.body(
            "👋 This is GoalGenieBot powered by Sip Wealth 🤖\n\n"
            "Please enter your goal like this:\n\n"
            "*goal: 1 crore*\n*tenure: 7 years*\n*sip: 60000*\n*risk: aggressive*"
        )

    return str(resp)

@app.route("/")
def home():
    return "✅ GoalGenieBot is running with recommendations!"

if __name__ == "__main__":
    app.run(debug=True)
