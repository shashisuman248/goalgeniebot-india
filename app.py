from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ GoalGenieBot is running with recommendations!'

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

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

def generate_pdf(goal, tenure, sip, risk, funds):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "📊 Mutual Fund Goal Report")
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Goal Amount: ₹{goal}")
    p.drawString(50, 700, f"Tenure: {tenure} years")
    p.drawString(50, 680, f"Monthly SIP: ₹{sip}")
    p.drawString(50, 660, f"Risk Appetite: {risk.capitalize()}")
    p.drawString(50, 630, "Recommended Funds:")

    y = 610
    for name, category in funds:
        p.drawString(60, y, f"• {name} ({category})")
        y -= 20

    p.save()
    buffer.seek(0)
    return buffer

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
            "*goal: 10000000*\n*tenure: 7*\n*sip: 60000*\n*risk: aggressive*"
        )

    return str(resp)
