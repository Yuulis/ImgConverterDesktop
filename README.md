<h1 align="center">ImgConverterDesktop</h1>

<p align="center">
  <img alt="GitHub Release" src="https://badgen.net/github/release/Yuulis/ImgConverterDesktop">
  <img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FYuulis%2FImgConverterDesktop%2Frefs%2Fheads%2Fmain%2Fpyproject.toml">
  <img alt="Flet Version" src="https://img.shields.io/badge/Flet-0.82.2-blueviolet?logo=flutter&logoColor=white">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green">
  <img alt="GitHub Actions Workflow Status" src="https://badgen.net/github/checks/Yuulis/ImgConverterDesktop/main">
  <br>
  <img alt="Windows" src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white">
  <img alt="macOS" src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white">
  <img alt="Linux" src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black">
</p>

<p align="center">シンプルなデスクトップ向け画像形式変換アプリケーション</p>

---

## 機能

- PNG / JPEG / WebP / TIFF / GIF / BMP / PDF / ICO / EPS など 24 以上のフォーマットに対応
- `pillow-heif` による HEIC/HEIF 形式もサポート
- 変換元・変換先の形式・画像サイズ・ファイルサイズを表示するサムネイルプレビュー
- アプリ上から変換後の画像に直接アクセス可能
- Windows / macOS / Linux で動作するクロスプラットフォーム対応

## スクリーンショット

![メイン画面](screenshots/main.png)

## インストール

[Releases](https://github.com/Yuulis/ImgConverterDesktop/releases) ページから、お使いの OS に適した最新のリリースをダウンロードしてください。

| OS | ダウンロードファイル | 起動方法 |
|----|----------------------|----------|
| Windows | `ImgConverterDesktop-x.x.x-windows.zip` を解凍 | `imgconverterdesktop.exe` を実行 |
| macOS | `ImgConverterDesktop-x.x.x-macos.zip` を解凍 | `ImgConverterDesktop.app` を起動 |
| Linux | `ImgConverterDesktop-x.x.x-linux.zip` を解凍 | `imgconverterdesktop` を実行 |

## 使い方

1. 変換形式をプルダウンメニューから選択
2. 「Open File」ボタンを押して、変換したい画像ファイルを選択（複数選択可）
3. 画像選択後、自動的に変換が開始され、サムネイルプレビューに変換前・変換後の画像が表示されます
4. 「Open Output Folder」ボタンを押して、変換後の画像が保存されるフォルダにアクセス可能

## 不具合の報告

バグを発見した場合は [GitHub Issues](https://github.com/Yuulis/ImgConverterDesktop/issues) よりご報告ください。
報告の際は以下の情報を含めていただけると助かります。

- OS とバージョン（例: Windows 11, macOS 15.x, Ubuntu 24.04）
- アプリのバージョン
- 再現手順
- 期待する動作と実際の動作

## 開発者向け

### 前提条件

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/)

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/Yuulis/ImgConverterDesktop.git
cd ImgConverterDesktop

# 依存関係のインストール
uv sync --all-groups

# アプリの起動
uv run flet run src
```

### テスト

```bash
uv run python -m unittest discover -s tests -p "test_*.py" -v
```

### ビルド

```bash
# Windows
uv run flet build windows

# macOS
uv run flet build macos

# Linux
uv run flet build linux
```

## プロジェクトについて

このアプリは [Flet](https://flet.dev/) ライブラリを使用して作成されました。

## ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) のもとで公開されています。
