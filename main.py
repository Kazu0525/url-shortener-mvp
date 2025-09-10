from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import string
import json
import os
from datetime import datetime

app = FastAPI()

# データベース（メモリ内）
url_db = {}
campaigns = {}
analytics = {}

def generate_code(length=6):
    """ランダムコード生成"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_short_url(original_url, custom_code=None, custom_name=None, campaign=None):
    """短縮URL作成"""
    code = custom_code if custom_code else generate_code()
    
    # 重複チェック
    if code in url_db:
        if custom_code:
            return None, "このコードは既に使用されています"
        else:
            # 自動生成の場合は再生成
            while code in url_db:
                code = generate_code()
    
    url_db[code] = {
        "original_url": original_url,
        "custom_name": custom_name,
        "campaign": campaign,
        "created_at": datetime.now().isoformat(),
        "clicks": 0
    }
    
    return code, None

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def home():
    return """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>一括リンク生成システム</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { 
            max-width: 1600px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 { 
            color: #2c3e50; 
            border-bottom: 4px solid #4CAF50; 
            padding-bottom: 15px; 
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .instructions { 
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 20px; 
            border-radius: 10px; 
            margin: 25px 0; 
            border-left: 5px solid #2196F3;
        }
        
        .instructions h3 {
            margin-bottom: 15px;
            color: #1976d2;
        }
        
        .instructions ol {
            margin-left: 20px;
            line-height: 1.8;
        }
        
        .action-buttons { 
            display: flex; 
            flex-wrap: wrap; 
            gap: 12px; 
            margin: 25px 0; 
            justify-content: center;
        }
        
        .btn { 
            padding: 12px 20px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 14px; 
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            min-width: 120px;
            justify-content: center;
        }
        
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .btn-add { 
            background: linear-gradient(135deg, #2196F3 0%, #1976d2 100%);
            color: white; 
        }
        
        .btn-clear { 
            background: linear-gradient(135deg, #FF9800 0%, #f57c00 100%);
            color: white; 
        }
        
        .btn-generate { 
            background: linear-gradient(135deg, #4CAF50 0%, #388e3c 100%);
            color: white; 
            font-weight: bold;
            font-size: 16px;
            padding: 15px 25px;
        }
        
        .btn-admin { 
            background: linear-gradient(135deg, #9C27B0 0%, #7b1fa2 100%);
            color: white; 
        }
        
        .spreadsheet-container { 
            margin: 25px 0; 
            overflow-x: auto; 
            border: 2px solid #e0e0e0; 
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .spreadsheet-table { 
            width: 100%; 
            border-collapse: separate;
            border-spacing: 0;
            min-width: 1200px;
        }
        
        .spreadsheet-table th { 
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white; 
            text-align: center; 
            padding: 16px 12px; 
            border-right: 1px solid #388e3c;
            font-weight: 600;
            font-size: 14px;
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
            background: white;
        }
        
        .spreadsheet-table tbody tr:hover td {
            background: #f5f5f5;
        }
        
        .spreadsheet-table input { 
            width: 100%; 
            border: 2px solid transparent; 
            padding: 10px 8px; 
            font-size: 14px;
            outline: none; 
            background: transparent;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .spreadsheet-table input:focus { 
            background: #fff3cd; 
            border-color: #ffc107;
        }
        
        .row-number { 
            background: #f8f9fa; 
            text-align: center; 
            font-weight: bold; 
            width: 70px;
            color: #495057;
            font-size: 14px;
        }
        
        .delete-btn { 
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .delete-btn:hover { 
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        }
        
        .results-section { 
            margin: 35px 0; 
            display: none; 
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .result-item { 
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            padding: 20px; 
            margin: 15px 0; 
            border-radius: 8px; 
            border-left: 5px solid #28a745;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
        }
        
        .error-item { 
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 5px solid #dc3545;
            color: #721c24;
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
        }
        
        .copy-btn { 
            background: linear-gradient(135deg, #fd7e14 0%, #f39c12 100%);
            color: white; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 6px; 
            cursor: pointer; 
            margin-left: 12px; 
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        
        .copy-btn:hover { 
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(253, 126, 20, 0.3);
        }
        
        .loading { 
            text-align: center; 
            padding: 30px; 
            background: #f8f9fa;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .spinner { 
            border: 4px solid #f3f3f3; 
            border-top: 4px solid #4CAF50; 
            border-radius: 50%; 
            width: 40px; 
            height: 40px; 
            animation: spin 1s linear infinite; 
            margin: 0 auto 20px;
        }
        
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        
        .short-url {
            background: #f0f4ff;
            padding: 10px 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
            display: inline-block;
            margin: 5px 0;
        }
        
        .summary-box {
            background: linear-gradient(135deg, #e7f3ff 0%, #cce7ff 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #2196F3;
        }
        
        @media (max-width: 768px) {
            .spreadsheet-container {
                overflow-x: scroll;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 一括リンク生成システム</h1>
        
        <div class="instructions">
            <h3>📋 使い方</h3>
            <ol>
                <li><strong>B列（必須）</strong>: 短縮したい元のURLを入力（http:// または https:// で始めてください）</li>
                <li><strong>C列（任意）</strong>: カスタム短縮コードを入力（空白の場合は自動生成）</li>
                <li><strong>D列（任意）</strong>: カスタム名を入力（管理画面で識別しやすくします）</li>
                <li><strong>E列（任意）</strong>: キャンペーン名を入力（同じキャンペーンのURLをグループ化）</li>
                <li><strong>F列（任意）</strong>: 生成数量を入力（空白の場合は1個生成）</li>
                <li><strong>「🚀 一括生成開始」</strong>ボタンをクリック</li>
            </ol>
        </div>

        <div class="action-buttons">
            <button type="button" class="btn btn-add" onclick="addRows(1)">➕ 1行追加</button>
            <button type="button" class="btn btn-add" onclick="addRows(5)">➕ 5行追加</button>
            <button type="button" class="btn btn-add" onclick="addRows(10)">➕ 10行追加</button>
            <button type="button" class="btn btn-clear" onclick="clearAllData()">🗑️ 全削除</button>
            <button type="button" class="btn btn-generate" onclick="startGeneration()">🚀 一括生成開始</button>
            <button type="button" class="btn btn-admin" onclick="window.location.href='/admin'">📊 管理画面へ</button>
        </div>

        <div class="spreadsheet-container">
            <table class="spreadsheet-table">
                <thead>
                    <tr>
                        <th style="width: 70px;">A<br>行番号</th>
                        <th style="width: 35%;">B<br>オリジナルURL ※必須</th>
                        <th style="width: 12%;">C<br>カスタム短縮コード<br>(任意)</th>
                        <th style="width: 12%;">D<br>カスタム名<br>(任意)</th>
                        <th style="width: 12%;">E<br>キャンペーン名<br>(任意)</th>
                        <th style="width: 8%;">F<br>生成数量<br>(任意)</th>
                        <th style="width: 100px;">操作</th>
                    </tr>
                </thead>
                <tbody id="dataTable">
                    <!-- 初期行 -->
                </tbody>
            </table>
        </div>

        <div class="action-buttons">
            <button type="button" class="btn btn-add" onclick="addRows(1)">➕ 1行追加</button>
            <button type="button" class="btn btn-add" onclick="addRows(5)">➕ 5行追加</button>
            <button type="button" class="btn btn-add" onclick="addRows(10)">➕ 10行追加</button>
            <button type="button" class="btn btn-clear" onclick="clearAllData()">🗑️ 全削除</button>
            <button type="button" class="btn btn-generate" onclick="startGeneration()">🚀 一括生成開始</button>
        </div>

        <div class="results-section" id="resultsArea">
            <h2>📈 生成結果</h2>
            <div id="resultsContent"></div>
        </div>
    </div>

    <script>
        // グローバル変数
        let rowCount = 0;
        const baseUrl = window.location.origin;
        
        // 初期化
        window.addEventListener('DOMContentLoaded', function() {
            // 初期行を5行追加
            addRows(5);
        });
        
        // 行追加機能
        function addRows(count) {
            const table = document.getElementById('dataTable');
            
            for (let i = 0; i < count; i++) {
                rowCount++;
                const newRow = table.insertRow();
                newRow.innerHTML = \`
                    <td class="row-number">\${rowCount}</td>
                    <td><input type="url" placeholder="https://example.com" /></td>
                    <td><input type="text" placeholder="例: product\${rowCount.toString().padStart(2, '0')}" /></td>
                    <td><input type="text" placeholder="例: 商品\${String.fromCharCode(65 + ((rowCount - 1) % 26))}" /></td>
                    <td><input type="text" placeholder="例: 春キャンペーン" /></td>
                    <td><input type="number" min="1" max="20" value="1" /></td>
                    <td><button class="delete-btn" onclick="deleteRow(this)">🗑️ 削除</button></td>
                \`;
            }
            updateRowNumbers();
        }
        
        // 行削除機能
        function deleteRow(button) {
            const table = document.getElementById('dataTable');
            if (table.rows.length > 1) {
                button.closest('tr').remove();
                updateRowNumbers();
            } else {
                alert('最低1行は必要です');
            }
        }
        
        // 行番号更新
        function updateRowNumbers() {
            const table = document.getElementById('dataTable');
            const rows = table.getElementsByTagName('tr');
            for (let i = 0; i < rows.length; i++) {
                rows[i].cells[0].textContent = i + 1;
            }
            rowCount = rows.length;
        }
        
        // 全削除機能
        function clearAllData() {
            if (confirm('全てのデータを削除しますか？')) {
                const table = document.getElementById('dataTable');
                table.innerHTML = '';
                rowCount = 0;
                addRows(1); // 最低1行追加
                document.getElementById('resultsArea').style.display = 'none';
            }
        }
        
        // 一括生成機能
        async function startGeneration() {
            const table = document.getElementById('dataTable');
            const rows = table.getElementsByTagName('tr');
            const requestData = [];
            
            // データ収集
            for (let i = 0; i < rows.length; i++) {
                const row = rows[i];
                const inputs = row.querySelectorAll('input');
                const url = inputs[0].value.trim();
                
                if (url) {
                    if (!url.startsWith('http://') && !url.startsWith('https://')) {
                        alert(\`行 \${i + 1}: URLは http:// または https:// で始めてください\`);
                        return;
                    }
                    
                    const quantity = parseInt(inputs[4].value) || 1;
                    
                    // 指定数量分だけリクエストを作成
                    for (let j = 0; j < quantity; j++) {
                        requestData.push({
                            url: url,
                            custom_code: inputs[1].value.trim() ? inputs[1].value.trim() + (quantity > 1 ? \`_\${j + 1}\` : '') : '',
                            custom_name: inputs[2].value.trim(),
                            campaign: inputs[3].value.trim()
                        });
                    }
                }
            }
            
            if (requestData.length === 0) {
                alert('少なくとも1つのURLを入力してください');
                return;
            }
            
            // 生成処理
            const generateBtns = document.querySelectorAll('.btn-generate');
            generateBtns.forEach(btn => {
                btn.disabled = true;
                btn.textContent = '⏳ 生成中...';
            });
            
            const resultsArea = document.getElementById('resultsArea');
            const resultsContent = document.getElementById('resultsContent');
            resultsArea.style.display = 'block';
            resultsContent.innerHTML = '<div class="loading"><div class="spinner"></div><p>リンクを生成しています...</p></div>';
            
            try {
                const formData = new FormData();
                formData.append('data', JSON.stringify(requestData));
                
                const response = await fetch('/api/bulk-generate', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(\`処理エラー: \${response.status}\`);
                }
                
                const result = await response.json();
                showResults(result);
                
            } catch (error) {
                resultsContent.innerHTML = \`<div class="error-item">エラーが発生しました: \${error.message}</div>\`;
            } finally {
                generateBtns.forEach(btn => {
                    btn.disabled = false;
                    btn.textContent = '🚀 一括生成開始';
                });
            }
        }
        
        // 結果表示
        function showResults(result) {
            const resultsContent = document.getElementById('resultsContent');
            let successCount = 0;
            let errorCount = 0;
            
            if (result.results) {
                result.results.forEach(item => {
                    if (item.success) successCount++;
                    else errorCount++;
                });
            }
            
            let html = \`
                <div class="summary-box">
                    <h3 style="margin: 0 0 15px 0; color: #1976d2;">📊 生成結果サマリー</h3>
                    <p style="margin: 0; font-size: 16px;">
                        成功: <strong style="color: #28a745;">\${successCount}</strong> | 
                        エラー: <strong style="color: #dc3545;">\${errorCount}</strong> | 
                        合計: <strong>\${successCount + errorCount}</strong>
                    </p>
                </div>
            \`;
            
            if (result.results) {
                result.results.forEach((item, index) => {
                    if (item.success) {
                        html += \`
                            <div class="result-item">
                                <p style="margin: 0 0 8px 0;"><strong>\${index + 1}. 元URL:</strong> \${item.url}</p>
                                \${item.custom_name ? \`<p style="margin: 0 0 8px 0;"><strong>カスタム名:</strong> \${item.custom_name}</p>\` : ''}
                                \${item.campaign ? \`<p style="margin: 0 0 8px 0;"><strong>キャンペーン:</strong> \${item.campaign}</p>\` : ''}
                                <p style="margin: 0;">
                                    <strong>短縮URL:</strong><br>
                                    <span class="short-url">\${item.short_url}</span>
                                    <button class="copy-btn" onclick="copyText('\${item.short_url}', this)">📋 コピー</button>
                                </p>
                            </div>
                        \`;
                    } else {
                        html += \`
                            <div class="error-item">
                                <p style="margin: 0;">❌ \${item.url} - \${item.error}</p>
                            </div>
                        \`;
                    }
                });
            }
            
            resultsContent.innerHTML = html;
        }
        
        // コピー機能
        function copyText(text, button) {
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = '✅ コピー完了！';
                button.style.background = 'linear-gradient(135deg, #28a745 0%, #218838 100%)';
                
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.background = '';
                }, 2000);
            }).catch(() => {
                prompt('以下のURLをコピーしてください:', text);
            });
        }
    </script>
</body>
</html>
"""

@app.post("/api/bulk-generate")
async def bulk_generate(data: str = Form(...)):
    """一括URL生成API"""
    try:
        request_data = json.loads(data)
        results = []
        
        for item in request_data:
            url = item.get('url', '').strip()
            custom_code = item.get('custom_code', '').strip()
            custom_name = item.get('custom_name', '').strip()
            campaign = item.get('campaign', '').strip()
            
            if not url:
                continue
                
            if not url.startswith(('http://', 'https://')):
                results.append({
                    "url": url,
                    "success": False,
                    "error": "無効なURL形式"
                })
                continue
            
            # 短縮URL生成
            code, error = create_short_url(
                original_url=url,
                custom_code=custom_code if custom_code else None,
                custom_name=custom_name if custom_name else None,
                campaign=campaign if campaign else None
            )
            
            if error:
                results.append({
                    "url": url,
                    "success": False,
                    "error": error
                })
            else:
                base_url = "https://url-shortener-spreadsheet.onrender.com"  # あなたのRender URLに変更
                results.append({
                    "url": url,
                    "success": True,
                    "short_url": f"{base_url}/s/{code}",
                    "short_code": code,
                    "custom_name": custom_name,
                    "campaign": campaign
                })
        
        return JSONResponse({"results": results})
        
    except Exception as e:
        return JSONResponse(
            {"error": f"処理エラー: {str(e)}"},
            status_code=400
        )

@app.get("/s/{code}")
async def redirect_url(code: str):
    """短縮URLリダイレクト"""
    if code in url_db:
        url_db[code]["clicks"] += 1
        return RedirectResponse(url_db[code]["original_url"])
    return HTMLResponse("URL not found", status_code=404)

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    """管理画面"""
    # キャンペーン別の統計
    campaign_stats = {}
    for code, data in url_db.items():
        campaign = data.get("campaign", "未分類")
        if campaign not in campaign_stats:
            campaign_stats[campaign] = {"count": 0, "clicks": 0}
        campaign_stats[campaign]["count"] += 1
        campaign_stats[campaign]["clicks"] += data["clicks"]
    
    html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理画面</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 4px solid #9C27B0;
            padding-bottom: 15px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }}
        th {{
            background: #9C27B0;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .btn-back {{
            background: linear-gradient(135deg, #4CAF50 0%, #388e3c 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }}
        .btn-back:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        .campaign-section {{
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 URL短縮サービス管理画面</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div>総URL数</div>
                <div class="stat-number">{len(url_db)}</div>
            </div>
            <div class="stat-card">
                <div>総クリック数</div>
                <div class="stat-number">{sum(url["clicks"] for url in url_db.values())}</div>
            </div>
            <div class="stat-card">
                <div>キャンペーン数</div>
                <div class="stat-number">{len(campaign_stats)}</div>
            </div>
        </div>
        
        <h2>📋 登録済みURL一覧</h2>
        <table>
            <thead>
                <tr>
                    <th>短縮コード</th>
                    <th>カスタム名</th>
                    <th>元のURL</th>
                    <th>キャンペーン</th>
                    <th>作成日時</th>
                    <th>クリック数</th>
                </tr>
            </thead>
            <tbody>"""
    
    for code, data in sorted(url_db.items(), key=lambda x: x[1]["created_at"], reverse=True):
        html += f"""
                <tr>
                    <td><code>{code}</code></td>
                    <td>{data.get('custom_name', '-')}</td>
                    <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        <a href="{data['original_url']}" target="_blank">{data['original_url']}</a>
                    </td>
                    <td>{data.get('campaign', '-')}</td>
                    <td>{data['created_at'][:19]}</td>
                    <td style="text-align: center;"><strong>{data['clicks']}</strong></td>
                </tr>"""
    
    html += """
            </tbody>
        </table>
        
        <div class="campaign-section">
            <h2>🎯 キャンペーン別統計</h2>
            <table>
                <thead>
                    <tr>
                        <th>キャンペーン名</th>
                        <th>URL数</th>
                        <th>総クリック数</th>
                        <th>平均クリック数</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for campaign, stats in sorted(campaign_stats.items(), key=lambda x: x[1]["clicks"], reverse=True):
        avg_clicks = round(stats["clicks"] / stats["count"], 1) if stats["count"] > 0 else 0
        html += f"""
                    <tr>
                        <td>{campaign}</td>
                        <td>{stats["count"]}</td>
                        <td>{stats["clicks"]}</td>
                        <td>{avg_clicks}</td>
                    </tr>"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <a href="/" class="btn-back">🏠 ホームに戻る</a>
    </div>
</body>
</html>
    """
    
    return HTMLResponse(content=html)

@app.get("/health")
async def health():
    return {"status": "healthy", "urls": len(url_db)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
