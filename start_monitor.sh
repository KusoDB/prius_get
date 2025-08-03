#!/bin/bash
# プリウス監視システム起動スクリプト

cd "$(dirname "$0")"

echo "🚗 プリウス監視システム起動中..."
echo "監視条件: プリウス, 2019年以降, 4WD/e-Four, 160万円以下"
echo "チェック間隔: 30分"
echo "停止するには Ctrl+C を押してください"
echo ""

python3 prius_monitor.py