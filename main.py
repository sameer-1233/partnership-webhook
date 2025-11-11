from flask import Flask, request, jsonify
import re
import sys
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"}), 200


@app.route('/', methods=['POST'])
def extract_company_data():
    try:
        # Print raw request data for debugging
        raw_data = request.data.decode('utf-8')
        print("\n==========================")
        print("📥 RAW REQUEST BODY:", raw_data)
        print("==========================\n")

        # Try to parse JSON safely
        try:
            data = json.loads(raw_data)
        except Exception as e:
            print("❌ Could not parse JSON:", e)
            return jsonify({"error": "Invalid JSON", "raw_data": raw_data}), 400

        print("✅ PARSED JSON:", data)

        # Try multiple possible keys for email text
        possible_keys = ["Body", "body", "plain", "snippet", "text", "message"]
        email_text = ""
        for key in possible_keys:
            if key in data:
                email_text = data[key]
                break

        if not email_text:
            print("⚠️  No email text found, dumping keys ->", list(data.keys()))
            return jsonify({"error": "Missing email text", "available_keys": list(data.keys())}), 400

        print("📩 EMAIL TEXT:", email_text)

        # --- Regex Extraction Logic ---
        company_match = re.search(r'([A-Za-z0-9&\s]+(?:Pvt|Ltd|LLP|Inc|Company|Corporation)[A-Za-z\s]*)', email_text)
        service_match = re.search(r'offer[s]? (.+?)(?: in| at| for|\.|$)', email_text, re.IGNORECASE)
        city_match = re.search(r'in ([A-Za-z\s]+)', email_text)
        contact_match = re.search(r'Contact[:\-]?\s*([A-Za-z\s]+)', email_text)
        phone_match = re.search(r'(\+?\d[\d\s\-]{7,15})', email_text)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', email_text)

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

        print("✅ EXTRACTED:", extracted)
        return jsonify(extracted), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

