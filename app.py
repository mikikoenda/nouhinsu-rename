from flask import Flask, request, jsonify, send_file, render_template_string
import base64
import json
import re
import os
import io
import traceback
import urllib.request
import urllib.error
import urllib.parse
from datetime import date

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>納品書リネームツール</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0f0f0f;
    --surface: #1a1a1a;
    --surface2: #242424;
    --border: #2e2e2e;
    --accent: #c8a96e;
    --accent2: #e8c98e;
    --text: #e8e8e8;
    --text-muted: #888;
    --success: #5a9e6f;
    --error: #c05a5a;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Noto Sans JP', sans-serif;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 24px;
  }

  header {
    text-align: center;
    margin-bottom: 48px;
  }

  .logo-mark {
    display: inline-block;
    width: 48px;
    height: 48px;
    border: 2px solid var(--accent);
    transform: rotate(45deg);
    margin-bottom: 20px;
    position: relative;
  }
  .logo-mark::after {
    content: '';
    position: absolute;
    inset: 6px;
    border: 1px solid var(--accent);
  }

  h1 {
    font-size: 1.4rem;
    font-weight: 300;
    letter-spacing: 0.2em;
    color: var(--accent2);
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 0.8rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 2px;
    width: 100%;
    max-width: 640px;
    padding: 32px;
    margin-bottom: 16px;
  }

  .drop-zone {
    border: 1.5px dashed var(--border);
    border-radius: 2px;
    padding: 48px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }

  .drop-zone:hover, .drop-zone.dragover {
    border-color: var(--accent);
    background: rgba(200,169,110,0.04);
  }

  .drop-zone input[type="file"] {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
    width: 100%;
    height: 100%;
  }

  .drop-icon {
    font-size: 2rem;
    margin-bottom: 12px;
    opacity: 0.5;
  }

  .drop-text {
    font-size: 0.9rem;
    color: var(--text-muted);
    line-height: 1.6;
  }

  .drop-text strong {
    color: var(--accent);
    font-weight: 500;
  }

  .file-list {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .file-item {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.85rem;
  }

  .file-item .file-name {
    flex: 1;
    color: var(--text-muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
  }

  .file-item .status {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 1px;
  }

  .status.pending { color: var(--text-muted); border: 1px solid var(--border); }
  .status.processing { color: var(--accent); border: 1px solid var(--accent); animation: pulse 1s infinite; }
  .status.done { color: var(--success); border: 1px solid var(--success); }
  .status.error { color: var(--error); border: 1px solid var(--error); }

  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

  .result-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--accent2);
    margin-top: 4px;
  }

  .file-item-inner { flex: 1; min-width: 0; }

  .btn {
    width: 100%;
    padding: 14px;
    background: var(--accent);
    color: #0f0f0f;
    border: none;
    border-radius: 2px;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 20px;
  }

  .btn:hover { background: var(--accent2); }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .download-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: transparent;
    border: 1px solid var(--success);
    color: var(--success);
    border-radius: 1px;
    font-size: 0.75rem;
    cursor: pointer;
    text-decoration: none;
    font-family: 'Noto Sans JP', sans-serif;
    transition: all 0.2s;
  }
  .download-btn:hover { background: var(--success); color: #0f0f0f; }

  .rule-box {
    background: var(--surface2);
    border-left: 2px solid var(--accent);
    padding: 12px 16px;
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.8;
    font-family: 'DM Mono', monospace;
  }

  .rule-box .rule-title {
    color: var(--accent);
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    margin-bottom: 6px;
  }

  footer {
    margin-top: 32px;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-align: center;
    line-height: 1.8;
  }
</style>
</head>
<body>

<header>
  <div class="logo-mark"></div>
  <h1>納品書リネームツール</h1>
  <p class="subtitle">PDFをドロップするだけで自動リネーム</p>
</header>

<div class="card">
  <div class="rule-box">
    <div class="rule-title">ファイル名ルール</div>
    納入先あり：日付_納品書_得意先_納品先.pdf<br>
    納入先なし：日付_納品書_得意先.pdf
  </div>

  <div class="drop-zone" id="dropZone">
    <input type="file" id="fileInput" accept=".pdf" multiple>
    <div class="drop-icon">📄</div>
    <div class="drop-text">
      <strong>クリックまたはドラッグ＆ドロップ</strong><br>
      PDFファイルを選択（複数可）
    </div>
  </div>

  <div class="file-list" id="fileList"></div>

  <button class="btn" id="processBtn" disabled onclick="processAll()">
    リネーム開始
  </button>
</div>

<footer>
  株式会社中川ワイン 納品書管理ツール<br>
  ファイルはサーバーに保存されません
</footer>

<script>
  const files = [];

  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');
  const processBtn = document.getElementById('processBtn');

  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    addFiles([...e.dataTransfer.files]);
  });
  fileInput.addEventListener('change', () => addFiles([...fileInput.files]));

  function addFiles(newFiles) {
    newFiles.filter(f => f.name.endsWith('.pdf')).forEach(f => {
      files.push({ file: f, status: 'pending', result: null, blob: null });
    });
    renderList();
    processBtn.disabled = files.length === 0;
  }

  function renderList() {
    fileList.innerHTML = files.map((f, i) => `
      <div class="file-item" id="item-${i}">
        <div class="file-item-inner">
          <div class="file-name">${f.file.name}</div>
          ${f.result ? `<div class="result-name">→ ${f.result}</div>` : ''}
        </div>
        <span class="status ${f.status}">${statusLabel(f.status)}</span>
        ${f.blob ? `<a class="download-btn" onclick="downloadFile(${i})">↓ 保存</a>` : ''}
      </div>
    `).join('');
  }

  function statusLabel(s) {
    return { pending: '待機中', processing: '処理中...', done: '完了', error: 'エラー' }[s];
  }

  function downloadFile(i) {
    const f = files[i];
    const a = document.createElement('a');
    a.href = URL.createObjectURL(f.blob);
    a.download = f.result;
    a.click();
  }

  async function processAll() {
    processBtn.disabled = true;
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'pending') continue;
      files[i].status = 'processing';
      renderList();
      try {
        const formData = new FormData();
        formData.append('pdf', files[i].file);
        const res = await fetch('/rename', { method: 'POST', body: formData });
        if (!res.ok) throw new Error(await res.text());
        const blob = await res.blob();
        const filename = decodeURIComponent(res.headers.get('X-Filename'));
        files[i].blob = blob;
        files[i].result = filename;
        files[i].status = 'done';
      } catch (e) {
        files[i].status = 'error';
        files[i].result = e.message;
      }
      renderList();
    }
  }
</script>
</body>
</html>
"""

def extract_info(pdf_bytes: bytes) -> dict:
    pdf_base64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    prompt = """この納品書PDFから以下の情報をJSON形式で抽出してください。

抽出ルール:
1. 「得意先」: 「御中」の前にある宛先会社名。「株式会社」「有限会社」「合同会社」などの法人格は省略してください。
2. 「納品先」: 「納入先：」の後に書かれている会社名。「株式会社」「有限会社」「合同会社」などの法人格は省略してください。「納入先：」の記載がない場合は空文字列 "" を返してください。
3. 「日付」: 伝票の日付欄にある日付をYYYYMMDD形式で返してください。日付欄がなければ今日の日付を使ってください。

必ずこの形式のJSONのみを返してください（説明文は不要）:
{"得意先": "会社名", "納品先": "会社名または空文字", "日付": "YYYYMMDD"}"""

    payload = json.dumps({
        "model": "claude-opus-4-5",
        "max_tokens": 256,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_base64}},
                {"type": "text", "text": prompt}
            ]
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        text = result["content"][0]["text"].strip()
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        return json.loads(match.group())


def build_filename(info: dict) -> str:
    def clean(s):
        return re.sub(r'[\\/:*?"<>|]', "", s).strip()

    date_str = clean(info.get("日付", date.today().strftime("%Y%m%d")))
    tokui = clean(info.get("得意先", "不明"))
    nouhin = clean(info.get("納品先", ""))

    if nouhin:
        return f"{date_str}_納品書_{tokui}_{nouhin}.pdf"
    else:
        return f"{date_str}_納品書_{tokui}.pdf"


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/rename", methods=["POST"])
def rename():
    if "pdf" not in request.files:
        return "PDFが見つかりません", 400

    pdf_file = request.files["pdf"]
    pdf_bytes = pdf_file.read()

    try:
        info = extract_info(pdf_bytes)
        filename = build_filename(info)
    except Exception as e:
        traceback.print_exc()
        return str(e), 500

    response = send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
    response.headers["X-Filename"] = urllib.parse.quote(filename)
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
