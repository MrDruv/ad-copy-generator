from flask import Flask, request, jsonify, send_from_directory, render_template
from weasyprint import HTML
import os
import uuid
import traceback
import time
from datetime import datetime

app = Flask(__name__)

# Production-safe temporary directory
OUTPUT_DIR = "/tmp"

def cleanup_old_files(directory, max_age_seconds=900):
    """Automatically deletes PDFs older than 1 hour to save space."""
    try:
        now = time.time()
        for f in os.listdir(directory):
            path = os.path.join(directory, f)
            if f.startswith("offer-") and os.stat(path).st_mtime < now - max_age_seconds:
                if os.path.isfile(path):
                    os.remove(path)
    except Exception as e:
        print(f"Cleanup Error: {e}")

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    # Trigger timer-based cleanup
    cleanup_old_files(OUTPUT_DIR)

    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # Data Extraction
        company = raw_data.get('company_info', {})
        candidate = raw_data.get('candidate_info', {})
        role = raw_data.get('role_info', {})
        comp = raw_data.get('compensation_info', {})

        # Render HTML with Dynamic Placeholders
        rendered_html = render_template(
            'offer_letter.html',
            company_name=company.get('name', '[company_name]'), # Placeholder if name missing
            name=candidate.get('name', '[Candidate Name]'),
            candidate_location.get('location', '[candidate_location]'),
            location=role.get('location', 'Remote'),
            title=role.get('title', '[Role]'),
            department=role.get('department', 'General'),
            level=role.get('level', 'N/A'),
            reporting_manager=role.get('reporting_manager', 'TBD'),
            employment_type=role.get('employment_type', 'Full-Time'),
            total_ctc=comp.get('total_ctc', '0'),
            salary=comp.get('base_salary', '0'),
            bonus=comp.get('bonus', '0%'),
            equity=comp.get('equity', 'None'),
            benefits=raw_data.get('benefits', []),
            gross_pay=raw_data.get('gross_pay', 'N/A'),
            total_deductions=raw_data.get('total_deductions', 'N/A'),
            take_home_pay=raw_data.get('take_home_pay', 'N/A'),
            take_home=raw_data.get('take_home_pay', 'N/A'),
            joining_date=raw_data.get('joining_date', 'TBD'),
            current_date=datetime.now().strftime("%B %d, %Y")
        )

        # Generate and save PDF
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        HTML(string=rendered_html).write_pdf(target=filepath)

        # Force HTTPS for the download link
        base_url = request.host_url.replace("http://", "https://").rstrip('/')
        download_url = f"{base_url}/download/{filename}"

        return jsonify({
            "status": "success",
            "download_url": download_url,
            "expires_in": "60 minutes"
        })

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/download/<filename>')
def serve_pdf(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # For local development only; production uses Gunicorn
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
