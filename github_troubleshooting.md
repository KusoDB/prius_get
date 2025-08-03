# 🔧 GitHub Actions トラブルシューティング

## 「プリウス監視システム」ワークフローが表示されない場合

### ✅ チェックリスト

#### 1. ファイル配置確認
以下のファイルが正しい場所にあるか確認:
```
your-repo/
└── .github/
    └── workflows/
        └── prius-monitor.yml  ← このファイルが必要
```

#### 2. ファイルがGitHubにプッシュされているか確認
```bash
# ローカルで確認
ls -la .github/workflows/

# GitHubリポジトリのWebページで確認
# https://github.com/username/repo-name/blob/main/.github/workflows/prius-monitor.yml
```

#### 3. YAMLファイルの文法エラーチェック
GitHub上でファイルを開いて、エラー表示がないか確認

#### 4. リポジトリ設定確認
- GitHubリポジトリの「Settings」→「Actions」→「General」
- 「Allow all actions and reusable workflows」が選択されているか確認

### 🚀 解決手順

#### Step 1: ファイル存在確認
```bash
# 現在のディレクトリ構造を確認
find . -name "*.yml" -o -name "*.yaml"
```

#### Step 2: 強制的にファイルを追加
```bash
# .githubディレクトリを確実に作成
mkdir -p .github/workflows

# ワークフローファイルをコピー（確実に配置）
cp prius-monitor.yml .github/workflows/ 2>/dev/null || echo "ファイルが見つかりません"

# Gitに追加
git add .github/
git commit -m "📁 GitHub Actions ワークフロー追加"
git push
```

#### Step 3: 手動でワークフローファイル作成
GitHubの Web UI で直接作成する方法:

1. GitHubリポジトリページで「Actions」タブをクリック
2. 「set up a workflow yourself」をクリック  
3. ファイル名を `prius-monitor.yml` に変更
4. 以下の内容をコピペ:

```yaml
name: プリウス監視システム

on:
  schedule:
    - cron: '*/30 * * * *'
  workflow_dispatch:

jobs:
  monitor-prius:
    runs-on: ubuntu-latest
    
    steps:
    - name: チェックアウト
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Python環境セットアップ
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: 依存関係インストール
      run: |
        pip install playwright beautifulsoup4 python-dotenv requests
        playwright install chromium
        
    - name: 既存データ復元
      run: |
        mkdir -p data
        if [ -f "vehicles_backup.json" ]; then
          cp vehicles_backup.json data/vehicles.json
          echo "既存データを復元しました"
        fi
        
    - name: プリウス監視実行
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        python cloud_monitor.py
        
    - name: データバックアップ
      run: |
        if [ -f "data/vehicles.json" ]; then
          cp data/vehicles.json vehicles_backup.json
        fi
        if [ -f "data/monitor.log" ]; then
          tail -n 100 data/monitor.log > monitor_latest.log
        fi
        
    - name: 変更をコミット
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add vehicles_backup.json monitor_latest.log
        if git diff --staged --quiet; then
          echo "変更なし"
        else
          git commit -m "🤖 プリウス監視データ更新 $(date '+%Y-%m-%d %H:%M:%S')"
          git push
        fi
```

5. 「Commit changes」をクリック

### 🔍 確認方法

#### Actions タブに表示されるべき内容:
- ワークフロー名: 「プリウス監視システム」
- 実行状況: 「queued」「running」「completed」
- 手動実行ボタン: 「Run workflow」

#### まだ表示されない場合:
1. ブラウザの更新 (Ctrl+F5 / Cmd+Shift+R)
2. 数分待機（GitHubの処理に時間がかかる場合）
3. プライベートリポジトリの場合、GitHub Actions の利用制限をチェック

### 📧 代替案: 別のワークフロー名でテスト

もし「プリウス監視システム」が表示されない場合、英語名で試してみる:

```yaml
name: Prius Monitor System  # 英語名に変更
```

### 🆘 それでも解決しない場合

1. **リポジトリを新規作成し直す**
2. **パブリックリポジトリで試す** (プライベートリポジトリの制限回避)
3. **GitHub Status** (https://www.githubstatus.com/) でサービス障害を確認

---

**最も確実な方法: GitHubのWeb UIで直接ワークフローファイルを作成することです。**