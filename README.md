# C Table Arranger

A tool to extract and format C array information from source code.

## Features

- Parse C source code and extract array declarations
- Support for multi-dimensional arrays (1D, 2D, 3D+)
- Clean output format showing array dimensions and elements
- Command-line interface for easy usage
- Support for various C data types (int, float, char, etc.)

````markdown
# C Table Arranger — 使い方とツール説明

C ソースコードから配列宣言を抽出し、見やすく整形したテキスト出力を生成するツールです。

この README では以下を整理して解説します:
- インストール方法
- コマンドライン（CLI）での使い方
- ライブラリ API の使い方（Python）
- 事前処理（プリプロセス）についての注意点
- 開発手順と品質チェック
- トラブルシューティング

---

## インストール

パッケージマネージャー `uv` を使用する例:

```powershell
uv add c-table-arranger
```

注: 環境によっては `pip` 等でインストールするパターンも想定できますが、このプロジェクトでは `uv` を用いる手順が README に記載されています。

## コマンドライン（CLI）

基本的な使い方:

```powershell
c-table-arranger input.c
```

出力をファイルに保存する例:

```powershell
c-table-arranger input.c -o output.txt
```

主なオプション（例）:
- `-o, --output <file>` : 出力先ファイルを指定
- `-v, --verbose` : 詳細ログを有効にする
- `--format <style>` : 出力形式の指定（デフォルトはスペース区切り）

（注: 実際の CLI オプションは実装に依存します。必要なら `--help` 出力を README に追加できます。）

## ライブラリ（Python API）

Python スクリプト内で解析機能を使う例:

```python
from c_table_arranger.parser import CArrayParser
from c_table_arranger.formatter import ArrayFormatter

parser = CArrayParser()
arrays = parser.parse_file("example.c")

formatter = ArrayFormatter()
for array in arrays:
        print(formatter.format_array(array))
```

出力オブジェクトの構造（例）:
- `array.name` : 配列名
- `array.dimensions` : 次元リスト（例: [2, 3]）
- `array.elements` : 要素データ（多次元配列はネストされたリスト）

## プリプロセス（重要）

`pycparser` をベースに解析する場合、以下に注意してください:

- システムヘッダやマクロはプリプロセス (cpp -E など) しておくのが望ましい。
- `size_t` や `FILE`、typedef など未定義の識別子は fake headers（事前定義）で補完するか、簡略化しておく。
- 複雑なマクロやコンパイラ拡張（属性や組み込み関数）は削除または単純化する必要がある場合があります。

ツールに渡す前の前処理例:

```powershell
cpp -E input.c -I/path/to/fake_libc_include > input.i
c-table-arranger input.i
```

（Windows では `cpp` が無いことが多いため、WSL や MSYS2 のインストール、または Python ベースでプリプロセスを行うラッパーを用意することを推奨します。）

## 出力形式の例

入力:
```c
int matrix[2][3] = {{1, 2, 3}, {4, 5, 6}};
float values[4] = {1.5, 2.7, 3.14, 4.0};
```

デフォルト出力（例）:

```
Array: matrix
Dimensions: [2][3]
1 2 3
4 5 6

Array: values
Dimensions: [4]
1.5 2.7 3.14 4.0
```

## 開発・テスト

開発者向けの手順:

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

コードの品質ポリシーや CI の流れについては、プロジェクト内のガイドライン（`CLAUD.md` 等）を参照してください。

## トラブルシューティング

- 解析でエラーが出る場合:
    - まずプリプロセス（`cpp -E`）してみる
    - `fake_libc_include` 相当の簡易ヘッダを使って `size_t` 等を補完する
    - 初期化子が複雑な場合は簡略化してから解析を試す

- 出力が期待と異なる場合:
    - 配列の初期化方法（コンマ、ネストの深さ）を確認
    - 文字列リテラルやキャストによる副作用を確認

## 貢献ガイド

- 変更を加える前に Issue を立てて背景を説明してください。
- 新機能やバグ修正はテストを追加してプルリクを作成してください。
- コミットメッセージには変更の意図が分かる短い説明を入れてください。

## ライセンス

MIT ライセンス

---

必要であれば、README に次の追加を行います:
- 実際の CLI オプションのフルリファレンス（`--help` 出力）
- 具体的なインストール手順（pip など代替手段）
- Windows 固有のプリプロセス手順（PowerShell スクリプト）

ご希望の追加や修正を教えてください。
````