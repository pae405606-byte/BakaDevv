from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- 1. HOME ROUTE ---
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "system": "BakaApi Gateway",
        "example_usage": "https://baka-devv.vercel.app/checkmd5?md5=be24856c6e84f68630d98c2a54e7b2a5"
    }), 200

# --- 2. EASY GET API CHECK MD5 ROUTE ---
@app.route('/checkmd5', methods=['GET'])
def check_md5():
    try:
        # ចាប់យកកូដ md5 ដែលហុចមកតាម URL (ឧទាហរណ៍៖ ?md5=xxxx)
        md5_value = request.args.get('md5')
        
        if not md5_value:
            return jsonify({
                "success": False, 
                "message": "Missing 'md5' parameter in URL. Example: /checkmd5?md5=your_md5_here"
            }), 400

        # រត់ទៅសួរខាង anajak API ភ្លាមៗ
        anajak_url = f"https://anajak.site/bakong/api/check?md5={md5_value}"
        response = requests.get(anajak_url)
        result_data = response.json()

        # ចាប់យកលទ្ធផល (Status) ពីខាង anajak មកវិញ
        current_status = result_data.get('status', 'UNPAID')

        # បោះលទ្ធផលជះត្រឡប់ទៅវិញ
        if result_data.get('success') is True and current_status == 'PAID':
            return jsonify({
                "success": True,
                "status": "PAID",
                "message": "Payment verified successfully!"
            }), 200
        else:
            return jsonify({
                "success": False,
                "status": current_status,
                "message": result_data.get('message', 'Transaction pending or invalid.')
            }), 200

    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Gateway Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
