from flask import Flask, request, jsonify, render_template_string
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            md5 TEXT UNIQUE,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- COOL DARK MODE HTML TEMPLATE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BakaApi - Cyber Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#0f172a] text-slate-200 p-4 md:p-8 font-sans min-h-screen">

    <div class="max-w-6xl mx-auto">
        
        <div class="flex flex-col md:flex-row justify-between items-center bg-[#1e293b]/60 backdrop-blur-md p-6 rounded-2xl shadow-xl mb-8 border border-slate-800">
            <div class="flex items-center gap-4">
                <div class="bg-gradient-to-tr from-indigo-600 to-violet-500 text-white p-3 rounded-xl shadow-lg shadow-indigo-500/30">
                    <i class="fa-solid fa-terminal text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-2xl font-black tracking-wide bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">BakaApi Center</h1>
                    <p class="text-xs text-slate-400 font-mono">STATUS: OPERATIONAL // MD5_CHECKER</p>
                </div>
            </div>
            <div class="mt-4 md:mt-0">
                <button onclick="window.location.reload()" class="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 cursor-pointer shadow-sm">
                    <i class="fa-solid fa-rotate-right animate-spin-slow"></i> Sync Node
                </button>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-[#1e293b]/40 border border-emerald-500/20 p-6 rounded-2xl shadow-lg flex items-center justify-between relative overflow-hidden group">
                <div class="absolute -right-4 -bottom-4 text-emerald-500/5 text-8xl transition-all group-hover:scale-110">
                    <i class="fa-solid fa-circle-check"></i>
                </div>
                <div class="space-y-2 relative z-10">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">DATABASE.SUCCESS_PAID</span>
                    <h3 class="text-5xl font-black text-emerald-400 tracking-tight">{{ success }}</h3>
                    <p class="text-xs text-emerald-400/90 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-md inline-block font-mono">
                        // verified_nodes
                    </p>
                </div>
                <div class="bg-emerald-500/10 text-emerald-400 p-4 rounded-xl border border-emerald-500/30 shadow-md shadow-emerald-500/5">
                    <i class="fa-solid fa-bolt text-2xl"></i>
                </div>
            </div>

            <div class="bg-[#1e293b]/40 border border-amber-500/20 p-6 rounded-2xl shadow-lg flex items-center justify-between relative overflow-hidden group">
                <div class="absolute -right-4 -bottom-4 text-amber-500/5 text-8xl transition-all group-hover:scale-110">
                    <i class="fa-solid fa-clock"></i>
                </div>
                <div class="space-y-2 relative z-10">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-widest font-mono">DATABASE.PENDING_UNPAID</span>
                    <h3 class="text-5xl font-black text-amber-400 tracking-tight">{{ failed }}</h3>
                    <p class="text-xs text-amber-400/90 bg-amber-500/10 border border-amber-500/20 px-2.5 py-0.5 rounded-md inline-block font-mono">
                        // awaiting_response
                    </p>
                </div>
                <div class="bg-amber-500/10 text-amber-400 p-4 rounded-xl border border-amber-500/30 shadow-md shadow-amber-500/5">
                    <i class="fa-solid fa-shield-halved text-2xl"></i>
                </div>
            </div>
        </div>

        <div class="bg-[#1e293b]/40 rounded-2xl shadow-xl border border-slate-800 overflow-hidden">
            <div class="p-6 border-b border-slate-800 flex justify-between items-center bg-[#1e293b]/20">
                <h3 class="font-bold text-slate-200 text-base flex items-center gap-2 font-mono">
                    <i class="fa-solid fa-list text-indigo-400"></i> TRANSACTION_LOGS
                </h3>
                <span class="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-mono px-3 py-1 rounded-full">
                    TOTAL_RECORDS: {{ transactions|length }}
                </span>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-[#0f172a]/40 border-b border-slate-800 text-slate-400 text-xs font-mono uppercase tracking-wider">
                            <th class="p-4 w-20">INDEX</th>
                            <th class="p-4">MD5_HASH_IDENTIFIER</th>
                            <th class="p-4 w-44">NETWORK_STATUS</th>
                            <th class="p-4 w-52">TIMESTAMP</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800 text-slate-300 text-sm font-mono">
                        {% if not transactions %}
                        <tr>
                            <td colspan="4" class="p-12 text-center text-slate-500">
                                <i class="fa-solid fa-folder-closed text-4xl block mb-3 text-slate-600"></i> 
                                <span class="text-sm">// NO LIVE DATA STREAM DETECTED</span>
                            </td>
                        </tr>
                        {% endif %}
                        
                        {% for tx in transactions %}
                        <tr class="hover:bg-slate-800/30 transition-all">
                            <td class="p-4 text-slate-500">#{{ "%03d" | format(tx[0]) }}</td>
                            <td class="p-4">
                                <span class="text-indigo-400 bg-indigo-950/40 border border-indigo-900/50 px-2.5 py-1 rounded-md text-xs font-bold tracking-wider select-all">{{ tx[1] }}</span>
                            </td>
                            <td class="p-4">
                                {% if tx[2] == 'PAID' %}
                                <span class="inline-flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 text-xs font-bold px-2.5 py-1 rounded-md border border-emerald-500/20">
                                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400"></span> SUCCESS
                                </span>
                                {% else %}
                                <span class="inline-flex items-center gap-1.5 bg-amber-500/10 text-amber-400 text-xs font-bold px-2.5 py-1 rounded-md border border-amber-500/20">
                                    <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> PENDING
                                </span>
                                {% endif %}
                            </td>
                            <td class="p-4 text-slate-400 text-xs">
                                <i class="fa-regular fa-clock text-xs mr-1 text-slate-500"></i> {{ tx[3] }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

    </div>

</body>
</html>
'''

# --- 1. DASHBOARD ROUTE ---
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
    all_tx = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='PAID'")
    total_success = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='UNPAID'")
    total_failed = cursor.fetchone()[0]
    conn.close()
    return render_template_string(HTML_TEMPLATE, transactions=all_tx, success=total_success, failed=total_failed)

# --- 2. API CHECK MD5 ROUTE ---
@app.route('/checkmd5', methods=['POST'])
def check_md5():
    try:
        incoming_data = request.get_json()
        if not incoming_data:
            return jsonify({"success": False, "message": "No data provided"}), 400

        md5_value = incoming_data.get('md5')
        if not md5_value:
            return jsonify({"success": False, "message": "Missing md5 parameter"}), 400

        anajak_url = f"https://anajak.site/bakong/api/check?md5={md5_value}"
        response = requests.get(anajak_url)
        result_data = response.json()

        current_status = result_data.get('status', 'UNPAID')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (md5, status, timestamp)
            VALUES (?, ?, ?)
            ON CONFLICT(md5) DO UPDATE SET status=excluded.status
        ''', (md5_value, current_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

        if result_data.get('success') is True and current_status == 'PAID':
            return jsonify({"success": True, "status": "PAID", "message": "Node activated. Payment successful."}), 200
        else:
            return jsonify({"success": False, "status": current_status, "message": "Node pending."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
