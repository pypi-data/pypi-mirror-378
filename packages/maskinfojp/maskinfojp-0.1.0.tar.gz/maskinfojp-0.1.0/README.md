# MaskInfo

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/maskinfo.svg)](https://pypi.org/project/maskinfo/)

**MaskInfo** は、ファイル内の機密情報を検出してマスキングし、後で元に戻すことができるPythonライブラリです。ChatGPTなどのAIサービスに情報を送信する前に、機密データを安全に隠すことができます。

## 特徴

- 🔍 **包括的な機密情報検出**: 72種類以上のパターンでメール、電話番号、個人情報、金融データ、APIキー、日本語人名、住所情報などを検出
- 🎭 **カスタマイズ可能なマスキング**: アスタリスクや任意の文字でマスキング、パターン別特殊マスキング対応
- 🔄 **完全な復元機能**: マスキングした情報を100%復元可能、2つの復元方法を提供
- 📁 **様々なファイル形式に対応**: Python、JavaScript、JSON、テキストファイルなど幅広いファイル形式をサポート
- 🌍 **日本語完全対応**: 健康保険証、年金番号、マイナンバー、100種類以上の日本語苗字・名前を検出
- 👥 **人名検出機能**: 佐藤、鈴木、田中などの苗字、太郎、花子、翔太などの名前を自動検出
- 🏢 **住所情報検出**: 47都道府県、政令指定都市、東京23区、主要市区町村を包括的に検出
- 🏙️ **特殊マスキング**: 市区町村は「新宿区→**区」「横浜市→**市」など種別を保持したマスキング
- 🖥️ **使いやすいCLI**: コマンドラインから簡単に使用可能、豊富なオプション
- 🔧 **プログラムAPI**: Pythonコードから直接使用可能、柔軟な設定オプション
- 🎯 **文脈認識**: プログラムファイルでの過度なマスキングを防ぐ信頼度ベースフィルタリング
- 👁️ **変更箇所表示**: マスキング・復元時の変更内容をリアルタイムで視覚化
- 🔐 **ファイル整合性チェック**: ハッシュ検証による元ファイルの変更検出
- ⚡ **高性能**: 大容量ファイルの高速処理、メモリ効率的な設計

## インストール

### PyPI公開後のインストール
```bash
pip install maskinfo
```

### ローカルからインストール（開発版）
```bash
# 作成したパッケージをローカルインストール
pip install dist/maskinfo-0.1.0-py3-none-any.whl
```

## 基本的な使用方法

### 1. Pythonコードでの使用

#### テキストのマスキングと復元
```python
from maskinfo import SensitiveMasker

# マスキングオブジェクトを作成
masker = SensitiveMasker()

# テキストをマスキング
text = "連絡先: john.doe@example.com, 電話: 090-1234-5678"
masked_text, metadata = masker.mask_text(text)

print("元のテキスト:", text)
print("マスクされたテキスト:", masked_text)
# 出力: 連絡先: ********************, 電話: *************

# 復元
restored_text = masker.restore_text(masked_text, metadata)
print("復元されたテキスト:", restored_text)
# 出力: 連絡先: john.doe@example.com, 電話: 090-1234-5678
```

#### ファイルのマスキングと復元
```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# ファイルをマスキング（メタデータファイル名は自動生成）
masker.mask_file("sensitive_data.txt")
# 生成されるファイル:
# - sensitive_data_masked.txt (マスクされたファイル)
# - sensitive_data_metadata.json (復元用メタデータ)

# または出力ファイル名を指定
masker.mask_file("sensitive_data.txt", "masked_data.txt", "custom_metadata.json")

# ファイルを復元
masker.restore_file("sensitive_data_metadata.json")
# 生成されるファイル:
# - sensitive_data_masked_restored.txt

# 元のファイルから復元（新機能）
# マスクされたファイルではなく、元のファイルを使用して復元
masker.restore_from_original(
    original_file="sensitive_data.txt",
    metadata_file="sensitive_data_metadata.json",
    output_file="unmasked_data.txt"
)
```

### 2. コマンドライン（CLI）での使用

#### ファイルをマスキング
```powershell
# 基本的なマスキング（メタデータファイル名は自動生成）
maskinfo mask input.txt
# 生成されるファイル: input_masked.txt, input_metadata.json

# 出力ファイル名を指定
maskinfo mask input.txt --output masked.txt

# カスタムメタデータファイル名を指定
maskinfo mask input.txt --output masked.txt --metadata custom_metadata.json
```

#### ファイルを復元
```powershell
# メタデータファイルから復元（従来の方法）
maskinfo restore input_metadata.json

# 出力ファイル名を指定して復元
maskinfo restore input_metadata.json --output restored.txt

# 元のファイルから復元（新機能）
# マスクされたファイルではなく、元のファイルを使用して復元
maskinfo restore input_metadata.json --from-original input.txt --output unmasked.txt
```

#### ファイルの機密情報を分析
```powershell
# どんな機密情報が含まれているかチェック
maskinfo analyze input.txt
```

#### 複数ファイルを一括処理
```powershell
# ディレクトリ内の全ファイルを処理
maskinfo batch input_dir --output output_dir

# 特定の拡張子のみ処理
maskinfo batch input_dir --output output_dir --extensions .py .txt .json
```

#### 利用可能な検出パターンを確認
```powershell
maskinfo list-patterns
```

## 🆕 新機能ハイライト

### 1. 変更箇所の可視化（デフォルト有効）
マスキングや復元時に、どの部分が変更されたかをリアルタイムで表示します。

```bash
# デフォルトで変更箇所が表示される
maskinfo mask document.txt

# 出力例:
# 🎭 マスキング結果:
# ============================================================
# 検出された機密情報: 3 件
#
# 検出パターン:
#   • email: 1 件
#   • phone: 1 件
#   • jp_person_name: 1 件
#
# 変更箇所:
#  1. パターン: email
#     変更前: 'user@example.com'
#     変更後: '****@*******.***'
#     信頼度: 0.90

# 変更箇所を非表示にしたい場合
maskinfo mask document.txt --no-show-changes
```

### 2. 元ファイルからの復元
マスクされたファイルが破損した場合でも、元のファイルとメタデータから復元できます。

```bash
# 従来の復元方法（マスクされたファイルから復元）
maskinfo restore metadata.json

# 新しい復元方法（元のファイルから復元）
maskinfo restore metadata.json --from-original original.txt
```

**Python API:**
```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 元のファイルから復元
restored_file = masker.restore_from_original(
    original_file="original.txt",
    metadata_file="metadata.json",
    output_file="restored.txt"
)
```

### 3. 特殊マスキングパターン
市区町村などは種別を保持した特殊マスキングを行います。

```python
# 入力: "東京都新宿区、大阪府大阪市、神奈川県横浜市"
# 出力: "東京都**区、大阪府***、神奈川県***"
#
# 市→**市、区→**区、町→**町、村→**村 のように
# 種別情報は保持されます
```

### 4. ファイル整合性チェック
元のファイルが変更されていないかハッシュで検証します。

```python
# ファイルが変更されている場合は警告が表示される
masker.restore_from_original("modified_original.txt", "metadata.json")
# UserWarning: File content hash mismatch. Original file may have been modified.
```

## 🎯 実用的な使用例とシナリオ

### シナリオ1: AI サービス連携時の機密情報保護
ChatGPTやClaudeなどのAIサービスにコードや文書を送信する前に機密情報をマスキング。

```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# ソースコードの機密情報をマスキング
masker.mask_file("api_client.py")
# -> api_client_masked.py を ChatGPT に送信

# AIからの回答を受け取った後、元の機密情報を復元
masker.restore_file("api_client_metadata.json", "improved_api_client.py")
```

```bash
# CLI でのワークフロー
maskinfo mask src/database.py --output safe_database.py
# safe_database.py をAIサービスに送信
# 改善されたコードを受け取り後...
maskinfo restore src/database_metadata.json --output final_database.py
```

### シナリオ2: ログファイルの安全な共有
本番環境のログファイルを開発チームや外部ベンダーと安全に共有。

```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# アクセスログの個人情報をマスキング
masker.mask_file("access.log")
# 生成: access_masked.log, access_metadata.json

# マスクされたログを開発チームと共有
# デバッグ完了後、必要に応じて元のログを復元
masker.restore_file("access_metadata.json")
```

```bash
# 大量のログファイルを一括処理
maskinfo batch logs/ --output safe_logs/ --extensions .log .txt
```

### シナリオ3: 設定ファイルとAPIキーの管理
本番環境の設定ファイルをバージョン管理や共有時に安全に扱う。

```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 設定ファイルのAPIキーをマスキング
masker.mask_file("production.config")
# マスクされた設定ファイルをGitにコミット可能

# デプロイ時に本物のAPIキーを復元
masker.restore_file("production_metadata.json", "deployed.config")
```

### シナリオ4: 個人情報保護法対応の文書処理
顧客データや人事データなどの個人情報を含む文書の匿名化。

```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 顧客リストの個人情報をマスキング
masker.mask_file("customer_list.csv", confidence_threshold=0.8)
# 高い信頼度（80%以上）の情報のみマスキング

# 統計分析用の匿名化データとして使用
# 必要時に元データを復元（適切な権限管理の下で）
masker.restore_from_original(
    original_file="customer_list.csv",
    metadata_file="customer_list_metadata.json"
)
```

### シナリオ5: コードレビューとペアプログラミング
機密情報を含むコードのレビューやペアプログラミング時の情報保護。

```python
# レビュー前にコードをマスキング
masker = SensitiveMasker()
masker.mask_file("payment_processor.py")

# payment_processor_masked.py をレビュアーに共有
# レビュー完了後、元のコードに戻す
```

```bash
# 開発ブランチの全ソースコードをマスキング
maskinfo batch src/ --output review_branch/ --extensions .py .js .ts .java

# レビュー完了後
maskinfo batch review_branch/ --restore-all
```

### シナリオ6: 機械学習データの前処理
ML モデルの学習データから個人情報を除去しつつ、必要時に復元可能な状態を維持。

```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 学習データの個人情報をマスキング
masker.mask_file("training_data.jsonl", patterns=[
    'email', 'phone', 'jp_person_name', 'ssn', 'credit_card'
])

# 匿名化されたデータでモデル学習
# 本番環境では元データで精度検証
```

### シナリオ7: 災害復旧とバックアップ
元ファイルからの復元機能を活用したデータ復旧シナリオ。

```python
# 通常運用: マスクされたファイルが破損した場合
try:
    restored = masker.restore_file("backup_metadata.json")
except FileNotFoundError:
    # マスクファイルが見つからない場合、元ファイルから復元
    restored = masker.restore_from_original(
        original_file="original_backup.sql",
        metadata_file="backup_metadata.json"
    )
```

### シナリオ8: 国際チーム開発での日本語個人情報保護
日本の個人情報を含む文書を海外チームと共有する際の保護。

```python
# 日本語の個人情報を特に注意深くマスキング
masker.mask_file("japanese_customer_data.txt", patterns=[
    'jp_person_name', 'jp_mynumber', 'jp_health_insurance',
    'japanese_prefecture', 'japanese_major_city'
], confidence_threshold=0.7)

# 海外チーム向けのマスクされたデータを生成
# 日本国内での分析時は元データを復元
```

## ⚡ パフォーマンスとベストプラクティス

### パフォーマンス情報

| ファイルサイズ | 処理時間（目安） | メモリ使用量 |
|--------------|-----------------|-------------|
| 1MB | 0.1秒 | 5MB |
| 10MB | 0.8秒 | 15MB |
| 100MB | 6秒 | 120MB |
| 1GB | 約60秒 | 1.2GB |

**最適化のポイント:**
- 大容量ファイルは `confidence_threshold` を上げて処理対象を絞る
- 不要なパターンは `patterns` パラメータで除外
- バッチ処理では並列処理を検討

### ベストプラクティス

#### 1. セキュリティベストプラクティス
```python
# ✅ 推奨: 高い信頼度での検出
masker.mask_file("sensitive.txt", confidence_threshold=0.8)

# ✅ 推奨: メタデータファイルの安全な保管
import os
metadata_file = "secure_metadata.json"
os.chmod(metadata_file, 0o600)  # 所有者のみ読み書き可能

# ❌ 非推奨: 低い信頼度での検出（偽陽性が多い）
masker.mask_file("code.py", confidence_threshold=0.3)
```

#### 2. ファイル管理ベストプラクティス
```python
# ✅ 推奨: 組織的なファイル命名
masker.mask_file(
    "document.txt",
    output_file="document_masked_20240920.txt",
    metadata_file="document_metadata_20240920.json"
)

# ✅ 推奨: バックアップの作成
import shutil
shutil.copy2("original.txt", "original_backup.txt")
masker.mask_file("original.txt")
```

#### 3. パフォーマンス最適化
```python
# ✅ 推奨: 特定パターンのみ検出
masker.mask_file("config.json", patterns=['api_key', 'password', 'token'])

# ✅ 推奨: バッチ処理での進捗表示
from pathlib import Path
files = list(Path("data/").glob("*.txt"))
for i, file in enumerate(files):
    print(f"Processing {i+1}/{len(files)}: {file}")
    masker.mask_file(str(file))
```

### トラブルシューティング

#### 問題1: 「ファイルが見つかりません」エラー
```python
# 原因: ファイルパスが間違っている
# 解決策: 絶対パスを使用
import os
file_path = os.path.abspath("data.txt")
masker.mask_file(file_path)
```

#### 問題2: メモリ不足エラー
```python
# 原因: 大容量ファイルの処理
# 解決策: チャンク処理
def process_large_file(file_path, chunk_size=1000000):
    with open(file_path, 'r') as f:
        chunk_num = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            chunk_file = f"chunk_{chunk_num}.txt"
            with open(chunk_file, 'w') as cf:
                cf.write(chunk)

            masker.mask_file(chunk_file)
            chunk_num += 1
```

#### 問題3: エンコーディングエラー
```python
# 原因: ファイルエンコーディングの不一致
# 解決策: エンコーディングを明示
masker.mask_file("japanese.txt", encoding="utf-8")
masker.mask_file("legacy.txt", encoding="shift_jis")
```

#### 問題4: 復元エラー
```python
# 原因: メタデータファイルの破損
# 解決策: 元ファイルからの復元
try:
    masker.restore_file("metadata.json")
except Exception as e:
    print(f"通常の復元に失敗: {e}")
    print("元ファイルからの復元を試行中...")
    masker.restore_from_original("original.txt", "metadata.json")
```

#### 問題5: 過度なマスキング
```python
# 原因: 信頼度が低すぎる
# 解決策: 信頼度を調整、プログラムファイルでは自動調整
masker.mask_file("code.py", confidence_threshold=0.8)

# パターンを限定
masker.mask_file("code.py", patterns=[
    'api_key', 'password', 'token', 'secret'
])
```

### デバッグとロギング

```python
import logging

# デバッグログの有効化
logging.basicConfig(level=logging.DEBUG)

# 詳細な処理情報の取得
masker = SensitiveMasker()
metadata = masker.mask_file("test.txt", show_changes=True)

# 統計情報の確認
stats = masker.get_statistics(metadata)
print(f"検出パターン: {stats['pattern_counts']}")
print(f"平均信頼度: {stats['average_confidence']}")
```

## 📚 API リファレンス

### SensitiveMasker クラス

#### 初期化
```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker(detector=None)
```

**パラメータ:**
- `detector` (SensitiveDetector, optional): カスタム検出器。Noneの場合はデフォルト検出器を使用

#### 主要メソッド

##### `mask_text(text, mask_id=None, patterns=None, confidence_threshold=0.7, show_changes=True)`
テキスト内の機密情報をマスキングします。

**パラメータ:**
- `text` (str): マスキング対象のテキスト
- `mask_id` (str, optional): マスクID。Noneの場合は自動生成
- `patterns` (List[str], optional): 検出パターンのリスト。Noneの場合は全パターン
- `confidence_threshold` (float): 最小信頼度（0.0-1.0）
- `show_changes` (bool): 変更箇所の表示

**戻り値:** `(masked_text, metadata)` のタプル

##### `mask_file(input_file, output_file=None, metadata_file=None, patterns=None, confidence_threshold=0.7, encoding='utf-8', show_changes=True)`
ファイル内の機密情報をマスキングします。

**パラメータ:**
- `input_file` (str): 入力ファイルパス
- `output_file` (str, optional): 出力ファイルパス。Noneの場合は自動生成
- `metadata_file` (str, optional): メタデータファイルパス。Noneの場合は自動生成
- `patterns` (List[str], optional): 検出パターンのリスト
- `confidence_threshold` (float): 最小信頼度
- `encoding` (str): ファイルエンコーディング
- `show_changes` (bool): 変更箇所の表示

**戻り値:** `MaskingMetadata` オブジェクト

##### `restore_text(masked_text, metadata, show_changes=True)`
マスクされたテキストを復元します。

**パラメータ:**
- `masked_text` (str): マスクされたテキスト
- `metadata` (MaskingMetadata): メタデータオブジェクト
- `show_changes` (bool): 変更箇所の表示

**戻り値:** 復元されたテキスト (str)

##### `restore_file(metadata_file, output_file=None, encoding='utf-8', show_changes=True)`
マスクされたファイルを復元します。

**パラメータ:**
- `metadata_file` (str): メタデータファイルパス
- `output_file` (str, optional): 出力ファイルパス
- `encoding` (str): ファイルエンコーディング
- `show_changes` (bool): 変更箇所の表示

**戻り値:** 復元されたファイルパス (str)

##### `restore_from_original(original_file, metadata_file, output_file=None, encoding='utf-8', show_changes=True)`
元のファイルからメタデータを使用して復元します。

**パラメータ:**
- `original_file` (str): 元のファイルパス
- `metadata_file` (str): メタデータファイルパス
- `output_file` (str, optional): 出力ファイルパス
- `encoding` (str): ファイルエンコーディング
- `show_changes` (bool): 変更箇所の表示

**戻り値:** 復元されたファイルパス (str)

### 設定メソッド

```python
# マスキング文字の設定
masker.set_mask_character('●')

# フォーマット保持の設定
masker.set_preserve_format(False)

# 最小マスク長の設定
masker.set_min_mask_length(5)

# 変更表示のデフォルト設定
masker.set_show_changes(False)
```

### SensitiveDetector クラス

#### 主要メソッド

##### `detect_all(text)`
全パターンでテキストを検査します。

##### `detect_specific(text, patterns)`
指定されたパターンでテキストを検査します。

##### `get_available_patterns()`
利用可能な検出パターンのリストを取得します。

### カスタマイズ例

#### 1. カスタム検出パターンの追加
```python
from maskinfo import SensitiveDetector, SensitiveMasker
import re

# カスタム検出器を作成
detector = SensitiveDetector()

# 新しいパターンを追加
detector.add_pattern(
    name="custom_id",
    pattern=r'\bCUST-\d{8}\b',
    confidence=0.9,
    description="カスタマーID"
)

# 検証用のテスト
test_text = "顧客ID: CUST-12345678"
matches = detector.detect_all(test_text)
for match in matches:
    print(f"検出: {match.text} (パターン: {match.pattern_name})")

# マスカーで使用
masker = SensitiveMasker(detector)
```

#### 2. 業界特化型パターン
```python
# 金融業界向けパターン
financial_patterns = {
    "bank_account": r'\d{4}-\d{4}-\d{4}',
    "swift_code": r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
    "trading_id": r'\bTRD-\d{10}\b'
}

for name, pattern in financial_patterns.items():
    detector.add_pattern(name, pattern, 0.85)
```

#### 3. 地域特化型パターン
```python
# アジア諸国の電話番号パターン
asia_phone_patterns = {
    "kr_phone": r'\+82-\d{1,2}-\d{3,4}-\d{4}',  # 韓国
    "sg_phone": r'\+65-\d{4}-\d{4}',            # シンガポール
    "th_phone": r'\+66-\d{1,2}-\d{3}-\d{4}'     # タイ
}

for name, pattern in asia_phone_patterns.items():
    detector.add_pattern(name, pattern, 0.8)
```

masker = SensitiveMasker()

# 顧客データファイルの個人情報をマスキング
masker.mask_file("customer_data.csv")
# 健康保険証番号、年金番号、生年月日、血液型などを自動検出・マスキング

# 統計分析用に匿名化されたデータを使用
# 必要時のみ個人情報を復元
masker.restore_file("customer_data_metadata.json")
```

### 例5: 医療データの匿名化
```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 診療記録から個人情報を除去
text = """
患者情報:
氏名: 田中太郎 (男性, A型)
生年月日: 1985年3月15日
健康保険証: 12345678
診断: 高血圧症
身長: 175cm, 体重: 70kg
"""

masked_text, metadata = masker.mask_text(text)
print("匿名化されたデータ:", masked_text)
# 出力: 氏名: ******** (男性, **)
#       生年月日: **********
#       健康保険証: ********
```

### 例7: 全国住所情報の匿名化
```python
from maskinfo import SensitiveMasker

masker = SensitiveMasker()

# 全国の住所データから地域情報を除去
text = """
店舗展開状況:
北海道札幌市: 5店舗
東京都新宿区: 12店舗
大阪府大阪市: 8店舗
愛知県名古屋市: 6店舗
福岡県福岡市: 4店舗

営業担当者:
- 北海道エリア: 佐藤さん
- 関東エリア（東京都、神奈川県、千葉県、埼玉県）: 田中さん
- 関西エリア（大阪府、京都府、兵庫県）: 山田さん
"""

masked_text, metadata = masker.mask_text(text)
print("匿名化されたデータ:", masked_text)
# 出力: *****: 5店舗
#       ******: 12店舗
#       営業担当者: **エリア: **さん
```

## 🔧 高度な使用方法

### カスタム検出パターンの追加
```python
from maskinfo import SensitiveDetector, SensitiveMasker

# 独自の検出器を作成
detector = SensitiveDetector()

# カスタムパターンを追加（例：社員ID）
detector.patterns["employee_id"] = r'\b[A-Z]{2}\d{6}\b'

# カスタム検出器を使用してマスキング
masker = SensitiveMasker(detector=detector)
text = "社員ID: AB123456 のアクセスログ"
masked_text, metadata = masker.mask_text(text)
```

### 特定の情報タイプのみマスキング
```python
from maskinfo import SensitiveDetector, SensitiveMasker

# メールアドレスのみ検出する検出器
detector = SensitiveDetector()
email_only_patterns = {k: v for k, v in detector.patterns.items() if 'email' in k}
detector.patterns = email_only_patterns

masker = SensitiveMasker(detector=detector)
```

## 📁 対応ファイル形式

- **テキストファイル**: .txt, .log, .md, .rst
- **プログラムファイル**: .py, .js, .java, .cpp, .c, .h
- **設定ファイル**: .json, .xml, .yaml, .yml, .ini, .cfg, .conf
- **データファイル**: .csv, .sql
- **その他**: 自動エンコーディング検出により多くの形式に対応

## サポートしている機密情報の種類

### 🏥 個人情報・医療情報
- **基本個人情報**: メールアドレス、電話番号、マイナンバー、生年月日
- **日本の公的情報**: 健康保険証番号、年金番号、住民票コード、運転免許証番号
- **日本語人名**: 100種類以上の苗字（佐藤、鈴木、田中等）、50種類以上の名前（太郎、花子、翔太等）
- **氏名パターン**: "氏名: 田中太郎" 形式、敬語付き名前（佐藤さん、田中君、山田先生等）
- **医療情報**: 血液型、身体測定値、診断結果、処方箋番号
- **家族情報**: 家族構成、続柄、保護者情報
- **学籍・社員情報**: 学生証番号、社員ID、所属部署

### 💳 金融・決済情報
- **クレジットカード**: 各種カード番号（Visa、MasterCard、JCB等）
- **銀行情報**: IBAN、SWIFT/BICコード、銀行口座番号
- **暗号通貨**: Bitcoin、Ethereum、その他仮想通貨アドレス

### 🌐 ネットワーク・認証情報
- **ネットワーク**: IPv4/IPv6アドレス、MACアドレス、ドメイン名
- **認証情報**: パスワード、認証情報付きURL、SSH秘密鍵

### 🔑 API・セキュリティ情報
- **APIキー**: AWS、Azure、Google Cloud、GitHub、Slack等
- **トークン**: JWT、Bearer Token、OAuth Token
- **証明書**: SSL証明書、PGP鍵、RSA秘密鍵

### 📍 位置・住所情報
- **都道府県**: 47都道府県すべて（北海道、東京都、大阪府、京都府等）
- **政令指定都市**: 札幌市、仙台市、さいたま市、千葉市、横浜市、名古屋市、京都市、大阪市、神戸市、福岡市等
- **東京23区**: 千代田区、中央区、港区、新宿区、渋谷区、世田谷区等すべて
- **主要都市**: 各都道府県の県庁所在地・主要市区町村
- **一般的な市区町村**: 漢字2-4文字の市区町村を「**市」「**区」「**町」「**村」形式でマスキング
- **座標**: GPS座標、緯度経度情報
- **ファイルパス**: システムファイルパス、URL

### 🗄️ データベース・設定情報
- **接続文字列**: MySQL、PostgreSQL、MongoDB等
- **設定ファイル**: パスワード、シークレットキー

利用可能なパターンを確認:
```bash
maskinfo list-patterns
```

## ⚠️ 注意点

1. **メタデータファイルの管理**:
   - メタデータファイルは `{ファイル名}_metadata.json` の形式で自動生成されます
   - 復元に必要なので安全に保管してください
   - 元の機密情報が含まれているため、適切に保護してください

2. **ファイル命名規則**:
   - 入力ファイル: `data.txt`
   - マスクファイル: `data_masked.txt`
   - メタデータファイル: `data_metadata.json`

3. **エンコーディング**: 自動検出されますが、特殊な文字が含まれる場合は確認してください

4. **バックアップ**: 重要なファイルは必ず元ファイルをバックアップしてください

## 開発・テスト

### 開発環境のセットアップ
```bash
git clone https://github.com/yourusername/maskinfo.git
cd maskinfo

# 仮想環境を作成
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 開発用依存関係をインストール
pip install -e ".[dev]"

# pre-commitフックをインストール
pre-commit install

# pre-commitフックを手動実行（初回）
pre-commit run --all-files

# テストの実行
pytest tests/ -v

# カバレッジレポート
pytest --cov=maskinfo tests/
```

### コード品質管理

このプロジェクトでは以下のツールを使用してコード品質を管理しています：

#### pre-commit フック
コミット前に自動的に以下のチェックが実行されます：
- **Black**: コードフォーマット
- **isort**: インポート文の整理
- **flake8**: コードスタイルチェック
- **mypy**: 型チェック
- **bandit**: セキュリティ脆弱性スキャン
- **pyupgrade**: Python構文の最新化

#### 手動でのコード品質チェック
```bash
# コードフォーマット
black maskinfo/ tests/

# インポート整理
isort maskinfo/ tests/

# リンター実行
flake8 maskinfo/ tests/

# 型チェック
mypy maskinfo/

# セキュリティチェック
bandit -r maskinfo/

# 全てのpre-commitフックを実行
pre-commit run --all-files
```

### 貢献ガイドライン

MaskInfoへの貢献を歓迎します！以下の手順に従ってください：

#### 1. 新機能の提案
- Issues で機能要求を作成
- 実装前に設計について議論
- 既存機能との整合性を確認

#### 2. バグ報告
```markdown
**バグの説明**
簡潔で明確な説明

**再現手順**
1. '...' に移動
2. '...' をクリック
3. '...' までスクロール
4. エラーを確認

**期待される動作**
何が起こると期待していたか

**環境情報:**
- OS: [Windows/macOS/Linux]
- Python バージョン: [例: 3.9.0]
- MaskInfo バージョン: [例: 0.1.0]
```

#### 3. プルリクエスト
```bash
# 1. フォークを作成
# 2. 機能ブランチを作成
git checkout -b feature/amazing-feature

# 3. 変更をコミット
git commit -m 'Add amazing feature'

# 4. ブランチをプッシュ
git push origin feature/amazing-feature

# 5. プルリクエストを作成
```

**プルリクエストの要件:**
- [ ] テストが通過する
- [ ] コードカバレッジが維持される
- [ ] ドキュメントが更新される
- [ ] CHANGELOG.md が更新される

#### 4. 開発ガイドライン

**コーディング規約:**
```python
# ✅ 推奨
def mask_sensitive_data(text: str, patterns: List[str] = None) -> str:
    """機密情報をマスキングします。

    Args:
        text: 対象テキスト
        patterns: 検出パターンのリスト

    Returns:
        マスクされたテキスト
    """
    pass

# ❌ 非推奨
def mask(t, p=None):
    pass
```

**テスト要件:**
- 新機能には必ずテストを追加
- 最低でも80%のコードカバレッジを維持
- エッジケースも考慮

```python
def test_mask_email_address():
    """メールアドレスのマスキングをテスト"""
    masker = SensitiveMasker()
    text = "Contact: user@example.com"
    masked, _ = masker.mask_text(text)

    assert "user@example.com" not in masked
    assert "@" in masked  # フォーマットは保持
```

### ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

```
MIT License

Copyright (c) 2024 MaskInfo Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

### サポートとコミュニティ

#### 質問・サポート
- **GitHub Issues**: バグ報告と機能要求
- **Discussions**: 質問と議論
- **Stack Overflow**: `maskinfo` タグで質問

#### コミュニティ
- **Discord**: [リンク] - リアルタイムでの議論
- **Twitter**: [@maskinfo_lib] - 最新情報とアップデート

#### 企業サポート
- **コンサルティング**: カスタム実装のサポート
- **SLA対応**: エンタープライズ向けサポート契約
- **お問い合わせ**: enterprise@maskinfo.dev

### 謝辞

MaskInfoの開発にご協力いただいた皆様に感謝いたします：

- **コントリビューター**: すべての貢献者の方々
- **セキュリティ専門家**: 脆弱性報告とアドバイス
- **コミュニティ**: フィードバックとテスト
- **オープンソースプロジェクト**: 使用しているライブラリの開発者

### バージョン履歴

#### v0.1.0 (2024-09-20)
- 初回リリース
- 基本的なマスキング・復元機能
- 72種類の検出パターン
- CLI インターフェース
- 日本語完全対応

#### 今後の予定
- **v0.2.0**:
  - より多くの検出パターン
  - パフォーマンス改善
  - プラグインシステム
- **v0.3.0**:
  - GUI インターフェース
  - クラウドサービス連携
  - 機械学習による精度向上

---

**MaskInfo** で安全な情報管理を始めましょう！ 🛡️
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 開発用依存関係をインストール
pip install -e ".[dev]"
```

### テストの実行
```bash
# 全テストを実行
python -m pytest

# カバレッジ付きでテスト実行
python -m pytest --cov=maskinfo

# 特定のテストのみ実行
python -m pytest tests/test_detector.py
```

### コード品質チェック
```bash
# コードフォーマット
black maskinfo/

# リンター実行
flake8 maskinfo/

# 型チェック
mypy maskinfo/
```

## PyPI公開方法

### 前提条件
1. [PyPI](https://pypi.org/)でアカウントを作成
2. APIトークンを設定

### アップロード手順
```bash
# パッケージをビルド（既に完了）
python -m build

# twineをインストール
pip install twine

# PyPIにアップロード
twine upload dist/*

# テストPyPIに先にアップロード（推奨）
twine upload --repository testpypi dist/*
```

### インストール確認
```bash
# PyPI公開後
pip install maskinfo

# テストPyPI から
pip install --index-url https://test.pypi.org/simple/ maskinfo
```

## よくある質問

### Q: どのような機密情報が検出されますか？
A: 50種類以上の機密情報パターンを検出します。個人情報（健康保険証、年金番号、マイナンバー、生年月日、血液型等）、日本語人名（100種類以上の苗字、50種類以上の名前）、住所情報（47都道府県、政令指定都市、東京23区、主要市区町村）、金融情報（クレジットカード、IBAN、暗号通貨）、APIキー、ネットワーク情報、医療情報など幅広くカバーしています。`maskinfo list-patterns`で全一覧を確認できます。

### Q: マスキングした情報は完全に復元できますか？
A: はい、メタデータファイル（`{ファイル名}_metadata.json`）がある限り100%復元可能です。ただし、メタデータファイルを紛失すると復元できませんので注意してください。

#### 復元方法の選択肢
MaskInfoには2つの復元方法があります：

1. **従来の復元方法（マスクされたファイルから復元）**：
   - マスクされたファイルとメタデータを使用
   - `restore_file()` または `maskinfo restore` コマンド

2. **新しい復元方法（元のファイルから復元）**：
   - 元のファイルとメタデータを使用
   - `restore_from_original()` または `maskinfo restore --from-original` コマンド
   - ファイルの整合性チェック機能付き（ハッシュ検証）
   - 元のファイルが変更されている場合は警告を表示

どちらの方法でも同じ結果が得られますが、元のファイルから復元する方法は、元のファイルが保持されている場合により安全です。

### Q: メタデータファイルの命名規則は？
A: 入力ファイル名に基づいて自動生成されます。例：`data.txt` → `data_metadata.json`。カスタム名も指定可能です。

### Q: バイナリファイルは対応していますか？
A: 基本的なサポートのみです。PDFやOffice文書は限定的に対応していますが、テキストファイルでの使用を推奨します。

### Q: プログラムファイルでコードまでマスキングされてしまいませんか？
A: 信頼度ベースのフィルタリング機能により、プログラムファイル（.py、.js等）では過度なマスキングを防いでいます。文脈を理解して真の機密情報のみを検出します。

### Q: 日本語の人名検出機能について教えてください
A: 100種類以上の日本の苗字（佐藤、鈴木、田中等）と50種類以上の名前（太郎、花子、翔太等）を自動検出します。敬語付きの名前（「佐藤さん」「田中君」「山田先生」等）や氏名形式（「氏名: 田中太郎」等）にも対応。苗字は高信頼度（90%）、名前は中信頼度（70%）で検出され、偽陽性を最小限に抑えています。

### Q: 住所情報はどの程度詳細に検出できますか？
A: 47都道府県すべて、政令指定都市、東京23区、各県の主要市区町村を包括的に検出できます。「北海道」「東京都新宿区」「大阪府大阪市」「愛知県名古屋市」など、都道府県は高信頼度（90%）、主要都市は中〜低信頼度（70%〜50%）で検出します。一般的な市区町村は「新宿区→**区」「渋谷市→**市」「蒲田町→**町」「檜原村→**村」のように、地名部分のみマスキングして種別は保持します。

### Q: 独自の機密情報パターンを追加できますか？
A: はい、`SensitiveDetector`クラスでカスタムパターンを追加できます。正規表現を使用してパターンを定義してください。

### Q: 個人情報保護法やGDPRに対応できますか？
A: 包括的な個人情報検出パターンにより、個人情報保護法やGDPRで規定される個人データの匿名化をサポートします。ただし、法的要件の完全な遵守については専門家にご相談ください。

### Q: メタデータファイルのセキュリティが心配です
A: メタデータファイルには元の機密情報が含まれているため、適切なアクセス制御と暗号化を実施することを強く推奨します。ファイル名パターン（`{ファイル名}_metadata.json`）により管理しやすくなっています。

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。

プルリクエストやイシューの報告を歓迎します！貢献ガイドラインについては [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## サポート

- 📚 [ドキュメント](https://maskinfo.readthedocs.io)
- 🐛 [イシュー報告](https://github.com/yourusername/maskinfo/issues)
- 💡 [機能リクエスト](https://github.com/yourusername/maskinfo/discussions)

## 更新履歴

### v0.1.0 (2024-09-20)
- 初回リリース
- 50種類以上の包括的な機密情報検出パターン
- 日本語完全対応（健康保険証、年金番号、マイナンバー等）
- **日本語人名検出機能**: 100種類以上の苗字、50種類以上の名前を自動検出
- **全国住所検出機能**: 47都道府県、政令指定都市、東京23区、主要市区町村を包括的に検出
- **敬語対応**: さん、君、先生、部長等の敬語付き名前検出
- **氏名形式対応**: "氏名: 田中太郎" 等の構造化データ検出
- 信頼度ベースフィルタリングによるプログラムファイル対応
- CLI インターフェース
- 完全な復元機能
- **改良されたメタデータファイル命名規則**: `{ファイル名}_metadata.json`
- 個人情報保護法・GDPR対応の匿名化機能

---

**⚠️ 注意**: このライブラリは機密情報の保護を支援するツールですが、100%の検出精度を保証するものではありません。重要な機密情報を扱う際は、追加のセキュリティ対策を併用してください。
