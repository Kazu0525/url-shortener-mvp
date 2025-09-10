from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import random
import string
import os

app = FastAPI()

# メモリ内データベース
url_db = {}

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL短縮サービス</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
            margin: 20px 0;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #45a049;
        }
        #results {
            margin-top: 30px;
            display: none;
        }
        .result-item {
            background: #e8f5e9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }
        .error-item {
            background: #ffebee;
            border-left: 4px solid #f44336;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 URL短縮サービス</h1>
        <p>URLを入力してください（1行に1つ）</p>
        <textarea id="urls" placeholder="https://example.com&#10;https://google.com"></textarea>
        <button onclick="generateLinks()">短縮URLを生成</button>
        <div id="results"></div>
    </div>

    <script>
        async function generateLinks() {
            const urls = document.getElementById('urls').value.trim();
            if (!urls) {
                alert('URLを入力してください');
                return;
            }

            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'block';
            resultsDiv.innerHTML = '<div class="loading">処理中...</div>';

            try {
                const response = await fetch('/shorten', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'urls=' + encodeURIComponent(urls)
                });

                const data = await response.json();
                
                let html = '<h3>結果:</h3>';
                data.results.forEach(item => {
                    if (item.success) {
                        html += `<div class="result-item">
                            <strong>元URL:</strong> ${item.url}<br>
                            <strong>短縮URL:</strong> ${item.short_url}
                        </div>`;
                    } else {
                        html += `<div class="result-item error-item">
                            エラー: ${item.url}
                        </div>`;
                    }
                });
                resultsDiv.innerHTML = html;
            } catch (error) {
                resultsDiv.innerHTML = '<div class="error-item">エラーが発生しました</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.post("/shorten")
async def shorten(urls: str = Form(...)):
    url_list = [u.strip() for u in urls.split('\n') if u.strip()]
    results = []
    
    for url in url_list:
        if url.startswith(('http://', 'https://')):
            code = generate_code()
            url_db[code] = url
            results.append({
                "url": url,
                "success": True,
                "short_url": f"https://yourapp.onrender.com/s/{code}"
            })
        else:
            results.append({
                "url": url,
                "success": False
            })
    
    return JSONResponse({"results": results})

@app.get("/s/{code}")
async def redirect(code: str):
    if code in url_db:
        return RedirectResponse(url_db[code])
    return HTMLResponse("URL not found", status_code=404)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
