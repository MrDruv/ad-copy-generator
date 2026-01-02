from flask import Flask, request, jsonify, send_from_directory, render_template
from weasyprint import HTML
import os
import uuid
import traceback
import time
from datetime import datetime

app = Flask(__name__)

# Writable directory for temporary PDF storage
OUTPUT_DIR = "/tmp"

def cleanup_old_files(directory, max_age_seconds=600):
    """Deletes files older than the specified time (default 1 hour)."""
    try:
        now = time.time()
        for f in os.listdir(directory):
            path = os.path.join(directory, f)
            # Only target files with our 'offer-' prefix to be safe
            if f.startswith("offer-") and os.stat(path).st_mtime < now - max_age_seconds:
                if os.path.isfile(path):
                    os.remove(path)
    except Exception as e:
        print(f"Cleanup Error: {e}")

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    # 1. Trigger the cleanup timer logic
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

        # 2. Render HTML with all data fields
        rendered_html = render_template(
            'offer_letter.html',
            name=candidate.get('name', '[Candidate Name]'),
            location=role.get('location', 'Remote'),
            title=role.get('title', '[Role]'),
            department=role.get('department', 'Engineering'),
            level=role.get('level', 'L1'),
            salary=comp.get('total_ctc', 'TBD'),
            base_salary=comp.get('base_salary', 'TBD'),
            bonus=comp.get('bonus', 'N/A'),
            reporting_manager=role.get('reporting_manager', 'TBD'),
            employment_type=role.get('employment_type', 'Full-Time'),
            joining_date=raw_data.get('joining_date', 'TBD'),
            current_date=datetime.now().strftime("%B %d, %Y")
        )

        # 3. Save PDF to /tmp
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        HTML(string=rendered_html).write_pdf(target=filepath)

        # 4. Construct Secure HTTPS Link
        base_url = request.host_url.replace("http://", "https://").rstrip('/')
        download_url = f"{base_url}/download/{filename}"

        return jsonify({
            "status": "success",
            "download_url": download_url,
            "message": "File will be available for 60 minutes."
        })

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/download/<filename>')
def serve_pdf(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
