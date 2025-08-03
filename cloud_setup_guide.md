# 🌐 無料クラウド定期実行セットアップガイド

プリウス監視システムを無料のクラウドサービスで24時間365日動作させる方法

## 🚀 推奨: GitHub Actions（完全無料）

### メリット
- ✅ **完全無料** - パブリックリポジトリなら無制限
- ✅ **簡単セットアップ** - 数分で完了
- ✅ **安定性抜群** - GitHubの堅牢なインフラ
- ✅ **ログ保存** - 実行結果を自動保存
- ✅ **データ永続化** - GitHubリポジトリに自動保存

### セットアップ手順

#### 1. GitHubリポジトリ作成
```bash
# ローカルでGitリポジトリ初期化
git init
git add .
git commit -m "🚗 プリウス監視システム初期設定"

# GitHubで新しいリポジトリ作成後
git remote add origin https://github.com/あなたのユーザー名/prius-monitor.git
git branch -M main
git push -u origin main
```

#### 2. Slack Webhook URL取得（推奨）
1. [Slack API](https://api.slack.com/apps) でアプリ作成
2. "Incoming Webhooks" を有効化
3. ワークスペースに追加してWebhook URLをコピー

#### 3. GitHub Secrets設定
GitHubリポジトリの `Settings > Secrets and variables > Actions` で設定:

**必須（Slack通知用）:**
- `SLACK_WEBHOOK_URL`: `https://hooks.slack.com/services/...`

**オプション（メール通知用）:**
- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `EMAIL_USER`: `your-email@gmail.com`
- `EMAIL_PASSWORD`: `アプリパスワード`
- `TO_EMAIL`: `notification@example.com`

#### 4. 監視開始
- ファイルをプッシュすると自動で30分ごとに実行開始
- `Actions` タブで実行状況を確認可能
- 手動実行も `Run workflow` ボタンで可能

## 💰 料金について

### GitHub Actions（推奨）
- **パブリックリポジトリ**: 完全無料・無制限
- **プライベートリポジトリ**: 月2000分無料（プリウス監視なら十分）

### 実行時間計算
- 1回の実行: 約2-3分
- 30分間隔: 1日48回実行
- 月間使用時間: 約144分（無料枠内）

## 🔧 その他の無料オプション

### 2. Render.com（Web Service）
```bash
# render.yaml設定ファイル作成済み
# Render.comでリポジトリを接続するだけ
```
- 月750時間無料
- 自動デプロイ
- 環境変数設定UI

### 3. Railway（コンテナ）
- 月500時間＋5GBストレージ無料
- Dockerコンテナ対応
- データベース連携可能

### 4. Vercel（Serverless Functions）
- 月100GBの実行無料
- Edge Functionsで高速実行
- 自動スケーリング

## 📊 各サービス比較

| サービス | 無料枠 | セットアップ | データ永続化 | 推奨度 |
|---------|-------|------------|-------------|-------|
| **GitHub Actions** | 2000分/月 | ⭐⭐⭐ | ✅ Git | ⭐⭐⭐⭐⭐ |
| Render.com | 750時間/月 | ⭐⭐ | ❌ | ⭐⭐⭐ |
| Railway | 500時間/月 | ⭐⭐ | ✅ DB | ⭐⭐⭐ |
| Vercel | 100GB実行/月 | ⭐ | ❌ | ⭐⭐ |

## 🚨 注意事項

### 利用規約遵守
- 適切な間隔でのアクセス（30分間隔推奨）
- User-Agentの設定
- 過度なリクエストを避ける

### トラブルシューティング
1. **車両が検出されない**
   - GitHubのActionsログを確認
   - サイト構造の変更可能性

2. **通知が来ない**
   - Slack Webhook URLの確認
   - GitHub Secretsの設定確認

3. **実行時間超過**
   - チェック間隔を延長（60分など）
   - 不要な待機時間を削減

## 🎯 セットアップ完了後

1. **動作確認**
   - GitHubの `Actions` タブで実行ログ確認
   - Slackに通知が届くかテスト

2. **カスタマイズ**
   - 条件変更: `cloud_monitor.py` の設定値変更
   - 間隔変更: `.github/workflows/prius-monitor.yml` のcron設定変更

3. **監視開始**
   - システムが自動で24時間365日動作
   - 新着プリウスがあれば即座に通知

---

**これで完全無料でプリウス監視システムがクラウドで動作します！** 🎉

GitHubにプッシュするだけで、理想のプリウスを見逃すことなく監視できます。