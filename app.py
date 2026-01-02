from flask import Flask, request, jsonify, send_from_directory, render_template
from weasyprint import HTML
import os
import uuid
import traceback
from datetime import datetime

app = Flask(__name__)

# Use /tmp for Docker/Cloud compatibility (guaranteed writable)
OUTPUT_DIR = "/tmp"

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "live",
        "message": "Dockerized Phronetic AI API is running!",
        "version": "3.0"
    })

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # 1. Extract Data Blocks (matching your Orchestrator schema)
        company = raw_data.get('company_info', {})
        candidate = raw_data.get('candidate_info', {})
        role = raw_data.get('role_info', {})
        comp = raw_data.get('compensation_info', {})

        # 2. Render the external HTML Template
        # Ensure 'offer_letter.html' is in a folder named 'templates'
        rendered_html = render_template(
            'offer_letter.html',
            company_name=company.get('name', 'Phronetic AI'),
            name=candidate.get('name', '[Candidate Name]'),
            title=role.get('title', '[Role]'),
            location=role.get('location', 'Remote'),
            salary=comp.get('total_ctc', 'TBD'),
            level=role.get('level', 'L1'),
            current_date=datetime.now().strftime("%B %d, %Y")
        )

        # 3. Generate PDF and save to /tmp
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # WeasyPrint handles the HTML -> PDF conversion
        HTML(string=rendered_html).write_pdf(target=filepath)

        # 4. Construct the downloadable URL
        base_url = request.host_url.replace("http://", "https://").rstrip('/')
        download_url = f"{base_url}/download/{filename}"

        return jsonify({
            "status": "success",
            "download_url": download_url,
            "filename": filename,
            "preview": f"Offer generated for {candidate.get('name')}"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# Serve file from /tmp via a public /download/ route
@app.route('/download/<filename>')
def serve_pdf(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # Docker uses the PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
