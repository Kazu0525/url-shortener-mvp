from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import string
import random
import sqlite3
from datetime import datetime

app = FastAPI()

# Database and utility functions (minimal required)
def get_db_connection():
    conn = sqlite3.connect("url_shortener.db")
    conn.row_factory = sqlite3.Row
    return conn

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for _ in range(50):
        code = ''.join(random.choices(chars, k=length))
        cursor.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code
    
    conn.close()
    raise HTTPException(status_code=500, detail="短縮コード生成に失敗しました")

def validate_url(url):
    return url.startswith(('http://', 'https://'))

# Enhanced Bulk Generation HTML with Green Table Design
BULK_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>一括リンク生成 - LinkTracker Pro</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px; 
            font-weight: 300; 
        }
        .header p { 
            font-size: 1.2em; 
            opacity: 0.9; 
        }
        .content {
            padding: 40px;
        }
        .instructions { 
            background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
            padding: 25px; 
            border-radius: 10px; 
            margin-bottom: 30px;
            border-left: 5px solid #28a745;
        }
        .instructions h3 { 
            color: #2e7d32; 
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .instructions ol { 
            margin-left: 20px; 
            color: #388e3c;
        }
        .instructions li { 
            margin-bottom: 8px; 
            line-height: 1.6;
        }
        .action-buttons { 
            text-align: center; 
            margin: 30px 0;
        }
        .btn { 
            padding: 12px 24px; 
            margin: 5px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn-primary { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; }
        .btn-secondary { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); color: white; }
        .btn-danger { background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; }
        
        /* Enhanced Spreadsheet Table */
        .spreadsheet-container { 
            margin: 30px 0; 
            border: 3px solid #28a745;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.15);
        }
        .spreadsheet-table { 
            width: 100%; 
            border-collapse: collapse; 
            font-size: 14px;
            background: white;
        }
        .spreadsheet-table th { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white; 
            padding: 15px 10px;
            text-align: center; 
            font-weight: 600;
            font-size: 13px;
            border-right: 1px solid rgba(255,255,255,0.2);
            position: sticky; 
            top: 0;
            z-index: 10;
        }
        .spreadsheet-table th:last-child {
            border-right: none;
        }
        .spreadsheet-table td { 
            border: 1px solid #e0e0e0; 
            padding: 8px;
            vertical-align: middle;
        }
        .spreadsheet-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        .spreadsheet-table tr:hover {
            background: #e8f5e9;
        }
        
        /* Column Widths */
        .row-number { 
            width: 60px; 
            text-align: center; 
            font-weight: bold;
            background: #f8f9fa !important;
            color: #495057;
        }
        .url-column { width: 45%; }
        .custom-code-column { width: 12%; }
        .custom-name-column { width: 12%; }
        .campaign-column { width: 12%; }
        .quantity-column { 
            width: 8%; 
            text-align: center; 
        }
        .action-column { width: 10%; text-align: center; }
        
        /* Input Styling */
        .spreadsheet-table input, .spreadsheet-table select { 
            width: 100%; 
            border: 2px solid #e9ecef; 
            padding: 8px 10px; 
            border-radius: 6px;
            font-size: 13px;
            transition: all 0.3s ease;
        }
        .spreadsheet-table input:focus, .spreadsheet-table select:focus { 
            border-color: #28a745; 
            outline: none; 
            box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1);
        }
        .url-input {
            font-family: monospace;
        }
        .required { 
            border-left: 4px solid #dc3545 !important; 
        }
        .quantity-input {
            text-align: center;
            font-weight: 600;
        }
        
        /* Action Button */
        .delete-row-btn { 
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white; 
            border: none; 
            padding: 6px 12px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .delete-row-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 3px 10px rgba(220, 53, 69, 0.3);
        }
        
        /* Results Section */
        .results-section { 
            margin: 40px 0;
            border-top: 3px solid #28a745;
            padding-top: 30px;
        }
        .results-section h2 {
            color: #28a745;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        .result-item { 
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 10px; 
            border-left: 5px solid #28a745;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .error-item { 
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 5px solid #dc3545; 
        }
        .copy-btn { 
            background: linear-gradient(135deg, #fd7e14 0%, #e55100 100%);
            color: white; 
            border: none; 
            padding: 6px 12px; 
            border-radius: 5px; 
            cursor: pointer; 
            margin-left: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .copy-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 8px rgba(253, 126, 20, 0.3);
        }
        .stats-link { 
            color: #1976d2; 
            text-decoration: none; 
            font-weight: bold; 
            margin-left: 10px;
        }
        .stats-link:hover { 
            text-decoration: underline; 
        }
        
        /* Loading Animation */
        .loading { 
            text-align: center; 
            padding: 30px; 
        }
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #28a745; 
            border-radius: 50%; 
            width: 50px; 
            height: 50px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 20px;
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        
        /* Responsive Design */
        @media (max-width: 1400px) {
            .spreadsheet-container {
                overflow-x: auto;
            }
            .spreadsheet-table {
                min-width: 1200px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 一括リンク生成システム</h1>
            <p>効率的なURL短縮・管理プラットフォーム</p>
        </div>
        
        <div class="content">
            <div class="instructions">
                <h3>📋 操作ガイド</h3>
                <ol>
                    <li><strong>B列（オリジナルURL）</strong>: 短縮したい元のURLを入力してください（http:// または https:// で始めること）</li>
                    <li><strong>C列（カスタム短縮コード）</strong>: お好みの短縮コードを入力（空白の場合は自動生成されます）</li>
                    <li><strong>D列（カスタム名）</strong>: 管理しやすい名前を入力してください</li>
                    <li><strong>E列（キャンペーン名）</strong>: マーケティングキャンペーンのグループ名を入力</li>
                    <li><strong>F列（生成数量）</strong>: 同じURLから複数の短縮リンクを生成する場合の数量</li>
                    <li><strong>「🚀 一括生成開始」</strong>ボタンをクリックして処理を実行</li>
                </ol>
            </div>

            <div class="action-buttons">
                <button class="btn btn-secondary" id="addRowBtn">➕ 1行追加</button>
                <button class="btn btn-secondary" id="add5RowsBtn">➕ 5行追加</button>
                <button class="btn btn-secondary" id="add10RowsBtn">➕ 10行追加</button>
                <button class="btn btn-warning" id="clearAllBtn">🗑️ 全クリア</button>
                <button class="btn btn-danger" id="generateBtn">🚀 一括生成開始</button>
            </div>

            <div class="spreadsheet-container">
                <table class="spreadsheet-table" id="spreadsheetTable">
                    <thead>
                        <tr>
                            <th class="row-number">A<br>行番号</th>
                            <th class="url-column">B<br>オリジナルURL ※必須</th>
                            <th class="custom-code-column">C<br>カスタム短縮コード<br>（任意）</th>
                            <th class="custom-name-column">D<br>カスタム名<br>（任意）</th>
                            <th class="campaign-column">E<br>キャンペーン名<br>（任意）</th>
                            <th class="quantity-column">F<br>生成数量<br>（任意）</th>
                            <th class="action-column">操作</th>
                        </tr>
                    </thead>
                    <tbody id="spreadsheetBody">
                        <tr>
                            <td class="row-number">1</td>
                            <td><input type="url" class="required url-input" placeholder="https://example.com" required /></td>
                            <td><input type="text" placeholder="product01" /></td>
                            <td><input type="text" placeholder="商品A" /></td>
                            <td><input type="text" placeholder="春キャンペーン" /></td>
                            <td><input type="number" min="1" max="20" value="1" class="quantity-input" /></td>
                            <td><button class="delete-row-btn" onclick="removeRow(this)">🗑️ 削除</button></td>
                        </tr>
                        <tr>
                            <td class="row-number">2</td>
                            <td><input type="url" class="required url-input" placeholder="https://example2.com" required /></td>
                            <td><input type="text" placeholder="product02" /></td>
                            <td><input type="text" placeholder="商品B" /></td>
                            <td><input type="text" placeholder="夏キャンペーン" /></td>
                            <td><input type="number" min="1" max="20" value="1" class="quantity-input" /></td>
                            <td><button class="delete-row-btn" onclick="removeRow(this)">🗑️ 削除</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="action-buttons">
                <button class="btn btn-secondary" id="addRowBtn2">➕ 1行追加</button>
                <button class="btn btn-secondary" id="add5RowsBtn2">➕ 5行追加</button>
                <button class="btn btn-secondary" id="add10RowsBtn2">➕ 10行追加</button>
                <button class="btn btn-warning" id="clearAllBtn2">🗑️ 全クリア</button>
                <button class="btn btn-danger" id="generateBtn2">🚀 一括生成開始</button>
                <button class="btn btn-primary" onclick="window.location.href='/admin'">📊 管理画面へ</button>
            </div>

            <div class="results-section" id="resultsSection" style="display: none;">
                <h2>📈 生成結果</h2>
                <div id="resultsContent"></div>
            </div>
        </div>
    </div>

    <script>
        let rowCounter = 2;
        
        function addRow() {
            rowCounter++;
            const tbody = document.getElementById('spreadsheetBody');
            const newRow = tbody.insertRow();
            newRow.innerHTML = `
                <td class="row-number">${rowCounter}</td>
                <td><input type="url" class="required url-input" placeholder="https://example${rowCounter}.com" required /></td>
                <td><input type="text" placeholder="product${rowCounter.toString().padStart(2, '0')}" /></td>
                <td><input type="text" placeholder="商品${String.fromCharCode(64 + rowCounter)}" /></td>
                <td><input type="text" placeholder="キャンペーン${rowCounter}" /></td>
                <td><input type="number" min="1" max="20" value="1" class="quantity-input" /></td>
                <td><button class="delete-row-btn" onclick="removeRow(this)">🗑️ 削除</button></td>
            `;
            updateRowNumbers();
        }
        
        function addMultipleRows(count) {
            for (let i = 0; i < count; i++) {
                addRow();
            }
        }
        
        function removeRow(button) {
            const tbody = document.getElementById('spreadsheetBody');
            if (tbody.rows.length > 1) {
                button.closest('tr').remove();
                updateRowNumbers();
            } else {
                alert('最低1行は必要です');
            }
        }
        
        function updateRowNumbers() {
            const rows = document.querySelectorAll('#spreadsheetBody tr');
            rows.forEach((row, index) => {
                row.cells[0].textContent = index + 1;
            });
            rowCounter = rows.length;
        }
        
        function clearAll() {
            if (confirm('全てのデータを削除しますか？')) {
                document.getElementById('spreadsheetBody').innerHTML = `
                    <tr>
                        <td class="row-number">1</td>
                        <td><input type="url" class="required url-input" placeholder="https://example.com" required /></td>
                        <td><input type="text" placeholder="product01" /></td>
                        <td><input type="text" placeholder="商品A" /></td>
                        <td><input type="text" placeholder="春キャンペーン" /></td>
                        <td><input type="number" min="1" max="20" value="1" class="quantity-input" /></td>
                        <td><button class="delete-row-btn" onclick="removeRow(this)">🗑️ 削除</button></td>
                    </tr>
                `;
                rowCounter = 1;
                document.getElementById('resultsSection').style.display = 'none';
            }
        }
        
        function validateAndGenerate() {
            const rows = document.querySelectorAll('#spreadsheetBody tr');
            const data = [];
            let hasError = false;
            
            for (let row of rows) {
                const inputs = row.querySelectorAll('input');
                const originalUrl = inputs[0].value.trim();
                const customSlug = inputs[1].value.trim();
                const customName = inputs[2].value.trim();
                const campaignName = inputs[3].value.trim();
                const quantity = parseInt(inputs[4].value) || 1;
                
                if (originalUrl) {
                    if (!originalUrl.startsWith('http://') && !originalUrl.startsWith('https://')) {
                        alert('URLは http:// または https:// で始めてください');
                        inputs[0].focus();
                        hasError = true;
                        break;
                    }
                    
                    for (let i = 0; i < quantity; i++) {
                        let finalCustomSlug = customSlug;
                        let finalCustomName = customName;
                        
                        if (quantity > 1) {
                            if (customSlug) finalCustomSlug = customSlug + '_' + (i+1);
                            if (customName) finalCustomName = customName + '_' + (i+1);
                        }
                        
                        data.push({
                            url: originalUrl,
                            custom_name: finalCustomName || null,
                            campaign_name: campaignName || null
                        });
                    }
                }
            }
            
            if (hasError) return;
            
            if (data.length === 0) {
                alert('少なくとも1つのURLを入力してください');
                return;
            }
            
            if (data.length > 100) {
                if (!confirm('一度に ' + data.length + ' 個のURLを生成します。よろしいですか？')) {
                    return;
                }
            }
            
            generateLinks(data);
        }
        
        async function generateLinks(data) {
            const btn = document.getElementById('generateBtn');
            const btn2 = document.getElementById('generateBtn2');
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            
            [btn, btn2].forEach(button => {
                button.disabled = true;
                button.innerHTML = '⏳ 生成中...';
            });
            
            resultsSection.style.display = 'block';
            resultsContent.innerHTML = '<div class="loading"><div class="spinner"></div><p>リンクを生成しています...</p></div>';
            
            try {
                const formData = new FormData();
                const urlList = data.map(item => item.url).join('\\n');
                formData.append('urls', urlList);
                
                const response = await fetch('/api/bulk-process', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                resultsContent.innerHTML = `<div class="error-item">エラー: ${error.message}</div>`;
            } finally {
                [btn, btn2].forEach(button => {
                    button.disabled = false;
                    button.innerHTML = '🚀 一括生成開始';
                });
            }
        }
        
        function displayResults(result) {
            const resultsContent = document.getElementById('resultsContent');
            
            let successCount = 0;
            let errorCount = 0;
            
            if (result.results) {
                result.results.forEach(item => {
                    if (item.success) successCount++;
                    else errorCount++;
                });
            }
            
            let html = `
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #e8eaf6 100%); padding: 20px; border-radius: 10px; margin-bottom: 25px; border-left: 5px solid #1976d2;">
                    <h3>📊 生成サマリー</h3>
                    <p style="font-size: 1.1em; margin-top: 10px;">成功: <strong style="color: #28a745;">${successCount}</strong> | エラー: <strong style="color: #dc3545;">${errorCount}</strong> | 総生成数: <strong>${successCount + errorCount}</strong></p>
                </div>
            `;
            
            if (result.results && result.results.length > 0) {
                html += '<h3 style="color: #28a745; margin-bottom: 20px;">✅ 生成成功</h3>';
                result.results.forEach((item, index) => {
                    if (item.success) {
                        html += `
                            <div class="result-item">
                                <p><strong>${index + 1}. 元URL:</strong> <a href="${item.url}" target="_blank">${item.url}</a></p>
                                <p><strong>短縮URL:</strong> 
                                    <a href="${item.short_url}" target="_blank" style="color: #1976d2; font-weight: bold;">${item.short_url}</a>
                                    <button class="copy-btn" onclick="copyToClipboard('${item.short_url}')">📋 コピー</button>
                                    <a href="/analytics/${item.short_url.split('/').pop()}" target="_blank" class="stats-link">📈 分析</a>
                                </p>
                            </div>
                        `;
                    }
                });
                
                const errors = result.results.filter(item => !item.success);
                if (errors.length > 0) {
                    html += '<h3 style="color: #dc3545; margin: 30px 0 20px;">❌ エラー</h3>';
                    errors.forEach(item => {
                        html += `<div class="error-item"><strong>URL:</strong> ${item.url}<br><strong>エラー:</strong> ${item.error}</div>`;
                    });
                }
            }
            
            resultsContent.innerHTML = html;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('クリップボードにコピーしました: ' + text);
            });
        }
        
        // Event Listeners
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('addRowBtn').addEventListener('click', addRow);
            document.getElementById('add5RowsBtn').addEventListener('click', () => addMultipleRows(5));
            document.getElementById('add10RowsBtn').addEventListener('click', () => addMultipleRows(10));
            document.getElementById('clearAllBtn').addEventListener('click', clearAll);
            document.getElementById('generateBtn').addEventListener('click', validateAndGenerate);
            
            document.getElementById('addRowBtn2').addEventListener('click', addRow);
            document.getElementById('add5RowsBtn2').addEventListener('click', () => addMultipleRows(5));
            document.getElementById('add10RowsBtn2').addEventListener('click', () => addMultipleRows(10));
            document.getElementById('clearAllBtn2').addEventListener('click', clearAll);
            document.getElementById('generateBtn2').addEventListener('click', validateAndGenerate);
            
            // Initialize with additional rows
            addMultipleRows(3);
        });
    </script>
</body>
</html>
"""

@app.get("/bulk", response_class=HTMLResponse)
async def bulk_page():
    return HTMLResponse(content=BULK_HTML)

@app.post("/api/bulk-process")
async def bulk_process(urls: str = Form(...)):
    try:
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        results = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for url in url_list:
            if validate_url(url):
                short_code = generate_short_code()
                
                cursor.execute("""
                    INSERT INTO urls (short_code, original_url, created_at)
                    VALUES (?, ?, ?)
                """, (short_code, url, datetime.now().isoformat()))
                
                results.append({
                    "url": url,
                    "short_url": f"https://url-shortener-mvp.onrender.com/{short_code}",
                    "success": True
                })
            else:
                results.append({"url": url, "success": False, "error": "無効なURL"})
        
        conn.commit()
        conn.close()
        
        return JSONResponse({"results": results})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
