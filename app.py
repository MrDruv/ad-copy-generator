from flask import Flask, request, send_file, render_template, url_for
from weasyprint import HTML
import io
from datetime import datetime
import os

app = Flask(__name__)


OUTPUT_DIR = "static/offers"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def home():
    return {
        "status": "online",
        "message": "Phronetic AI Offer Letter API is running.",
        "endpoint": "/generate-pdf (POST)"
    }

@app.route('/generate-pdf', methods=['GET', 'POST']) 
def generate_pdf():
   
    if request.method == 'GET':
        return {
            "error": "Method Not Allowed for Browser",
            "message": "This endpoint requires a POST request with JSON data to generate a PDF.",
            "usage_example": {
                "name": "John Doe",
                "title": "Software Engineer",
                "salary": "10 LPA"
            }
        }, 405
    try:
        data = request.json
        if not data:
            return {"error": "Missing JSON payload"}, 400

        # 1. Render HTML
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
        
        # 2. Define unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = data.get('name', 'Candidate').replace(" ", "_")
        filename = f"Offer_{safe_name}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 3. Save PDF to disk (so we can provide a link)
        HTML(string=rendered_html).write_pdf(target=filepath)
        
        # 4. Return JSON with Link (Required for Phase 6 of your Orchestrator)
        # Change 'your-render-url.onrender.com' to your actual Render domain
        host = request.host_url.rstrip('/') 
        download_url = f"{host}/{OUTPUT_DIR}/{filename}"

        return {
            "status": "success",
            "message": f"Offer letter for {data.get('name')} generated.",
            "download_url": download_url
        }, 200

    except Exception as e:
        return {"error": str(e)}, 500

# Route to allow the Agent/User to actually download the file
@app.route('/static/offers/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
