# ImgConverterDesktop

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.82.2-02569B?style=flat&logo=flutter&logoColor=white)](https://flet.dev/)
[![Pillow](https://img.shields.io/badge/Pillow-10.0%2B-green?style=flat)](https://python-pillow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

[Flet](https://flet.dev/)（Flutter for Python）と [Pillow](https://python-pillow.org/) を使用した、デスクトップ向け画像フォーマット変換アプリです。

## 機能

- PNG / JPEG / WebP / TIFF / GIF / BMP / PDF / ICO / EPS など 24 以上のフォーマットに対応
- `pillow-heif` による HEIC/HEIF 形式もサポート
- 変換元・変換先フォーマット、画像サイズ、ファイルサイズを表示するサムネイルプレビュー
- アプリ上から直接出力フォルダーを開く

## 必要条件

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/)（パッケージマネージャー）

## インストール

### Windows

```bash
# uv のインストール（未インストールの場合）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# リポジトリのクローン
git clone https://github.com/your-username/ImgConverterDesktop.git
cd ImgConverterDesktop

# 依存関係のインストール
uv sync
```

### macOS

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# リポジトリのクローン
git clone https://github.com/your-username/ImgConverterDesktop.git
cd ImgConverterDesktop

# 依存関係のインストール
uv sync
```

### Linux

```bash
# uv のインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# リポジトリのクローン
git clone https://github.com/your-username/ImgConverterDesktop.git
cd ImgConverterDesktop

# 依存関係のインストール
uv sync
```

## 使い方

### 実行

```bash
uv run flet run src/main.py
```

### ビルド（デスクトップアプリ）

```bash
# Windows
uv run flet build windows -v

# macOS
uv run flet build macos -v

# Linux
uv run flet build linux -v
```

## 開発

### テストの実行

```bash
uv run pytest -v
```

### リント & フォーマット

```bash
uv run ruff check .
uv run ruff format .
```

## プロジェクト構成

```
ImgConverterDesktop/
├── src/
│   ├── main.py        # GUI エントリーポイント
│   ├── utils.py       # 画像変換ロジック
│   └── assets/
│       └── icon.png   # アプリアイコン
├── tests/
│   ├── test_utils.py
│   └── test_convert.py
├── input/             # 変換元画像（自動生成）
├── output/            # 変換後画像（自動生成）
├── pyproject.toml
└── LICENSE
```

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) のもとで公開されています。
