from flask import Flask, request, jsonify, make_response
import re

app = Flask(__name__)

# ---------- Helper Function ----------
def extract_company_data(body_text):
    """
    Extracts company info from plain text or email body.
    Adjust regexes if your email formats differ.
    """
    extracted = {
        "Company Name": "Not Found",
        "Service Offered": "Not Found",
        "City": "Not Found",
        "Contact Person": "Not Found",
        "Email": "Not Found",
        "Phone": "Not Found",
        "Summary": body_text[:200],  # First 200 chars
        "Status": "Received"
    }

    # Patterns — adjust as needed for your emails
    company_match = re.search(r"(?:Company|Organisation|Firm)\s*[:\-]\s*(.+)", body_text, re.I)
    service_match = re.search(r"(?:Service Offered|Service)\s*[:\-]\s*(.+)", body_text, re.I)
    city_match = re.search(r"(?:City|Location)\s*[:\-]\s*(.+)", body_text, re.I)
    contact_match = re.search(r"(?:Contact Person|Name)\s*[:\-]\s*(.+)", body_text, re.I)
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body_text)
    phone_match = re.search(r"\b\d{10}\b", body_text)

    # Assign matches if found
    if company_match: extracted["Company Name"] = company_match.group(1).strip()
    if service_match: extracted["Service Offered"] = service_match.group(1).strip()
    if city_match: extracted["City"] = city_match.group(1).strip()
    if contact_match: extracted["Contact Person"] = contact_match.group(1).strip()
    if email_match: extracted["Email"] = email_match.group(0).strip()
    if phone_match: extracted["Phone"] = phone_match.group(0).strip()

    return extracted


# ---------- Webhook Endpoint ----------
@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        # Try reading JSON (Zapier sends this way)
        data = request.get_json(force=True, silent=True) or {}
        print("📥 RAW REQUEST BODY:", data)

        # Handle fallback for form-encoded (if Gmail sends plain form)
        if not data and request.form:
            data = request.form.to_dict()
            print("📥 Parsed from form data:", data)

        # Extract email body text safely
        body_text = data.get("Body") or data.get("body") or ""
        extracted = extract_company_data(body_text)

        print("✅ FINAL EXTRACTED DATA:", extracted)

        # Return JSON response properly
        response = make_response(jsonify(extracted), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ---------- Health Check Route ----------
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"})


# ---------- Main ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


        
       
