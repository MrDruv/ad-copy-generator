import os
from flask import Flask, request, jsonify, send_from_directory
from tool import generate_gemini_image

app = Flask(__name__)

# Route 1: Trigger Generation
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Run the tool
    filename = generate_gemini_image(prompt)

    if filename.startswith("Error"):
        return jsonify({"status": "failed", "message": filename}), 500

    # Create the Download Link
    # This URL points to your Render app's /download/ route
    download_link = f"{request.host_url}download/{filename}"

    return jsonify({
        "status": "success",
        "file_path": f"/tmp/{filename}",
        "s3_link": download_link  # This is your download URL
    })

# Route 2: The "S3 Link" behavior (Download the file)
@app.route('/download/<filename>')
def download_file(filename):
    # Serves the file directly from /tmp/
    return send_from_directory('/tmp', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
