# C Table Arranger

C ソースコードから配列宣言を抽出し、見やすく整形したテキスト出力を生成するツールです。

以下の内容を整理して記載します:
- 概要
- 特徴
- インストール方法
- コマンドライン（CLI）での使い方
- ライブラリ（Python API）の使い方
- プリプロセス（前処理）に関する注意点
- 開発・テスト手順
- トラブルシューティング
- 貢献方法
- ライセンス

---

## 概要

C ソースコード内の配列（一次元・多次元）宣言を解析し、配列名・次元・要素を読み取り、可読性の高いテキスト形式で出力します。解析は Python ベースで行われ、コマンドラインツールとライブラリの両方として利用できます。

## 特徴

- C ソースコードから配列宣言を抽出
- 1D、2D、3D 以上の多次元配列をサポート
- 配列の次元・要素を分かりやすく表示
- コマンドラインインターフェイスを提供
- int, float, char 等の各種データ型に対応

## インストール

ローカルのパッケージマネージャー `uv` を使う例:

```powershell
uv add c-table-arranger
```

注: 環境によっては `pip` 等の別手段での配布を用いることも可能です。プロジェクトの配布方法に応じて README に手順を追加できます。

## コマンドライン（CLI）

基本的な実行例:

```powershell
c-table-arranger input.c
```

出力をファイルに保存する例:

```powershell
c-table-arranger input.c -o output.txt
```

よく使うオプション（例）:
- `-o, --output <file>` : 出力先ファイルを指定
- `-v, --verbose` : 詳細ログを有効化
- `--format <style>` : 出力スタイルを指定（デフォルトはスペース区切り）
- `--include-comments` : 初期化子内の C コメントを出力に含める（デフォルトでは除外）

注: 実際の CLI オプションは実装に依存します。正確なオプション一覧を README に載せたい場合は、`c-table-arranger --help` の出力を追加することを推奨します。

### Version

You can display the current program version from the CLI:

```powershell
c-table-arranger --version
```

The same version string also appears at the top of `c-table-arranger --help`.

## ライブラリ（Python API）

Python スクリプト内で解析機能を利用する例:

```python
from c_table_arranger.parser import CArrayParser
from c_table_arranger.formatter import ArrayFormatter

parser = CArrayParser()
arrays = parser.parse_file("example.c")

formatter = ArrayFormatter()
for array in arrays:
    print(formatter.format_array(array))
```

出力オブジェクト（例）:
- `array.name` : 配列名
- `array.dimensions` : 次元リスト（例: [2, 3]）
- `array.elements` : 要素（多次元はネストされたリスト）

## プリプロセス（重要）

この種の解析はソースに未定義の識別子やシステムヘッダ、複雑なマクロがあると失敗しやすいため、事前処理を行うことを推奨します。

- システムヘッダやマクロはプリプロセス（例: `cpp -E`）しておくと安定します。
- `size_t` や `FILE`、typedef など未定義の識別子は fake headers（事前定義）で補うか、簡略化しておくと良いです。
- コンパイラ拡張や複雑なマクロは削除または単純化しておく必要がある場合があります。

プリプロセス例:

```powershell
cpp -E input.c -I/path/to/fake_libc_include > input.i
c-table-arranger input.i
```

Windows 環境では `cpp` が標準で無い場合があるため、WSL/MINGW/MSYS2 を用いるか、Python でプリプロセスを行うラッパーを用意することを検討してください。

## 出力形式の例

入力:

```c
int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
float values[4] = {1.5, 2.7, 3.14, 4.0};
```

デフォルト出力（例）:

```text
Array: matrix
Dimensions: [2][3]
1 2 3
4 5 6

Array: values
Dimensions: [4]
1.5 2.7 3.14 4.0
```

## 開発・テスト

開発環境のセットアップ例（`uv` を使用）:

```powershell
# 開発依存関係をインストール
uv add --dev pytest pytest-asyncio anyio ruff pyright

# テストを実行
uv run --frozen pytest

# コード整形／チェック
uv run --frozen ruff format .
uv run --frozen ruff check .
uv run --frozen pyright
```

コード規約や CI の流れについてはプロジェクト内のガイド（`CLAUD.md` 等）を参照してください。

## スタンドアロン実行ファイルの作成

Windows 向けに単一の実行ファイル（`c-table-arranger.exe`）を作成する手順です。PyInstaller を利用します。

1. PyInstaller をインストールします。
   ```powershell
   uv add --dev pyinstaller
   # もしくは
   pip install pyinstaller
   ```
2. ルートディレクトリでビルドスクリプトを実行します。
   ```powershell
   python build_binary.py
   ```
   `dist/` フォルダに `c-table-arranger.exe` が生成されます。

PyInstaller のオプションを直接指定したい場合は、以下のコマンドでも同じ結果が得られます。

```powershell
pyinstaller --onefile --console --name c-table-arranger --distpath dist c_table_arranger/main.py
```

より細かな設定が必要な場合は、同梱の `c-table-arranger.spec` を編集し、`pyinstaller c-table-arranger.spec` を実行してください。

## トラブルシューティング

- 解析でエラーが出る場合:
  - まずプリプロセス（`cpp -E`）してみる
  - `fake_libc_include` 相当の簡易ヘッダで `size_t` 等を補完する
  - 初期化子が非常に複雑な場合は簡略化してから再試行する

- 出力が期待と異なる場合:
  - 配列の初期化方法（ネストやカンマの扱い）を確認する
  - 文字列リテラルやキャストによる副作用に注意する

## 貢献ガイド

- 変更を加える前に Issue を立てて背景を説明してください。
- 新機能やバグ修正にはテストを追加してプルリクエストを作成してください。
- コミットメッセージには意図が分かる短い説明を入れてください。

## ライセンス

MIT ライセンス

---

必要であれば以下の追加が可能です:
- 実際の CLI オプションのフルリファレンス（`--help` 出力を貼る）
- `pip` 等の代替インストール手順
- Windows 固有のプリプロセス手順（PowerShell スクリプト例）
