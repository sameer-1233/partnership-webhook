from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"}), 200


@app.route('/', methods=['POST'])
def extract_company_data():
    try:
        # Log the raw request for debugging
        print("🔹 Incoming request headers:", dict(request.headers))
        print("🔹 Raw request data:", request.data)

        # Safely parse JSON
        data = request.get_json(silent=True) or {}
        print("✅ Parsed JSON:", data)

        # Try to get the email body
        email_text = data.get("Body") or data.get("body") or ""

        if not email_text:
            print("⚠️ No 'Body' field found in JSON! Returning error.")
            return jsonify({"error": "Missing 'Body' field in request"}), 400

        # --- Extract key details ---
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

        print("✅ Extracted Data:", extracted)

        return jsonify(extracted), 200

    except Exception as e:
        print("❌ Error occurred:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
