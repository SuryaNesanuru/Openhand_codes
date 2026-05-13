#!/usr/bin/env python3
"""
Shopping Assistant Web Demo
A simple Flask web app to demo the shopping assistant.
"""

from flask import Flask, render_template_string, request, jsonify
import json
import re
from typing import Dict, List, Any, Optional

app = Flask(__name__)
PRODUCTS_FILE = "/workspace/project/data/products.json"

# Load products
with open(PRODUCTS_FILE, 'r') as f:
    PRODUCTS = json.load(f)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛒 Shopping Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            text-align: right;
        }
        .message .bubble {
            display: inline-block;
            padding: 12px 18px;
            border-radius: 18px;
            max-width: 80%;
            line-height: 1.5;
        }
        .message.user .bubble {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.assistant .bubble {
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 4px;
        }
        .products {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
            text-align: left;
        }
        .product {
            display: flex;
            gap: 12px;
            padding: 12px;
            background: white;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid #e9ecef;
        }
        .product:last-child { margin-bottom: 0; }
        .product-img {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #e9ecef, #dee2e6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .product-info { flex: 1; }
        .product-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }
        .product-price {
            color: #667eea;
            font-weight: 700;
            font-size: 1.1rem;
        }
        .product-brand {
            color: #6c757d;
            font-size: 0.85rem;
        }
        .product-available {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .available { background: #d4edda; color: #155724; }
        .unavailable { background: #f8d7da; color: #721c24; }
        .input-area {
            display: flex;
            gap: 10px;
            padding: 20px;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }
        .input-area input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 30px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        .input-area input:focus {
            border-color: #667eea;
        }
        .input-area button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, background 0.3s;
        }
        .input-area button:hover {
            background: #5a6fd6;
            transform: scale(1.02);
        }
        .suggestions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            padding: 0 20px 15px;
        }
        .suggestion {
            padding: 8px 16px;
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .suggestion:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 Shopping Assistant</h1>
            <p>Find exactly what you're looking for</p>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    <div class="bubble">
                        👋 Hi there! I'm your shopping assistant. What can I help you find today?
                    </div>
                </div>
            </div>
            
            <div class="suggestions">
                <div class="suggestion" onclick="ask('running shoes under \$100')">Running shoes under $100</div>
                <div class="suggestion" onclick="ask('wireless headphones')">Wireless headphones</div>
                <div class="suggestion" onclick="ask('yoga pants')">Yoga pants</div>
                <div class="suggestion" onclick="ask('smartphones')">Smartphones</div>
            </div>
            
            <form class="input-area" id="inputForm">
                <input type="text" id="query" placeholder="Try: 'Find running shoes under $100'" autocomplete="off">
                <button type="submit">Search</button>
            </form>
        </div>
    </div>
    
    <script>
        function ask(q) {
            document.getElementById('query').value = q;
            submitForm();
        }
        
        function submitForm() {
            const query = document.getElementById('query').value.trim();
            if (!query) return;
            
            addMessage('user', query);
            document.getElementById('query').value = '';
            
            fetch('/api/search', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            })
            .then(r => r.json())
            .then(data => {
                addMessage('assistant', '', data);
            });
        }
        
        function addMessage(role, text, data) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = 'message ' + role;
            
            if (role === 'user') {
                div.innerHTML = '<div class="bubble">' + text + '</div>';
            } else if (data && data.products && data.products.length > 0) {
                let html = '<div class="bubble">';
                if (data.count === 1) {
                    html += 'I found 1 product for you!';
                } else {
                    html += 'I found ' + data.count + ' products for you!';
                }
                html += '</div><div class="products">';
                
                for (const p of data.products.slice(0, 4)) {
                    const emoji = getEmoji(p.category);
                    html += '<div class="product">';
                    html += '<div class="product-img">' + emoji + '</div>';
                    html += '<div class="product-info">';
                    html += '<div class="product-name">' + p.name + '</div>';
                    html += '<div class="product-brand">' + p.brand + '</div>';
                    html += '<div class="product-price">$' + p.price.toFixed(2) + '</div>';
                    html += '</div>';
                    html += '<span class="product-available ' + (p.available ? 'available' : 'unavailable') + '">';
                    html += p.available ? '✅ In Stock' : '❌ Out of Stock';
                    html += '</span></div>';
                }
                
                html += '</div>';
                div.innerHTML = html;
                
                if (data.products[0] && data.products[0].available) {
                    div.innerHTML += '<div class="message assistant"><div class="bubble">Would you like more details on any of these? Just ask!</div></div>';
                }
            } else {
                div.innerHTML = '<div class="bubble">I couldn\'t find any products matching that. Try different keywords or browse our suggestions above!</div>';
            }
            
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function getEmoji(category) {
            const map = {
                'running-shoes': '👟',
                'headphones': '🎧',
                'smartphones': '📱',
                'yoga-pants': '👖',
                'laptops': '💻',
                'gaming': '🎮',
                'wearables': '⌚',
                'kitchen': '🍳',
                'home': '🏠',
                'audio': '🔊'
            };
            return map[category] || '📦';
        }
        
        document.getElementById('inputForm').onsubmit = function(e) {
            e.preventDefault();
            submitForm();
        };
    </script>
</body>
</html>
'''

def search_products(query: str) -> Dict[str, Any]:
    """Search products by query."""
    query_lower = query.lower()
    filters = {}
    
    # Extract price "under $X"
    under_match = re.search(r'under\s*\$?(\d+)', query_lower)
    if under_match:
        filters['max_price'] = float(under_match.group(1))
    
    # Extract category
    category_map = {
        'running shoes': 'running-shoes',
        'headphone': 'headphones',
        'yoga pants': 'yoga-pants',
        'smartphone': 'smartphones',
        'laptop': 'laptops',
        'gaming': 'gaming',
        'wearable': 'wearables',
        'kitchen': 'kitchen',
        'home': 'home',
        'audio': 'audio'
    }
    for term, cat in category_map.items():
        if term in query_lower:
            filters['category'] = cat
            break
    
    # Search products
    results = []
    for p in PRODUCTS:
        searchable = f"{p.get('name', '')} {p.get('description', '')} {p.get('brand', '')}"
        searchable += ' '.join(p.get('tags', []))
        
        if any(word in searchable.lower() for word in query_lower.split() if len(word) > 2):
            results.append(p)
    
    # Apply price filter
    if 'max_price' in filters:
        results = [p for p in results if p.get('price', float('inf')) <= filters['max_price']]
    
    # Limit to 10
    return {
        "query": query,
        "filters": filters,
        "products": results[:10],
        "count": len(results[:10])
    }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    query = data.get('query', '')
    results = search_products(query)
    return jsonify(results)

if __name__ == '__main__':
    print("🛒 Starting Shopping Assistant...")
    print("   Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=False)