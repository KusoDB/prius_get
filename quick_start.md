# ⚡ クイックスタート - 5分で無料クラウド監視開始

## 🎯 目標
GitHubにプッシュするだけで、プリウス監視システムを無料で24時間365日稼働

## 📋 必要なもの
- GitHubアカウント（無料）
- Slackワークスペース（オプション、推奨）

## 🚀 5分セットアップ

### Step 1: GitHubリポジトリ作成 (1分)
```bash
# プロジェクトディレクトリで実行
git init
git add .
git commit -m "🚗 プリウス監視システム"

# GitHubで新しいパブリックリポジトリ作成後
git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git
git branch -M main
git push -u origin main
```

### Step 2: Slack設定 (2分) **※推奨**
1. [api.slack.com/apps](https://api.slack.com/apps) で「Create New App」
2. 「From scratch」→ アプリ名「プリウス監視」→ ワークスペース選択
3. 左メニュー「Incoming Webhooks」→ 「Activate Incoming Webhooks」をON
4. 「Add New Webhook to Workspace」→ チャンネル選択 → 「Allow」
5. Webhook URLをコピー（`https://hooks.slack.com/services/...`）

### Step 3: GitHub Secrets設定 (1分)
GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」で追加:

**New repository secret:**
- Name: `SLACK_WEBHOOK_URL`
- Secret: （Step 2でコピーしたURL）

### Step 4: 監視開始 (1分)
- ファイルプッシュで自動開始
- 「Actions」タブで実行確認
- 30分ごとに自動実行

## ✅ 動作確認

### 即座にテスト実行
1. GitHubリポジトリの「Actions」タブ
2. 「プリウス監視システム」ワークフロー選択
3. 「Run workflow」ボタンクリック
4. 数分後にSlackに結果通知

### 初回実行で期待される結果
```
🤖 プリウス監視システム実行完了
⏰ 2025-08-03 09:15:30 (UTC)
📊 監視中の車両: 4台

• プリウス A ツーリング 4WD - 145万円
• プリウス S 4WD - 143.8万円  
• プリウス A - 143万円
• プリウス S セーフティープラス - 137.8万円
```

## 🎉 完了！

これで以下が自動化されました:
- ✅ 30分ごとの車両チェック
- ✅ 新着プリウス発見時の即座通知
- ✅ データの自動保存
- ✅ 実行ログの記録

## 📱 新着通知の例
新しいプリウスが見つかると、Slackにこんな通知が届きます:

```
🚗 プリウス新着車両発見！

• プリウス A ツーリング 4WD 🆕
  💰 142万円

🔗 検索結果を見る
⏰ 2025-08-03 12:30:15 (UTC)
```

## ⚙️ カスタマイズ

### 条件変更
`cloud_monitor.py` の先頭を編集:
```python
YEAR_FROM = "2018"    # 年式を2018年以降に変更
MAX_PRICE = "200"     # 価格上限を200万円に変更
```

### チェック間隔変更
`.github/workflows/prius-monitor.yml` の19行目:
```yaml
- cron: '*/15 * * * *'  # 15分ごとに変更
```

## 🆘 トラブルシューティング

### Q: 通知が来ない
**A:** GitHub SecretsでSLACK_WEBHOOK_URLが正しく設定されているか確認

### Q: 実行エラーが発生
**A:** GitHubの「Actions」タブでログを確認。エラー内容をSlackに自動通知

### Q: 料金は本当に無料？
**A:** パブリックリポジトリなら完全無料。プライベートでも月2000分まで無料

---

**これで理想のプリウスを見逃すことはありません！** 🎯

新着車両があれば即座にSlack通知が届き、すぐに確認・問い合わせできます。