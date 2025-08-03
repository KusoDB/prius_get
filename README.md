# プリウス中古車監視システム

トヨタ認定中古車サイトを定期的に監視し、条件に合うプリウスの新着車両を自動検出・通知するシステム

## 🎯 監視条件

- **車種**: プリウス
- **年式**: 2019年以降
- **駆動方式**: 4WD/e-Four
- **価格**: 160万円以下

## 🚀 使用方法

### 1. 初回セットアップ

```bash
# 依存関係のインストール
pip install playwright beautifulsoup4 python-dotenv requests

# Playwrightブラウザのインストール
playwright install chromium
```

### 2. 通知設定（オプション）

`.env`ファイルを作成して通知設定を追加：

```bash
# Slack通知（推奨）
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# メール通知（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
TO_EMAIL=notification@example.com
```

### 3. 監視開始

#### ワンショット実行（テスト用）
```bash
python test_monitor.py
```

#### 継続監視（30分間隔）
```bash
python prius_monitor.py
```

#### バックグラウンド実行
```bash
nohup python prius_monitor.py > monitor.out 2>&1 &
```

#### Cron設定（推奨）
```bash
# crontab -e で設定
# 30分ごとにチェック
*/30 * * * * cd /path/to/project && python3 prius_monitor.py --single-check
```

## 📁 ファイル構成

```
project/
├── prius_monitor.py      # メイン監視スクリプト
├── test_monitor.py       # テスト実行用
├── setup_notifications.py # 通知設定ヘルパー
├── .env                  # 環境変数設定
├── data/
│   ├── vehicles.json     # 検出済み車両データ
│   └── monitor.log       # 監視ログ
└── README.md            # このファイル
```

## 🔔 通知機能

### デスクトップ通知 (macOS)
- 新着車両発見時に即座にデスクトップ通知
- 通知設定不要で利用可能

### Slack通知
- Webhook URLを設定することで利用可能
- 車両情報を整形して送信
- 検索結果ページへのリンク付き

### メール通知
- SMTP設定で利用可能
- Gmail等のアプリパスワード推奨

## 📊 監視システムの仕組み

1. **車両データ取得**: Playwrightでサイトにアクセス
2. **新着判定**: 過去検出車両と比較してユニークIDで判定
3. **データ永続化**: JSON形式で既知車両を保存
4. **通知送信**: 複数チャネルで同時通知
5. **ログ記録**: 全活動をタイムスタンプ付きで記録

## ⚙️ 設定変更

`prius_monitor.py`の先頭で条件を変更可能：

```python
YEAR_FROM = "2019"        # 年式
MAX_PRICE = "160"         # 価格上限（万円）
DRIVE_TYPE = "2"          # 駆動方式（2=4WD）
CHECK_INTERVAL_MINUTES = 30  # チェック間隔（分）
```

## 🐛 トラブルシューティング

### 車両が検出されない
- `data/monitor.log`でログを確認
- ネットワーク接続を確認
- サイト構造変更の可能性

### 通知が来ない
- `.env`ファイルの設定を確認
- Slack Webhook URLの有効性を確認
- デスクトップ通知権限を確認

### 重複通知
- `data/vehicles.json`を削除してリセット

## 📈 検出実績

初回テスト結果（2025-08-03）:
- ✅ プリウス A ツーリング 4WD - 145万円
- ✅ プリウス S 4WD - 143.8万円  
- ✅ プリウス A - 143万円
- ✅ プリウス S セーフティープラス - 137.8万円

## 🎯 今後の改善予定

- [ ] GUI版の作成
- [ ] 複数車種対応
- [ ] 価格推移グラフ
- [ ] LINE通知対応
- [ ] 詳細フィルター（色、走行距離等）

---

**注意**: このシステムは個人利用目的で作成されており、サイトの利用規約を遵守してください。過度なアクセスは避け、適切な間隔でのチェックを心がけてください。