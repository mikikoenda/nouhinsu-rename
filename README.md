# 納品書リネームツール セットアップ手順

## 必要なもの
- GitHubアカウント（無料）
- Renderアカウント（無料）: https://render.com
- Anthropic APIキー: https://console.anthropic.com

---

## 手順

### 1. GitHubにアップロード
1. https://github.com にログイン
2. 右上の「+」→「New repository」
3. リポジトリ名を入力（例：`nouhinsu-rename`）→「Create repository」
4. 「uploading an existing file」をクリック
5. このフォルダの中身（app.py, requirements.txt, render.yaml）をすべてドラッグ＆ドロップ
6. 「Commit changes」をクリック

### 2. Renderにデプロイ
1. https://render.com にログイン（GitHubアカウントで登録可）
2. 「New +」→「Web Service」
3. GitHubのリポジトリを選択
4. 設定はそのままで「Create Web Service」
5. 「Environment」タブ →「Add Environment Variable」
   - Key: `ANTHROPIC_API_KEY`
   - Value: APIキーを貼り付け
6. 数分待つとURLが発行される（例：`https://nouhinsu-rename.onrender.com`）

### 3. 使い方
- 発行されたURLを3人で共有するだけ！
- ブラウザでPDFをドラッグ＆ドロップ → 自動でリネームしてダウンロード

---

## 費用
- GitHub：無料
- Render（無料プラン）：無料（月750時間まで）
- Anthropic API：納品書1枚あたり約0.3〜1円

## 注意
- Renderの無料プランは15分操作がないとスリープします
- 初回アクセス時に30秒ほど起動時間がかかる場合があります
- PDFはサーバーに保存されません（処理後すぐに破棄）
