from flask import Flask, request
import json
import re

app = Flask(__name__)

# -----------------------------
# Helper Function
# -----------------------------
def extract_company_data(body_text):
    extracted = {
        "Company Name": "Not Found",
        "Service Offered": "Not Found",
        "City": "Not Found",
        "Contact Person": "Not Found",
        "Email": "Not Found",
        "Phone": "Not Found",
        "Summary": body_text[:200] + "..." if len(body_text) > 200 else body_text,
        "Status": "Received"
    }

    # Regex patterns
    company_match = re.search(r"We are\s+([A-Za-z0-9&\s]+)", body_text, re.I)
    service_match = re.search(r"offer\s+([A-Za-z\s]+)", body_text, re.I)
    city_match = re.search(r"in\s+([A-Za-z\s]+)", body_text, re.I)
    contact_match = re.search(r"Contact[:\-]?\s*([A-Za-z\s]+)", body_text, re.I)
    phone_match = re.search(r"(\+?\d[\d\s\-]{7,15})", body_text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", body_text)

    if company_match: extracted["Company Name"] = company_match.group(1).strip()
    if service_match: extracted["Service Offered"] = service_match.group(1).strip()
    if city_match: extracted["City"] = city_match.group(1).strip()
    if contact_match: extracted["Contact Person"] = contact_match.group(1).strip()
    if phone_match: extracted["Phone"] = phone_match.group(1).strip()
    if email_match: extracted["Email"] = email_match.group(0).strip()

    return extracted


# -----------------------------
# Webhook Endpoint
# -----------------------------
@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        data = request.get_json(force=True, silent=True) or {}
        print("📥 RAW REQUEST BODY:", data)

        # Handle the “Data” string from Zapier
        if isinstance(data, dict) and "Data" in data and isinstance(data["Data"], str):
            try:
                inner_data = json.loads(data["Data"])  # Parse the stringified JSON
                print("🔍 Parsed inner Data JSON:", inner_data)
                data = inner_data
            except json.JSONDecodeError:
                print("⚠️ Could not parse inner JSON string. Using as-is.")

        # Pick text from any likely key
        possible_keys = ["Body", "body", "plain", "bodyPlain", "snippet", "text"]
        body_text = ""
        for key in possible_keys:
            if key in data and isinstance(data[key], str):
                body_text = data[key]
                break

        if not body_text:
            body_text = str(data)

        extracted = extract_company_data(body_text)
        print("✅ FINAL EXTRACTED DATA:", extracted)

        # Return FLAT JSON for Zapier
        return extracted, 200

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}, 500


# -----------------------------
# Health Route
# -----------------------------
@app.route('/', methods=['GET'])
def home():
    return {"message": "Partnership Inquiry Webhook is live!"}, 200


# -----------------------------
# Runner
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
