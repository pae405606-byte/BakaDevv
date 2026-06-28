from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/checkmd5', methods=['GET'])
def check_md5():
    md5_value = request.args.get('md5')
    if not md5_value:
        return jsonify({"success": False, "message": "Missing md5 parameter"}), 400
    
    try:
        # បាញ់ទៅសួរ anajak.site
        res = requests.get(f"https://anajak.site/bakong/api/check?md5={md5_value}", timeout=5)
        return jsonify(res.json()), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/')
def index():
    return "API is Online"
