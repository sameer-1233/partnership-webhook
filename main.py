from flask import Flask, request, jsonify
import json, re

app = Flask(__name__)

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

    company = re.search(r"We are\s+([A-Za-z0-9&\s]+)", body_text, re.I)
    service = re.search(r"offer\s+([A-Za-z\s]+)", body_text, re.I)
    city = re.search(r"in\s+([A-Za-z\s]+)", body_text, re.I)
    contact = re.search(r"Contact[:\-]?\s*([A-Za-z\s]+)", body_text, re.I)
    phone = re.search(r"(\+?\d[\d\s\-]{7,15})", body_text)
    email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", body_text)

    if company: extracted["Company Name"] = company.group(1).strip()
    if service: extracted["Service Offered"] = service.group(1).strip()
    if city: extracted["City"] = city.group(1).strip()
    if contact: extracted["Contact Person"] = contact.group(1).strip()
    if phone: extracted["Phone"] = phone.group(1).strip()
    if email: extracted["Email"] = email.group(0).strip()

    return extracted


@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        data = request.get_json(force=True, silent=True) or {}
        print("📥 RAW REQUEST BODY:", data)

        # Some versions of Zapier wrap the payload inside 'Data'
        if "Data" in data and isinstance(data["Data"], str):
            try:
                data = json.loads(data["Data"])
            except:
                pass

        body_text = data.get("Body") or data.get("body") or ""
        extracted = extract_company_data(body_text)

        print("✅ FINAL EXTRACTED DATA:", extracted)

        # ✅ Return FLAT JSON that Zapier unpacks automatically
        return jsonify(extracted)

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Partnership Inquiry Webhook is live!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
