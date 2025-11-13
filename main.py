from flask import Flask, request, jsonify
import re
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"})


@app.route('/', methods=['POST'])
def extract_company_data():
    try:
        # ✅ Step 1: Capture everything Zapier sends
        raw_body = request.get_data(as_text=True)
        print("\n📥 RAW REQUEST BODY:", raw_body)

        # ✅ Step 2: Try to parse JSON, else fallback to form or raw text
        try:
            data = request.get_json(force=True)
            print("📦 Parsed JSON:", data)
        except Exception:
            # Try to decode as form
            try:
                data = request.form.to_dict()
                print("📑 Parsed FORM:", data)
            except Exception:
                data = {"raw": raw_body}

        # ✅ Step 3: Find the main text field (works with Gmail & Zapier)
        email_text = (
            data.get("Body")
            or data.get("body")
            or data.get("plain")
            or data.get("text")
            or data.get("snippet")
            or data.get("raw")
            or raw_body
        )
        print("📩 Email text detected:", email_text[:300])

        # ✅ Step 4: Extract structured info
        company_match = re.search(r'([A-Za-z0-9&\s]+(?:Pvt|Ltd|LLP|Inc|Company|Corporation)[A-Za-z\s]*)', email_text)
        service_match = re.search(r'offer[s]? (.+?)(?: in| at| for|\.|$)', email_text, re.IGNORECASE)
        city_match = re.search(r'in ([A-Za-z\s]+)', email_text)
        contact_match = re.search(r'Contact[:\-]?\s*([A-Za-z\s]+)', email_text)
        phone_match = re.search(r'(\+?\d[\d\s\-]{7,15})', email_text)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', email_text)

        # ✅ Step 5: Format output for Zapier → Google Sheets
        extracted = {
            "Company Name": company_match.group(1).strip() if company_match else "Not Found",
            "Service Offered": service_match.group(1).strip() if service_match else "Not Found",
            "City": city_match.group(1).strip() if city_match else "Not Found",
            "Contact Person": contact_match.group(1).strip() if contact_match else "Not Found",
            "Email": email_match.group(0) if email_match else "Not Found",
            "Phone": phone_match.group(1).strip() if phone_match else "Not Found",
            "Summary": email_text[:200] + "..." if len(email_text) > 200 else email_text,
            "Status": "Received"
        }

        print("✅ FINAL EXTRACTED DATA:", json.dumps(extracted, indent=2))
        from flask import make_response, jsonify

@app.route('/', methods=['POST'])
def handle_webhook():
    data = request.get_json(force=True)
    extracted = extract_company_data(data.get("Body", ""))

    print("✅ FINAL EXTRACTED DATA:", extracted)
    response = make_response(jsonify(extracted), 200)
    response.headers["Content-Type"] = "application/json"
    return response


    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

        
        
