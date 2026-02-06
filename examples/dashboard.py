from flask import Flask, render_template_string, jsonify
import random
import time
import threading

app = Flask(__name__)

# Mock Data Store
stats = {
    "total_packets": 0,
    "bandwidth_saved": 0, # bytes
    "active_agents": ["Agent_A", "Agent_B", "Observer"],
    "trust_score": 0.95
}

logs = []

def generate_mock_traffic():
    """Simulate background traffic for the dashboard"""
    actions = ["MOVE", "SCAN", "ALERT", "SYNC"]
    while True:
        action = random.choice(actions)
        size = random.randint(50, 200)
        saved = int(size * random.uniform(0.3, 0.7))
        
        stats["total_packets"] += 1
        stats["bandwidth_saved"] += saved
        stats["trust_score"] = max(0.8, min(1.0, stats["trust_score"] + random.uniform(-0.01, 0.01)))
        
        log_entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "sender": random.choice(stats["active_agents"]),
            "action": action,
            "size": f"{size}b",
            "saved": f"{saved}b"
        }
        logs.insert(0, log_entry)
        if len(logs) > 20: logs.pop()
        
        time.sleep(2)

# Start background thread
t = threading.Thread(target=generate_mock_traffic, daemon=True)
t.start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>UAL Live Dashboard</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }
        .card { border: 1px solid #333; padding: 15px; margin-bottom: 20px; background: #222; }
        h1 { color: #fff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 8px; border-bottom: 1px solid #333; }
        .metric { font-size: 24px; font-weight: bold; }
        .label { font-size: 12px; color: #888; }
    </style>
    <script>
        function updateStats() {
            fetch('/api/stats').then(r => r.json()).then(data => {
                document.getElementById('pkt').innerText = data.total_packets;
                document.getElementById('bw').innerText = data.bandwidth_saved + ' bytes';
                document.getElementById('trust').innerText = (data.trust_score * 100).toFixed(1) + '%';
                
                let logHtml = '<tr><th>Time</th><th>Sender</th><th>Action</th><th>Size</th><th>Delta Saved</th></tr>';
                data.logs.forEach(l => {
                    logHtml += `<tr><td>${l.timestamp}</td><td>${l.sender}</td><td>${l.action}</td><td>${l.size}</td><td>${l.saved}</td></tr>`;
                });
                document.getElementById('log-table').innerHTML = logHtml;
            });
        }
        setInterval(updateStats, 1000);
    </script>
</head>
<body>
    <h1>🚀 UAL Live Dashboard (v0.2.1)</h1>
    
    <div style="display: flex; gap: 20px;">
        <div class="card" style="flex:1">
            <div class="label">TOTAL PACKETS</div>
            <div class="metric" id="pkt">0</div>
        </div>
        <div class="card" style="flex:1">
            <div class="label">BANDWIDTH SAVED (Delta)</div>
            <div class="metric" id="bw">0</div>
        </div>
        <div class="card" style="flex:1">
            <div class="label">NETWORK TRUST SCORE</div>
            <div class="metric" id="trust">100%</div>
        </div>
    </div>

    <div class="card">
        <h3>Live Traffic Log</h3>
        <table id="log-table">
            <!-- Populated by JS -->
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    return jsonify({
        **stats,
        "logs": logs
    })

if __name__ == '__main__':
    print("Starting UAL Dashboard on http://localhost:5000")
    app.run(port=5000)
