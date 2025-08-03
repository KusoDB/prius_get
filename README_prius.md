# プリウス認定中古車監視システム

毎日自動でプリウスの認定中古車を検索し、新しい車両が見つかったときにメール通知するシステムです。

## 機能

- **自動検索**: 毎日指定時刻にプリウス中古車を自動検索
- **条件フィルタ**: 年式・駆動方式・価格での絞り込み
- **変更検知**: 新規追加・削除された車両を検知
- **メール通知**: 変更があった場合の自動メール送信
- **ログ機能**: 実行履歴の記録

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 設定ファイルの作成

```bash
python setup_prius_monitor.py
```

設定項目:
- **検索条件**: 価格上限、最低年式、駆動方式
- **通知設定**: メールアドレス、SMTPサーバー設定
- **スケジュール**: チェック実行時刻

### 3. メール設定 (Gmail使用の場合)

1. Googleアカウントで2段階認証を有効にする
2. [アプリパスワード](https://myaccount.google.com/apppasswords)を生成
3. 生成されたパスワードを設定で使用

## 使用方法

### 手動チェック実行

```bash
python prius_monitor.py check
```

### デーモンとして実行 (毎日自動実行)

```bash
python prius_monitor.py daemon
```

### 設定確認

```bash
python prius_monitor.py config
```

## 自動起動設定

### macOS (launchd)

```bash
# launchdファイルをコピー
cp com.user.prius-monitor.plist ~/Library/LaunchAgents/

# サービス開始
launchctl load ~/Library/LaunchAgents/com.user.prius-monitor.plist

# サービス停止
launchctl unload ~/Library/LaunchAgents/com.user.prius-monitor.plist
```

### Linux (systemd)

```bash
# サービスファイルをコピー
sudo cp prius-monitor.service /etc/systemd/system/

# サービス有効化・開始
sudo systemctl daemon-reload
sudo systemctl enable prius-monitor.service
sudo systemctl start prius-monitor.service

# 状態確認
sudo systemctl status prius-monitor.service
```

## 設定ファイル (prius_config.json)

```json
{
  "search_conditions": {
    "car_name": "プリウス",
    "price_max": 160,
    "year_min": 2019,
    "drive_type": "e-Four",
    "certified_only": true
  },
  "notification": {
    "email_enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipient_email": "recipient@gmail.com",
    "subject": "プリウス中古車情報更新"
  },
  "schedule": {
    "check_time": "09:00",
    "timezone": "Asia/Tokyo"
  }
}
```

## ログファイル

- `prius_monitor.log`: 実行ログ
- `prius_data.json`: 検索結果データ（変更検知用）

## 通知メール例

```
プリウス中古車情報更新 - 2025年08月02日 09:00

検索条件:
- 車種: プリウス
- 年式: 2019年以降
- 駆動方式: e-Four
- 支払総額: 160万円以下

現在の該当車両数: 3件
前回チェック時: 1件

【新規追加車両: 2件】
--------------------------------------------------
1. プリウス Aプレミアム
   価格: 145.8万円
   年式: 2020
   走行距離: 35,000km
   販売店: トヨタモビリティ東京
   URL: https://gazoo.com/U-Car/detail?Id=...

2. プリウス S
   価格: 138.5万円
   年式: 2019
   走行距離: 42,000km
   販売店: トヨタモビリティ神奈川
   URL: https://gazoo.com/U-Car/detail?Id=...
```

## トラブルシューティング

### メール送信エラー

- Gmailの2段階認証とアプリパスワードを確認
- ファイアウォール設定でSMTPポート(587)が開いているか確認

### 検索結果が取得できない

- インターネット接続を確認
- ログファイルでエラー詳細を確認

### デーモンが起動しない

- Pythonパスと作業ディレクトリを確認
- 権限設定を確認

## カスタマイズ

### 他の車種への対応

`prius_monitor.py`の`search_prius()`メソッドを修正:

```python
# 車種名フィルタを変更
if '車種名' in car_name.lower():
    # 条件チェック
```

### 通知方法の追加

- Slack通知
- LINE通知
- Discord通知

など、`send_notification()`メソッドを拡張できます。