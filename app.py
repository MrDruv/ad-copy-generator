from flask import Flask, request, send_file, render_template
from weasyprint import HTML
import io
from datetime import datetime
import os

app = Flask(__name__)
@app.route('/')
def home():
    return {
        "status": "online",
        "message": "Phronetic AI Offer Letter API is running.",
        "endpoint": "/generate-pdf (POST)"
    }
@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        
        # Mapping all professional fields requested
        rendered_html = render_template(
            'offer_letter.html', 
            name=data.get('name', '[Candidate Name]'),
            location=data.get('location', '[Location]'),
            title=data.get('title', '[Job Title]'),
            department=data.get('department', '[Department]'),
            level=data.get('level', '[Level]'),
            salary=data.get('salary', '[Salary Amount]'),
            bonus=data.get('bonus', '[Bonus Details]'),
            equity=data.get('equity', '[Equity Details]'),
            current_date=datetime.now().strftime("%B %d, %Y")
        )
        
        # Generate PDF in memory
        pdf_file = io.BytesIO()
        HTML(string=rendered_html).write_pdf(target=pdf_file)
        pdf_file.seek(0)
        
        filename = f"Offer_Letter_{data.get('name', 'Candidate')}.pdf".replace(" ", "_")
        
        return send_file(
            pdf_file,
            mimetype='application/pdf',
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
