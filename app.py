import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# 1. Upload Route: Receives the image from your Agent
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save to /tmp/ (Render's temporary storage)
    save_path = os.path.join('/tmp', file.filename)
    file.save(save_path)

    # Generate the "S3-style" Link
    download_url = f"{request.host_url}download/{file.filename}"

    return jsonify({
        "status": "success",
        "url": download_url
    })

# 2. Download Route: Allows you to view/download the image
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('/tmp', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
