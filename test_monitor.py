#!/usr/bin/env python3
"""
監視システムのテスト実行
"""

import asyncio
from prius_monitor import PriusMonitor

async def test_monitoring():
    """監視システムをテスト"""
    print("🧪 プリウス監視システムテスト開始")
    print("=" * 50)
    
    monitor = PriusMonitor()
    
    # 1回だけチェックを実行
    print("📡 車両情報を取得中...")
    new_count = await monitor.check_for_new_vehicles()
    
    print(f"\n✅ テスト完了")
    print(f"🚗 新着車両: {new_count}台")
    
    # データファイルの確認
    import json
    from pathlib import Path
    
    vehicles_file = Path("data/vehicles.json")
    if vehicles_file.exists():
        with open(vehicles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"💾 保存済み車両: {len(data)}台")
        
        if data:
            print("\n📋 検出済み車両一覧:")
            for vehicle_id, vehicle in data.items():
                print(f"  • {vehicle['name']} - {vehicle['price']} ({vehicle_id})")
    
    # ログファイルの確認
    log_file = Path("data/monitor.log")
    if log_file.exists():
        print(f"\n📝 ログファイル: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"📄 ログエントリ数: {len(lines)}")
        if lines:
            print("📃 最新ログ:")
            for line in lines[-3:]:
                print(f"  {line.strip()}")

if __name__ == "__main__":
    asyncio.run(test_monitoring())