from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Store user sessions in memory (for demo only, not scalable)
user_sessions = {}

@app.route('/whatsapp', methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender = request.values.get('From', '')

    resp = MessagingResponse()
    msg = resp.message()

    # Get user state
    session = user_sessions.get(sender, {'step': 0})

    if session['step'] == 0:
        msg.body("🙏 Namaste! Yeh GoalGenieBot powered by Sip Wealth hai.\nAapka investment goal kya hai?\n(Example: Bacche ki padhai, Ghar, Retirement)")
        session['step'] = 1

    elif session['step'] == 1:
        session['goal'] = incoming_msg
        msg.body("👍 Achha! Ab bataye aap har mahine kitni SIP karna chahte hain? (₹ mein)")
        session['step'] = 2

    elif session['step'] == 2:
        session['sip'] = incoming_msg
        msg.body("Kitne saal ke liye invest karna chahte hain?")
        session['step'] = 3

    elif session['step'] == 3:
        session['tenure'] = incoming_msg
        msg.body("Aapka risk profile kya hai? (Low / Medium / High)")
        session['step'] = 4

    elif session['step'] == 4:
        session['risk'] = incoming_msg
        # Yahan recommendation logic lagayenge baad mein
        response_text = (
            f"✅ Aapka Goal: {session['goal'].title()}\n"
            f"SIP: ₹{session['sip']}/month for {session['tenure']} years\n"
            f"Risk Profile: {session['risk'].title()}\n\n"
            f"📊 Mutual Fund Recommendation (demo):\n👉 *Axis Growth Opportunities Fund*\n\n"
            f"Detailed PDF report jaldi hi bheji jaayegi. Dhanyavaad!"
        )
        msg.body(response_text)
        session['step'] = 0  # Reset for next interaction

    user_sessions[sender] = session
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
