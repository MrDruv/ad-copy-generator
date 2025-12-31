from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import io
import os
import uuid
import traceback
import json

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Ensure static folder exists for temporary file storage
os.makedirs('static', exist_ok=True)

def ensure_dict(data):
    """Helper to convert string inputs to dict if needed."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return {"name": data}
    return data if data else {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "live",
        "message": "Professional Offer Letter API is running!",
        "version": "2.0"
    })

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "No JSON payload provided"}), 400

        # 1. Normalize and Validate Input Data
        company = ensure_dict(raw_data.get('company_info'))
        candidate = ensure_dict(raw_data.get('candidate_info'))
        role = ensure_dict(raw_data.get('role_info'))
        comp = ensure_dict(raw_data.get('compensation_info'))

        if not company or not candidate or not role:
            return jsonify({"error": "Missing required info blocks"}), 400

        # 2. Setup PDF Document
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer, 
            pagesize=A4,
            rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50
        )
        styles = getSampleStyleSheet()
        
        # Custom Style for the Header
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Title'],
            fontSize=22,
            textColor=colors.HexColor("#1A237E"),
            spaceAfter=10
        )
        
        story = []

        # --- Document Header ---
        story.append(Paragraph(company.get('name', 'Your Company').upper(), header_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceBefore=5, spaceAfter=20))
        
        # --- Date and Recipient ---
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"<b>To: {candidate.get('name', 'Valued Candidate')}</b>", styles['Normal']))
        story.append(Spacer(1, 15))

        # --- Subject ---
        story.append(Paragraph(f"<u>Subject: Offer of Employment - {role.get('title', 'Position')}</u>", styles['Heading2']))
        story.append(Spacer(1, 15))

        # --- Body Content ---
        opening_text = (
            f"Dear {candidate.get('name', 'Candidate')}, <br/><br/>"
            f"We are delighted to offer you the position of <b>{role.get('title', 'Position')}</b> "
            f"at <b>{company.get('name', 'our organization')}</b>. Based on your application and subsequent interviews, "
            f"we are confident that your skills and experience will be a significant asset to our team."
        )
        story.append(Paragraph(opening_text, styles['Normal']))
        story.append(Spacer(1, 15))

        # --- Role Details ---
        story.append(Paragraph("<b>Employment Details:</b>", styles['Heading3']))
        story.append(Paragraph(f"• <b>Location:</b> {role.get('location', 'Remote')}", styles['Normal']))
        
        # Handle CTC calculation safely
        total_ctc = comp.get('total_ctc', 0)
        try:
            ctc_val = float(total_ctc)
            ctc_text = f"₹{ctc_val/100000:.2f} Lakhs" if ctc_val >= 100000 else f"₹{ctc_val:,.2f}"
        except:
            ctc_text = str(total_ctc)

        story.append(Paragraph(f"• <b>Total Compensation (CTC):</b> {ctc_text} per annum", styles['Normal']))
        story.append(Paragraph(f"• <b>Proposed Joining Date:</b> {raw_data.get('joining_date', 'TBD')}", styles['Normal']))
        story.append(Spacer(1, 20))

        # --- Benefits (if any) ---
        compliance = raw_data.get('compliance_result', {})
        benefits = compliance.get('benefits', [])
        if benefits:
            story.append(Paragraph("<b>Standard Benefits:</b>", styles['Heading3']))
            for benefit in benefits:
                story.append(Paragraph(f"• {benefit}", styles['Normal']))
            story.append(Spacer(1, 20))

        # --- Closing and Signature ---
        story.append(Spacer(1, 30))
        story.append(Paragraph("Sincerely,", styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>HR Department</b><br/>{company.get('name', 'Company')}", styles['Normal']))
        
        story.append(Spacer(1, 40))
        story.append(Paragraph("__________________________<br/>Candidate Signature", styles['Normal']))

        # 3. Finalize PDF
        doc.build(story)
        pdf_buffer.seek(0)

        # Save to static folder
        filepath = os.path.join('static', filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        # Construct dynamic URL
        base_url = request.host_url.rstrip('/')
        download_url = f"{base_url}/static/{filename}"

        return jsonify({
            "status": "success",
            "download_url": download_url,
            "filename": filename,
            "preview": f"Offer generated for {candidate.get('name')} at {company.get('name')}"
        })

    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e), 
            "trace": traceback.format_exc()
        }), 500

@app.route('/static/<filename>')
def serve_pdf(filename):
    filepath = os.path.join('static', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
