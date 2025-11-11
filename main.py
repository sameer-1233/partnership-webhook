from flask import Flask, request, jsonify
import re, json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"})

@app.route('/', methods=['POST'])
def extract_company_data():
    try:
        # Try JSON first
        data = request.get_json(silent=True)

        # If not JSON, try form data (Zapier sometimes sends form-encoded)
        if not data:
            raw_data = request.data.decode("utf-8")
            print("📥 Raw request (non-JSON):", raw_data)
            try:
                data = json.loads(raw_data)
            except:
                # Convert form-encoded format into dict
                data = dict(request.form)
        
        print("📥 Final parsed data:", data)

        # Extract text from possible keys
        email_text = (
            data.get("Body")
            or data.get("body")
            or data.get("plain")
            or data.get("snippet")
            or data.get("text")
            or ""
        )

        print("📩 Email text:", email_text)

        # Regex extraction logic
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
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

        
        
