#!/usr/bin/env python3
"""
通知設定セットアップスクリプト
.envファイルに通知設定を追加
"""

import os
from pathlib import Path

def setup_env_file():
    """環境変数設定ファイルを作成/更新"""
    env_file = Path(".env")
    
    print("🔧 プリウス監視システム通知設定")
    print("=" * 50)
    
    config = {}
    
    # 既存の.envファイルを読み込み
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    
    print("\n📱 通知設定（エンターでスキップ）")
    
    # Slack設定
    print("\n1. Slack通知設定")
    slack_url = input(f"Slack Webhook URL [{config.get('SLACK_WEBHOOK_URL', '')}]: ").strip()
    if slack_url:
        config['SLACK_WEBHOOK_URL'] = slack_url
    
    # メール設定
    print("\n2. メール通知設定")
    smtp_server = input(f"SMTP Server (例: smtp.gmail.com) [{config.get('SMTP_SERVER', '')}]: ").strip()
    if smtp_server:
        config['SMTP_SERVER'] = smtp_server
        
        smtp_port = input(f"SMTP Port (例: 587) [{config.get('SMTP_PORT', '587')}]: ").strip()
        config['SMTP_PORT'] = smtp_port or '587'
        
        email_user = input(f"送信者メールアドレス [{config.get('EMAIL_USER', '')}]: ").strip()
        if email_user:
            config['EMAIL_USER'] = email_user
        
        email_password = input(f"送信者メールパスワード/アプリパスワード [{config.get('EMAIL_PASSWORD', '')}]: ").strip()
        if email_password:
            config['EMAIL_PASSWORD'] = email_password
        
        to_email = input(f"通知先メールアドレス [{config.get('TO_EMAIL', '')}]: ").strip()
        if to_email:
            config['TO_EMAIL'] = to_email
    
    # .envファイルに書き込み
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write("# プリウス監視システム設定\n\n")
        
        f.write("# Slack通知設定\n")
        f.write(f"SLACK_WEBHOOK_URL={config.get('SLACK_WEBHOOK_URL', '')}\n\n")
        
        f.write("# メール通知設定\n")
        f.write(f"SMTP_SERVER={config.get('SMTP_SERVER', '')}\n")
        f.write(f"SMTP_PORT={config.get('SMTP_PORT', '587')}\n")
        f.write(f"EMAIL_USER={config.get('EMAIL_USER', '')}\n")
        f.write(f"EMAIL_PASSWORD={config.get('EMAIL_PASSWORD', '')}\n")
        f.write(f"TO_EMAIL={config.get('TO_EMAIL', '')}\n")
    
    print(f"\n✅ 設定を {env_file} に保存しました")
    
    # 設定状況を表示
    print("\n📋 現在の通知設定:")
    if config.get('SLACK_WEBHOOK_URL'):
        print("  ✅ Slack通知: 設定済み")
    else:
        print("  ❌ Slack通知: 未設定")
    
    if all([config.get('SMTP_SERVER'), config.get('EMAIL_USER'), config.get('TO_EMAIL')]):
        print("  ✅ メール通知: 設定済み")
    else:
        print("  ❌ メール通知: 未設定")
    
    print("  ✅ デスクトップ通知: 利用可能（macOS）")

def create_launch_script():
    """起動スクリプトを作成"""
    script_content = '''#!/bin/bash
# プリウス監視システム起動スクリプト

cd "$(dirname "$0")"

echo "🚗 プリウス監視システム起動中..."
echo "停止するには Ctrl+C を押してください"
echo ""

python3 prius_monitor.py
'''
    
    with open("start_monitor.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("start_monitor.sh", 0o755)
    print("✅ 起動スクリプト start_monitor.sh を作成しました")

def create_cron_example():
    """cron設定例を表示"""
    cron_example = '''
# プリウス監視システムのcron設定例
# crontab -e で編集してください

# 30分ごとに1回チェック（推奨）
*/30 * * * * cd /Users/ishidatomohisa/projects/250803_prius_get && python3 prius_monitor.py --single-check

# 15分ごとに1回チェック（頻繁）
*/15 * * * * cd /Users/ishidatomohisa/projects/250803_prius_get && python3 prius_monitor.py --single-check

# 毎時0分にチェック（控えめ）
0 * * * * cd /Users/ishidatomohisa/projects/250803_prius_get && python3 prius_monitor.py --single-check
'''
    
    with open("cron_example.txt", "w") as f:
        f.write(cron_example.strip())
    
    print("✅ cron設定例を cron_example.txt に保存しました")

if __name__ == "__main__":
    setup_env_file()
    print()
    create_launch_script()
    create_cron_example()
    
    print(f"\n🎯 次のステップ:")
    print("1. ./start_monitor.sh で監視開始")
    print("2. または python3 prius_monitor.py で直接実行")
    print("3. バックグラウンド実行は cron_example.txt を参考に設定")
    print()
    print("📝 ログは data/monitor.log に保存されます")
    print("💾 検出済み車両は data/vehicles.json に保存されます")