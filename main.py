from flask import Flask, request
import re

app = Flask(__name__)

# -----------------------------
# Helper Function: Extract Data
# -----------------------------
def extract_company_data(body_text):
    """
    Extracts company info (company name, service, city, contact person, phone, etc.)
    from an email body text. You can adjust regex patterns based on real examples.
    """

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
    company_match = re.search(
        r"(?:Company|Organisation|Firm|Business)\s*[:\-]\s*([A-Za-z0-9&\s\.]+)",
        body_text, re.IGNORECASE)
    service_match = re.search(
        r"(?:Service Offered|We offer|Service)\s*[:\-]?\s*([A-Za-z\s]+)",
        body_text, re.IGNORECASE)
    city_match = re.search(
        r"(?:City|Location|based in|in)\s*[:\-]?\s*([A-Za-z\s]+)",
        body_text, re.IGNORECASE)
    contact_match = re.search(
        r"(?:Contact Person|Name|Contact)\s*[:\-]?\s*([A-Za-z\s]+)",
        body_text, re.IGNORECASE)
    phone_match = re.search(r"(\+?\d[\d\s\-]{7,15})", body_text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", body_text)

    # Assign extracted matches
    if company_match: extracted["Company Name"] = company_match.group(1).strip()
    if service_match: extracted["Service Offered"] = service_match.group(1).strip()
    if city_match: extracted["City"] = city_match.group(1).strip()
    if contact_match: extracted["Contact Person"] = contact_match.group(1).strip()
    if phone_match: extracted["Phone"] = phone_match.group(1).strip()
    if email_match: extracted["Email"] = email_match.group(0).strip()

    return extracted


# -----------------------------
# POST Route: Zapier → Flask
# -----------------------------
@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        # Parse incoming JSON
        data = request.get_json(force=True, silent=True) or {}
        print("📥 RAW REQUEST BODY:", data)

        # Extract possible fields from Gmail/Zapier payload
        possible_keys = ["Body", "body", "plain", "bodyPlain", "snippet", "text"]
        body_text = ""
        for key in possible_keys:
            if key in data and isinstance(data[key], str):
                body_text = data[key]
                break

        if not body_text:
            body_text = str(data)

        # Run extraction logic
        extracted = extract_company_data(body_text)
        print("✅ FINAL EXTRACTED DATA:", extracted)

        # Return FLAT JSON (Zapier reads these as top-level fields)
        return extracted, 200

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}, 500


# -----------------------------
# GET Route: Health Check
# -----------------------------
@app.route('/', methods=['GET'])
def home():
    return {"message": "Partnership Inquiry Webhook is live!"}, 200


# -----------------------------
# App Runner
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
