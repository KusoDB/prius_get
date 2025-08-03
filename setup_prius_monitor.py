#!/usr/bin/env python3
"""
プリウス監視システムのセットアップスクリプト
"""

import json
import os

def setup_config():
    """設定ファイルのセットアップ"""
    print("プリウス監視システムのセットアップ")
    print("=" * 50)
    
    config = {
        "search_conditions": {
            "car_name": "プリウス",
            "price_max": 160,
            "year_min": 2019,
            "drive_type": "e-Four",
            "certified_only": True
        },
        "notification": {
            "email_enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": "",
            "subject": "プリウス中古車情報更新"
        },
        "schedule": {
            "check_time": "09:00",
            "timezone": "Asia/Tokyo"
        }
    }
    
    # 検索条件の設定
    print("\n【検索条件の設定】")
    price_max = input(f"支払総額上限 (現在: {config['search_conditions']['price_max']}万円): ")
    if price_max.strip():
        config['search_conditions']['price_max'] = int(price_max)
    
    year_min = input(f"最低年式 (現在: {config['search_conditions']['year_min']}年): ")
    if year_min.strip():
        config['search_conditions']['year_min'] = int(year_min)
    
    drive_type = input(f"駆動方式 (現在: {config['search_conditions']['drive_type']}): ")
    if drive_type.strip():
        config['search_conditions']['drive_type'] = drive_type
    
    # 通知設定
    print("\n【通知設定】")
    email_enabled = input("メール通知を有効にしますか？ (y/n): ").lower() == 'y'
    config['notification']['email_enabled'] = email_enabled
    
    if email_enabled:
        config['notification']['sender_email'] = input("送信者メールアドレス: ")
        config['notification']['sender_password'] = input("送信者パスワード (Gmailアプリパスワード): ")
        config['notification']['recipient_email'] = input("受信者メールアドレス: ")
        
        print("\n※Gmailを使用する場合:")
        print("1. Googleアカウントで2段階認証を有効にする")
        print("2. アプリパスワードを生成して上記パスワード欄に入力")
        print("3. https://myaccount.google.com/apppasswords")
    
    # スケジュール設定
    print("\n【スケジュール設定】")
    check_time = input(f"チェック時刻 (現在: {config['schedule']['check_time']}): ")
    if check_time.strip():
        config['schedule']['check_time'] = check_time
    
    # 設定ファイル保存
    with open('prius_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("\n設定完了!")
    print(f"設定ファイル: {os.path.abspath('prius_config.json')}")
    
    return config

def show_usage(config):
    """使用方法を表示"""
    print("\n" + "=" * 50)
    print("使用方法:")
    print("-" * 30)
    print("1. 即座にチェック実行:")
    print("   python prius_monitor.py check")
    print()
    print("2. デーモンとして実行 (毎日自動チェック):")
    print("   python prius_monitor.py daemon")
    print()
    print("3. 設定ファイル確認:")
    print("   python prius_monitor.py config")
    print()
    print(f"設定内容:")
    print(f"- 検索条件: {config['search_conditions']['car_name']} {config['search_conditions']['drive_type']}")
    print(f"- 年式: {config['search_conditions']['year_min']}年以降")
    print(f"- 価格: {config['search_conditions']['price_max']}万円以下")
    print(f"- チェック時刻: 毎日 {config['schedule']['check_time']}")
    print(f"- メール通知: {'有効' if config['notification']['email_enabled'] else '無効'}")

def create_systemd_service():
    """systemdサービスファイルを作成 (Linux用)"""
    print("\n【Linux systemd サービス設定】")
    create_service = input("systemdサービスファイルを作成しますか？ (y/n): ").lower() == 'y'
    
    if create_service:
        current_dir = os.path.abspath('.')
        python_path = os.popen('which python3').read().strip()
        
        service_content = f"""[Unit]
Description=Prius Monitor Service
After=network.target

[Service]
Type=simple
User={os.environ.get('USER', 'nobody')}
WorkingDirectory={current_dir}
ExecStart={python_path} {current_dir}/prius_monitor.py daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = 'prius-monitor.service'
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"\nサービスファイルを作成しました: {service_file}")
        print("\nインストール手順:")
        print(f"1. sudo cp {service_file} /etc/systemd/system/")
        print("2. sudo systemctl daemon-reload")
        print("3. sudo systemctl enable prius-monitor.service")
        print("4. sudo systemctl start prius-monitor.service")
        print("\n状態確認: sudo systemctl status prius-monitor.service")

def create_launchd_plist():
    """launchdファイルを作成 (macOS用)"""
    print("\n【macOS launchd 設定】")
    create_plist = input("launchdファイルを作成しますか？ (y/n): ").lower() == 'y'
    
    if create_plist:
        current_dir = os.path.abspath('.')
        python_path = os.popen('which python3').read().strip()
        
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.prius-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{current_dir}/prius_monitor.py</string>
        <string>daemon</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{current_dir}/prius_monitor.log</string>
    <key>StandardErrorPath</key>
    <string>{current_dir}/prius_monitor_error.log</string>
</dict>
</plist>
"""
        
        plist_file = 'com.user.prius-monitor.plist'
        with open(plist_file, 'w') as f:
            f.write(plist_content)
        
        print(f"\nlaunchdファイルを作成しました: {plist_file}")
        print("\nインストール手順:")
        print(f"1. cp {plist_file} ~/Library/LaunchAgents/")
        print("2. launchctl load ~/Library/LaunchAgents/com.user.prius-monitor.plist")
        print("\n停止: launchctl unload ~/Library/LaunchAgents/com.user.prius-monitor.plist")

def main():
    print("プリウス監視システム セットアップ")
    print("このスクリプトで設定を行います。")
    
    # 設定ファイル作成
    config = setup_config()
    
    # 使用方法表示
    show_usage(config)
    
    # OS固有のサービス設定
    import platform
    if platform.system() == 'Linux':
        create_systemd_service()
    elif platform.system() == 'Darwin':  # macOS
        create_launchd_plist()
    
    print("\n" + "=" * 50)
    print("セットアップ完了!")
    print("まずは手動でテストしてください:")
    print("python prius_monitor.py check")

if __name__ == "__main__":
    main()