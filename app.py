from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the recommendation matrix
matrix_path = 'data/recommendation_matrix.xlsx'
df = pd.read_excel(matrix_path)

# Clean up column names for safety
df.columns = [col.strip().lower() for col in df.columns]

def match_fund(sip, tenure, risk):
    # Filter by risk profile
    filtered = df[df['risk'].str.lower() == risk.lower()]
    if filtered.empty:
        return None, "No match found for this risk profile."

    # Try to match based on tenure and SIP ranges
    matched = filtered[
        (filtered['min_sip'] <= sip) &
        (filtered['max_sip'] >= sip) &
        (filtered['min_tenure'] <= tenure) &
        (filtered['max_tenure'] >= tenure)
    ]

    if matched.empty:
        return None, "No exact match found for your SIP and tenure range."

    best_match = matched.iloc[0]
    return best_match, None

@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    # your code here

def webhook():
    if request.method == "GET":
        return "GoalGenieBot is live!"

    incoming_msg = request.json.get("Body", "").lower()
    sender = request.json.get("From", "")

    # Check if input format is correct
    try:
        lines = incoming_msg.strip().split("\n")
        user_data = {}
        for line in lines:
            if "goal" in line:
                user_data["goal"] = int(line.split()[-1].replace("₹", "").replace(",", ""))
            elif "tenure" in line:
                user_data["tenure"] = int(line.split()[0])
            elif "sip" in line:
                user_data["sip"] = int(line.split()[-1].replace("₹", "").replace(",", ""))
            elif "risk" in line:
                user_data["risk"] = line.split()[-1].lower()

        goal = user_data["goal"]
        tenure = user_data["tenure"]
        sip = user_data["sip"]
        risk = user_data["risk"]

        # Fund matching
        match, error = match_fund(sip, tenure, risk)

        if error:
            return jsonify({"message": f"Sorry! {error}"})

        fund_name = match['fund']
        logic = match['logic']
        explanation = match['explanation']
        hindi = match['hindi_explanation']

        response = f"""📊 *Fund Recommendation*\n
✅ *{fund_name}*\n
🧠 *Logic:* {logic}\n
📘 *Explanation:* {explanation}\n
🗣️ *हिंदी में:* {hindi}
        """

    except Exception as e:
        response = ("⚠️ Error parsing input.\n"
                    "Please send your details like this:\n"
                    "`goal 10000000`\n"
                    "`tenure 7 years`\n"
                    "`sip 60000`\n"
                    "`risk aggressive`")

    return jsonify({"message": response})

if __name__ == "__main__":
    app.run(debug=True)
